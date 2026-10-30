// HIL ESP32 DevKit V1 - modelo de moto (KTM Duke 390 aprox.) + roda fonica 22-2 via I2S/PCM5102
// PC -> ESP : "throttle,clutch,gear[,brake]\n"  (0-255, 0-255, 0-7 (7=re), 0-255)
//             "P,nome,valor\n"                   (parametros vindos do moto_duke390.json)
// ESP -> PC : "rpm,vss_hz,inj_us,ign_age_ms,gear,kmh*10,torque*10,map*10,fuelfactor*100,fb_ok\n" a cada 50 ms
#include <Arduino.h>
#include <driver/i2s.h>
#include <math.h>

// ---------- I2S (PCM5102) ----------
#define I2S_BCK_PIN 27
#define I2S_LCK_PIN 14
#define I2S_DIN_PIN 22

// ---------- Saidas p/ Speeduino ----------
#define DAC_TPS_PIN 25
#define DAC_MAP_PIN 26
#define CLUTCH_PIN 15
#define VSS_PIN 16

// ---------- Entradas da ECU (isoladas) ----------
#define FEEDBACK_INJ_PIN 4
#define FEEDBACK_IGN_PIN 5

const i2s_port_t I2S_PORT = I2S_NUM_0;
const int SAMPLE_RATE = 44100;
const int BUFFER_SIZE = 64;

const int TOTAL_TEETH = 22;
const int MISSING_TEETH = 2;
const int PRESENT_TEETH = TOTAL_TEETH - MISSING_TEETH;
const float DEGREES_PER_TOOTH = 360.0 / TOTAL_TEETH;
const float CRANK_AMPLITUDE = 0.6;

float crank_angle = 0.0;

// ---------- Parametros (defaults = moto_duke390.json; o PC sobrescreve) ----------
float idle_rpm = 1400, rev_limit_rpm = 10500, engine_inertia = 0.08, displacement_cc = 373;
float fric_const_nm = 2.0, fric_per_rpm = 0.0012, idle_gain = 0.03, idle_max_nm = 8.0;
float map_idle_kpa = 38, map_zero_torque_kpa = 25, baro_kpa = 101.3, iat_c = 30, ve = 0.85, afr = 14.7;
float inj_flow_ccmin = 230, inj_deadtime_ms = 0.8, fuel_density = 0.74, use_inj_feedback = 0;
float mass_kg = 230, wheel_radius_m = 0.30, wheel_inertia = 1.5, cda = 0.36, crr = 0.015, brake_max_n = 2200;
float primary_ratio = 2.9, final_ratio = 3.0, reverse_ratio = 2.714;
float clutch_tmax_nm = 70, clutch_start = 0.2, clutch_end = 0.7;
float vss_ppr = 16, map_sensor_min_kpa = 10, map_sensor_max_kpa = 260;
float gr[7] = {0, 2.714, 1.882, 1.409, 1.143, 0.960, 0.840};
float tq_n = 12;
float tqr[16] = {1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 10500, 11500};
float tqn[16] = {20, 24, 27, 29, 31, 33, 35, 35, 34, 31, 28, 15};

struct Param { const char *name; float *ptr; };
#define PR(x) {#x, &x}
Param params[] = {
  PR(idle_rpm), PR(rev_limit_rpm), PR(engine_inertia), PR(displacement_cc),
  PR(fric_const_nm), PR(fric_per_rpm), PR(idle_gain), PR(idle_max_nm),
  PR(map_idle_kpa), PR(map_zero_torque_kpa), PR(baro_kpa), PR(iat_c), PR(ve), PR(afr),
  PR(inj_flow_ccmin), PR(inj_deadtime_ms), PR(fuel_density), PR(use_inj_feedback),
  PR(mass_kg), PR(wheel_radius_m), PR(wheel_inertia), PR(cda), PR(crr), PR(brake_max_n),
  PR(primary_ratio), PR(final_ratio), PR(reverse_ratio),
  PR(clutch_tmax_nm), PR(clutch_start), PR(clutch_end),
  PR(vss_ppr), PR(map_sensor_min_kpa), PR(map_sensor_max_kpa), PR(tq_n),
  {"g1", &gr[1]}, {"g2", &gr[2]}, {"g3", &gr[3]}, {"g4", &gr[4]}, {"g5", &gr[5]}, {"g6", &gr[6]},
};
const int NPARAMS = sizeof(params) / sizeof(params[0]);

void setParam(const char *name, float v) {
  for (int i = 0; i < NPARAMS; i++)
    if (!strcmp(params[i].name, name)) { *params[i].ptr = v; return; }
  int idx;
  if (sscanf(name, "tqr%d", &idx) == 1 && idx >= 0 && idx < 16) tqr[idx] = v;
  else if (sscanf(name, "tqn%d", &idx) == 1 && idx >= 0 && idx < 16) tqn[idx] = v;
}

// ---------- Estado ----------
uint8_t throttle = 0, clutch = 0, gear = 0, brake = 0;
float omega_e = 1400 * TWO_PI / 60.0;  // rad/s
float vel = 0;                          // m/s (negativo = re)
float map_kpa = 38, torque_ind = 0, fuel_factor = 1.0;
bool fb_ok = false;
uint32_t vss_hz = 0;

volatile uint32_t tempo_injecao_us = 0;
volatile uint32_t inicio_pulso_inj = 0;
volatile uint32_t ultimo_inj_ms = 0;
volatile uint32_t momento_ignicao_us = 0;

void IRAM_ATTR isr_leitura_injetor() {
  if (digitalRead(FEEDBACK_INJ_PIN) == LOW) inicio_pulso_inj = micros();
  else { tempo_injecao_us = micros() - inicio_pulso_inj; ultimo_inj_ms = millis(); }
}
void IRAM_ATTR isr_leitura_ignicao() { momento_ignicao_us = micros(); }

void pwmSetup() {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcAttach(VSS_PIN, 1000, 8);
#else
  ledcSetup(2, 1000, 8); ledcAttachPin(VSS_PIN, 2);
#endif
}
void pwmVss(uint32_t hz) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcWriteTone(VSS_PIN, hz);
#else
  ledcWriteTone(2, hz);
#endif
}

void setupI2S() {
  i2s_config_t cfg = {};
  cfg.mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX);
  cfg.sample_rate = SAMPLE_RATE;
  cfg.bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT;
  cfg.channel_format = I2S_CHANNEL_FMT_ONLY_LEFT;
  cfg.communication_format = I2S_COMM_FORMAT_STAND_I2S;
  cfg.intr_alloc_flags = ESP_INTR_FLAG_LEVEL1;
  cfg.dma_buf_count = 8;
  cfg.dma_buf_len = BUFFER_SIZE;
  cfg.use_apll = false;
  cfg.tx_desc_auto_clear = true;
  cfg.fixed_mclk = 0;
  i2s_pin_config_t pins = {};
  pins.bck_io_num = I2S_BCK_PIN;
  pins.ws_io_num = I2S_LCK_PIN;
  pins.data_out_num = I2S_DIN_PIN;
  pins.data_in_num = I2S_PIN_NO_CHANGE;
  i2s_driver_install(I2S_PORT, &cfg, 0, NULL);
  i2s_set_pin(I2S_PORT, &pins);
}

// ---------- Serial ----------
char lineBuf[64];
uint8_t lineLen = 0;

void handleLine(char *s) {
  if (s[0] == 'P' && s[1] == ',') {
    char *name = s + 2;
    char *comma = strchr(name, ',');
    if (!comma) return;
    *comma = 0;
    setParam(name, atof(comma + 1));
    return;
  }
  int t, c, g, b = 0;
  int n = sscanf(s, "%d,%d,%d,%d", &t, &c, &g, &b);
  if (n < 3) return;
  throttle = constrain(t, 0, 255);
  clutch = constrain(c, 0, 255);
  gear = constrain(g, 0, 7);  // 0 = neutro, 7 = re
  brake = constrain(b, 0, 255);
  digitalWrite(CLUTCH_PIN, clutch > 127 ? HIGH : LOW);
  dacWrite(DAC_TPS_PIN, throttle);
}

void lerSerial() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n') {
      lineBuf[lineLen] = 0;
      handleLine(lineBuf);
      lineLen = 0;
    } else if (ch != '\r' && lineLen < sizeof(lineBuf) - 1) {
      lineBuf[lineLen++] = ch;
    }
  }
}

// ---------- Modelo da moto ----------
float tqWot(float rpm) {
  int n = constrain((int)tq_n, 2, 16);
  if (rpm <= tqr[0]) return tqn[0];
  for (int i = 1; i < n; i++)
    if (rpm <= tqr[i]) return tqn[i - 1] + (tqn[i] - tqn[i - 1]) * (rpm - tqr[i - 1]) / (tqr[i] - tqr[i - 1]);
  return tqn[n - 1];
}

// Fator de combustivel a partir do pulso real do bico (1.0 = estequiometrico)
void atualizaCombustivel() {
  bool recente = (millis() - ultimo_inj_ms) < 300;
  uint32_t pw = tempo_injecao_us;
  fb_ok = recente && pw > 0 && pw < 50000;
  if (!fb_ok) { fuel_factor = (use_inj_feedback > 0.5f) ? 0.0f : 1.0f; return; }
  float rho = 1.184f * (map_kpa / 101.3f) * (298.0f / (273.0f + iat_c));  // kg/m3
  float ar_g = rho * displacement_cc * 1e-3f * ve;                         // g/ciclo
  float comb_g = ar_g / afr;
  float vazao_g_ms = inj_flow_ccmin / 60.0f * fuel_density / 1000.0f;      // g/ms
  float pw_ideal = comb_g / vazao_g_ms;
  float pw_real = pw / 1000.0f - inj_deadtime_ms;
  fuel_factor = (pw_ideal > 0.05f) ? constrain(pw_real / pw_ideal, 0.0f, 2.0f) : 1.0f;
}

void passoFisica(float dt) {
  float thr = throttle / 255.0f;
  float rpm = omega_e * 60.0f / TWO_PI;

  // MAP (borboleta) e carga
  float map_max = baro_kpa * 0.98f;
  map_kpa = map_idle_kpa + (map_max - map_idle_kpa) * powf(thr, 1.3f);
  float carga = constrain((map_kpa - map_zero_torque_kpa) / (map_max - map_zero_torque_kpa), 0.0f, 1.0f);

  // Eficiencia pela mistura (so tem efeito com feedback do bico)
  float eff = 1.0f;
  if (use_inj_feedback > 0.5f) {
    float ff = fuel_factor;
    eff = ff < 1.0f ? ff : (ff < 1.15f ? 1.0f : fmaxf(0.6f, 1.0f - (ff - 1.15f) * 0.8f));
  }
  float t_ind = tqWot(rpm) * carga * eff;
  if (rpm > rev_limit_rpm) t_ind = 0;
  torque_ind = t_ind;

  float t_fric = fric_const_nm + fric_per_rpm * rpm;
  float t_idle = 0;
  if (rpm < idle_rpm) t_idle = fminf(idle_max_nm, (idle_rpm - rpm) * idle_gain);

  // Embreagem
  float pedal = clutch / 255.0f;
  float eng = constrain((clutch_end - pedal) / (clutch_end - clutch_start), 0.0f, 1.0f);
  float ratio = 0;
  if (gear >= 1 && gear <= 6) ratio = gr[gear] * primary_ratio * final_ratio;
  else if (gear == 7) ratio = -reverse_ratio * primary_ratio * final_ratio;
  float t_c = 0;
  if (ratio != 0) {
    float w_in = vel / wheel_radius_m * ratio;
    float x = (omega_e - w_in) / 10.0f;
    t_c = clutch_tmax_nm * eng * x / (1.0f + fabsf(x));
  }

  // Motor
  omega_e += (t_ind + t_idle - t_fric - t_c) / engine_inertia * dt;
  if (omega_e < 0) omega_e = 0;

  // Veiculo
  float f_tracao = (ratio != 0) ? t_c * ratio / wheel_radius_m : 0;
  float f_drag = 0.5f * 1.2f * cda * vel * fabsf(vel);
  float f_roll = crr * mass_kg * 9.81f * (vel / (fabsf(vel) + 0.3f));
  float f_brake = (brake / 255.0f) * brake_max_n * (vel / (fabsf(vel) + 0.2f));
  float m_eff = mass_kg + wheel_inertia / (wheel_radius_m * wheel_radius_m);
  float v_new = vel + (f_tracao - f_drag - f_roll - f_brake) / m_eff * dt;
  if (vel * v_new < 0 && fabsf(f_tracao) < 50) v_new = 0;  // resistencias nao invertem o sentido
  vel = v_new;
}

void atualizaFisica(uint32_t elapsed_us) {
  int passos = constrain((int)(elapsed_us / 500), 1, 20);
  for (int i = 0; i < passos; i++) passoFisica(0.0005f);

  float v = (map_kpa - map_sensor_min_kpa) / (map_sensor_max_kpa - map_sensor_min_kpa) * 5.0f;
  dacWrite(DAC_MAP_PIN, (uint8_t)constrain(v / 3.3f * 255.0f, 0.0f, 255.0f));

  float circ = TWO_PI * wheel_radius_m;
  vss_hz = (uint32_t)(fabsf(vel) / circ * vss_ppr);
  pwmVss(vss_hz);
}

void enviaTelemetria() {
  uint32_t age = (micros() - momento_ignicao_us) / 1000;
  Serial.printf("%d,%u,%u,%u,%u,%d,%d,%d,%d,%d\n", (int)(omega_e * 60.0f / TWO_PI), vss_hz,
                tempo_injecao_us, age, gear, (int)(vel * 36.0f), (int)(torque_ind * 10),
                (int)(map_kpa * 10), (int)(fuel_factor * 100), fb_ok ? 1 : 0);
}

void setup() {
  Serial.begin(115200);
  pinMode(CLUTCH_PIN, OUTPUT);
  pwmSetup();
  dacWrite(DAC_TPS_PIN, 0);
  pinMode(FEEDBACK_INJ_PIN, INPUT_PULLUP);
  pinMode(FEEDBACK_IGN_PIN, INPUT_PULLDOWN);
  attachInterrupt(digitalPinToInterrupt(FEEDBACK_INJ_PIN), isr_leitura_injetor, CHANGE);
  attachInterrupt(digitalPinToInterrupt(FEEDBACK_IGN_PIN), isr_leitura_ignicao, RISING);
  setupI2S();
}

void loop() {
  static uint32_t tFis = 0, tTx = 0, tComb = 0;
  lerSerial();

  uint32_t nowUs = micros();
  if (nowUs - tFis >= 5000) {
    atualizaFisica(nowUs - tFis);
    tFis = nowUs;
  }
  uint32_t now = millis();
  if (now - tComb >= 20) { atualizaCombustivel(); tComb = now; }
  if (now - tTx >= 50) { enviaTelemetria(); tTx = now; }

  // ---- Roda fonica 22-2 (codigo base) ----
  float rpm = omega_e * 60.0f / TWO_PI;
  float angle_increment = (360.0 * (rpm / 60.0)) / (float)SAMPLE_RATE;
  int16_t sample_buffer[BUFFER_SIZE];
  size_t bytes_written;
  for (int i = 0; i < BUFFER_SIZE; i++) {
    crank_angle += angle_increment;
    if (crank_angle >= 360.0) crank_angle -= 360.0;
    int tooth = (int)(crank_angle / DEGREES_PER_TOOTH);
    if (tooth >= PRESENT_TEETH) {
      sample_buffer[i] = 0;
    } else {
      float tooth_angle = crank_angle - (tooth * DEGREES_PER_TOOTH);
      float phase = (tooth_angle / DEGREES_PER_TOOTH) * TWO_PI;
      sample_buffer[i] = (int16_t)(sin(phase) * CRANK_AMPLITUDE * 32767.0);
    }
  }
  i2s_write(I2S_PORT, sample_buffer, sizeof(sample_buffer), &bytes_written, portMAX_DELAY);
}

// HIL ESP32 DevKit V1 - baseado no CodigoEsp.ino (roda fonica 22-2 via I2S/PCM5102)
// PC -> ESP : "throttle,clutch,gear\n"   (0-255, 0-255, 0-6)
// ESP -> PC : "rpm,vss_hz,inj_us,ign_age_ms,gear\n" a cada 50 ms
#include <Arduino.h>
#include <driver/i2s.h>
#include <math.h>

// ---------- I2S (PCM5102) - pinos movidos p/ liberar os DACs 25/26 ----------
#define I2S_BCK_PIN 27   // BCK
#define I2S_LCK_PIN 14   // LCK
#define I2S_DIN_PIN 22   // DIN

// ---------- Saidas p/ Speeduino ----------
// DACs internos de 8 bit (precisam de filtro RC: resistor + capacitor p/ GND)
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
const float CRANK_AMPLITUDE = 0.6;  // fixo (antes era o slider)

float crank_angle = 0.0;

// ---------- Estado HIL ----------
const float IDLE_RPM = 1000, MAX_RPM = 10500;
float rpm = IDLE_RPM;
uint8_t throttle = 0, clutch = 0, gear = 0;
float gear_ratios[7] = {0.0, 2.66, 1.88, 1.45, 1.20, 1.03, 0.90};
uint32_t vss_hz = 0;

volatile uint32_t tempo_injecao_us = 0;
volatile uint32_t inicio_pulso_inj = 0;
volatile uint32_t momento_ignicao_us = 0;

void IRAM_ATTR isr_leitura_injetor() {
  if (digitalRead(FEEDBACK_INJ_PIN) == LOW) inicio_pulso_inj = micros();
  else tempo_injecao_us = micros() - inicio_pulso_inj;
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

// ---------- Serial (parser nao bloqueante) ----------
char lineBuf[48];
uint8_t lineLen = 0;

void handleLine(char *s) {
  int t, c, g;
  if (sscanf(s, "%d,%d,%d", &t, &c, &g) != 3) return;
  throttle = constrain(t, 0, 255);
  clutch = constrain(c, 0, 255);
  gear = constrain(g, 0, 6);  // 0 = neutro
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

// ---------- Modelo simples do motor (~ a cada 5 ms) ----------
void atualizaFisica(float dt) {
  float alvo = IDLE_RPM + (MAX_RPM - IDLE_RPM) * (throttle / 255.0f);
  // Embreagem/neutro: gira livre (rapido). Engatado: inercia do carro (lento).
  float tau = (clutch > 127 || gear == 0) ? 0.25f : 0.8f;
  rpm += (alvo - rpm) * (dt / tau);
  rpm = constrain(rpm, 200.0f, MAX_RPM);

  uint8_t mapDuty = map(throttle, 0, 255, 75, 250);  // mesma curva do PDF
  dacWrite(DAC_MAP_PIN, mapDuty);

  if (gear > 0 && clutch < 127) vss_hz = (uint32_t)((rpm / gear_ratios[gear]) / 60.0f);
  else vss_hz = 0;
  pwmVss(vss_hz);
}

void enviaTelemetria() {
  uint32_t age = (micros() - momento_ignicao_us) / 1000;
  Serial.printf("%d,%u,%u,%u,%u\n", (int)rpm, vss_hz, tempo_injecao_us, age, gear);
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
  static uint32_t tFis = 0, tTx = 0;
  lerSerial();

  uint32_t now = millis();
  if (now - tFis >= 5) {
    atualizaFisica((now - tFis) / 1000.0f);
    tFis = now;
  }
  if (now - tTx >= 50) {
    enviaTelemetria();
    tTx = now;
  }

  // ---- Roda fonica 22-2 (codigo base) ----
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



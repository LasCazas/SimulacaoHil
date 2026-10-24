#include <driver/i2s.h>
#include <math.h>

// Pinos mapeados para a serigrafia da placa PCM5102 Roxa
#define I2S_BCK_PIN 26   // Ligar no pino BCK
#define I2S_LCK_PIN 25   // Ligar no pino LCK
#define I2S_DIN_PIN 22   // Ligar no pino DIN

#define SLIDER_RPM_PIN 36
#define SLIDER_AMP_PIN 39

const i2s_port_t I2S_PORT = I2S_NUM_0;
const int SAMPLE_RATE = 44100;
const int BUFFER_SIZE = 64;

const int TOTAL_TEETH = 22; // Padrão Duke 390
const int MISSING_TEETH = 2;
const int PRESENT_TEETH = TOTAL_TEETH - MISSING_TEETH;
const float DEGREES_PER_TOOTH = 360.0 / TOTAL_TEETH;

float crank_angle = 0.0;

void setupI2S() {
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = BUFFER_SIZE,
    .use_apll = false,
    .tx_desc_auto_clear = true,
    .fixed_mclk = 0
  };

  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_BCK_PIN,
    .ws_io_num = I2S_LCK_PIN,
    .data_out_num = I2S_DIN_PIN,
    .data_in_num = I2S_PIN_NO_CHANGE
  };

  i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_PORT, &pin_config);
}

void setup() {
  Serial.begin(115200);
  pinMode(SLIDER_RPM_PIN, INPUT);
  pinMode(SLIDER_AMP_PIN, INPUT);
  setupI2S();
  Serial.println("Gerador 22-2 I2S Iniciado.");
}

void loop() {
  int rawRPM = analogRead(SLIDER_RPM_PIN);
  int rawAmp = analogRead(SLIDER_AMP_PIN);
  
  float targetRPM = map(rawRPM, 0, 4095, 200, 11500);
  static unsigned long ultimoPrint = 0;
  if (millis() - ultimoPrint > 500) {
    Serial.print("RPM Teorico (ESP32): ");
    Serial.println(targetRPM);
    ultimoPrint = millis();
  }
  float amplitude = map(rawAmp, 0, 4095, 5, 100) / 100.0;
  
  float crank_hz = targetRPM / 60.0;
  float angle_increment = (360.0 * crank_hz) / (float)SAMPLE_RATE;

  int16_t sample_buffer[BUFFER_SIZE];
  size_t bytes_written;

  for (int i = 0; i < BUFFER_SIZE; i++) {
    crank_angle += angle_increment;
    if (crank_angle >= 360.0) crank_angle -= 360.0;

    int current_tooth = (int)(crank_angle / DEGREES_PER_TOOTH);

    if (current_tooth >= PRESENT_TEETH) {
      sample_buffer[i] = 0; // Região da falha
    } else {
      float tooth_angle = crank_angle - (current_tooth * DEGREES_PER_TOOTH);
      float phase = (tooth_angle / DEGREES_PER_TOOTH) * TWO_PI;
      sample_buffer[i] = (int16_t)(sin(phase) * amplitude * 32767.0);
    }
  }

  i2s_write(I2S_PORT, &sample_buffer, sizeof(sample_buffer), &bytes_written, portMAX_DELAY);
}
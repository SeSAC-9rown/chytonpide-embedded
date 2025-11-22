#include "driver/i2s.h"

// --- 마이크 설정 (I2S Bus 1) ---
#define I2S_MIC_PORT      (I2S_NUM_1)
#define I2S_MIC_BCK       (18)
#define I2S_MIC_WS        (16)
#define I2S_MIC_DATA_IN   (17)

// --- 스피커 설정 (I2S Bus 0) ---
#define I2S_SPK_PORT      (I2S_NUM_0)
#define I2S_SPK_BCK       (8)
#define I2S_SPK_WS        (20)
#define I2S_SPK_DATA_OUT  (19)

// --- 오디오 설정 ---
#define SAMPLE_RATE       (16000)
#define BUFFER_SIZE       (512)
#define VOICE_THRESHOLD   (500)   // 음성 감지 임계값 (조정 가능)
#define SILENCE_TIMEOUT   (30)    // 침묵 감지 (30번 연속 = 약 2초)

int16_t audioBuffer[BUFFER_SIZE];
int16_t recordBuffer[SAMPLE_RATE * 5]; // 최대 5초 녹음
int recordIndex = 0;
int silenceCount = 0;
bool isRecording = false;

void setup() {
  delay(1000);
  
  // ========== 마이크 초기화 ==========
  i2s_config_t i2s_config_mic = {
      .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
      .sample_rate = SAMPLE_RATE,
      .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
      .channel_format = I2S_CHANNEL_FMT_ONLY_RIGHT,
      .communication_format = I2S_COMM_FORMAT_STAND_I2S,
      .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
      .dma_buf_count = 4,
      .dma_buf_len = BUFFER_SIZE,
      .use_apll = false,
      .tx_desc_auto_clear = false,
      .fixed_mclk = 0
  };
  
  i2s_driver_install(I2S_MIC_PORT, &i2s_config_mic, 0, NULL);
  
  i2s_pin_config_t pin_config_mic = {
      .bck_io_num = I2S_MIC_BCK,
      .ws_io_num = I2S_MIC_WS,
      .data_out_num = I2S_PIN_NO_CHANGE,
      .data_in_num = I2S_MIC_DATA_IN
  };
  
  i2s_set_pin(I2S_MIC_PORT, &pin_config_mic);
  i2s_zero_dma_buffer(I2S_MIC_PORT);
  
  // ========== 스피커 초기화 ==========
  i2s_config_t i2s_config_spk = {
      .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
      .sample_rate = SAMPLE_RATE,
      .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
      .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
      .communication_format = I2S_COMM_FORMAT_STAND_I2S,
      .intr_alloc_flags = 0,
      .dma_buf_count = 8,
      .dma_buf_len = 64,
      .use_apll = false,
      .tx_desc_auto_clear = true
  };
  
  i2s_driver_install(I2S_SPK_PORT, &i2s_config_spk, 0, NULL);
  
  i2s_pin_config_t pin_config_spk = {
      .bck_io_num = I2S_SPK_BCK,
      .ws_io_num = I2S_SPK_WS,
      .data_out_num = I2S_SPK_DATA_OUT,
      .data_in_num = I2S_PIN_NO_CHANGE
  };
  
  i2s_set_pin(I2S_SPK_PORT, &pin_config_spk);
  
  delay(500);
}

void loop() {
  size_t bytes_read = 0;
  
  // 마이크에서 읽기
  i2s_read(I2S_MIC_PORT, audioBuffer, sizeof(audioBuffer), &bytes_read, portMAX_DELAY);
  
  if (bytes_read > 0) {
    // 음성 레벨 계산
    int16_t max_level = 0;
    for (int i = 0; i < bytes_read / 2; i++) {
      if (abs(audioBuffer[i]) > max_level) {
        max_level = abs(audioBuffer[i]);
      }
    }
    
    // 음성 감지
    if (max_level > VOICE_THRESHOLD) {
      silenceCount = 0;
      
      if (!isRecording) {
        // 녹음 시작
        isRecording = true;
        recordIndex = 0;
      }
      
      // 버퍼에 저장
      int samples = bytes_read / 2;
      if (recordIndex + samples < SAMPLE_RATE * 5) {
        for (int i = 0; i < samples; i++) {
          recordBuffer[recordIndex++] = audioBuffer[i];
        }
      }
    } else {
      // 침묵 감지
      if (isRecording) {
        silenceCount++;
        
        // 일정 시간 침묵이 계속되면 재생
        if (silenceCount > SILENCE_TIMEOUT) {
          playRecording();
          isRecording = false;
          recordIndex = 0;
          silenceCount = 0;
        }
      }
    }
  }
}

void playRecording() {
  if (recordIndex == 0) return;
  
  // 녹음된 내용을 스피커로 재생
  size_t bytes_written = 0;
  i2s_write(I2S_SPK_PORT, recordBuffer, recordIndex * sizeof(int16_t), 
            &bytes_written, portMAX_DELAY);
  
  delay(100);
}

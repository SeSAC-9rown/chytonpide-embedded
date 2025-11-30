#include "ESP32Servo.h"

#define SERVO_PIN 7  // 서보 모터가 연결된 핀 번호

Servo myServo;  // 서보 객체 생성

void setup() {
  // 표준 50Hz 서보 모터 주파수 설정
  myServo.setPeriodHertz(50);
  
  // 서보 모터 연결 (SG90: 500~2500 마이크로초 펄스 폭)
  myServo.attach(SERVO_PIN, 500, 2500);
  
  // 초기 위치를 0도로 설정
  myServo.write(0);
  delay(1000);  // 서보가 초기 위치로 이동할 시간
}

void loop() {
  // 0도에서 180도로 이동
  for (int angle = 0; angle <= 180; angle += 1) {
    myServo.write(angle);
    delay(15);  // 각도 변경 간격 (부드러운 움직임)
  }
  delay(1000);  // 180도에서 잠시 대기
  
  // 180도에서 0도로 이동
  for (int angle = 180; angle >= 0; angle -= 1) {
    myServo.write(angle);
    delay(15);
  }
  delay(1000);  // 0도에서 잠시 대기
}

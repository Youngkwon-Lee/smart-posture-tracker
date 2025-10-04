# 🚀 Phase 1: Arduino 개발 단계별 계획

> MPU-6050 IMU 센서를 이용한 기본 자세 추적 시스템 개발

## 📅 4주 개발 계획

### 1주차: 환경 설정 및 기본 테스트
### 2주차: 센서 데이터 처리 및 필터링  
### 3주차: 자세 분류 알고리즘 개발
### 4주차: 통합 테스트 및 최적화

---

## 🔧 1주차: 환경 설정 및 기본 테스트

### Day 1-2: 개발 환경 구축
**목표**: Arduino 개발 환경 완전히 설정하기

#### ✅ Arduino IDE 설정
- [ ] Arduino IDE 최신 버전 다운로드 및 설치
- [ ] 보드 매니저에서 Arduino AVR Boards 설치 확인
- [ ] USB 드라이버 설치 (Windows의 경우)
- [ ] 포트 연결 확인 (Tools → Port)

#### ✅ 기본 동작 테스트
```cpp
// 1단계: LED 점멸 테스트
void setup() {
  pinMode(13, OUTPUT);
}

void loop() {
  digitalWrite(13, HIGH);
  delay(1000);
  digitalWrite(13, LOW);
  delay(1000);
}
```
- [ ] 내장 LED 점멸 테스트 성공
- [ ] 시리얼 통신 테스트 (9600 baud)
- [ ] 외부 LED 연결 테스트

### Day 3-4: MPU-6050 라이브러리 설치 및 연결

#### ✅ 라이브러리 설치
- [ ] `MPU6050` by Electronic Cats 설치
- [ ] `I2Cdev` by Jeff Rowberg 설치  
- [ ] `Wire` 라이브러리 (기본 내장) 확인

#### ✅ 하드웨어 연결
```
MPU-6050    Arduino Uno
VCC      →  3.3V (또는 5V)
GND      →  GND
SDA      →  A4 (SDA)
SCL      →  A5 (SCL)
```

#### ✅ I2C 스캔 테스트
```cpp
// I2C 장치 스캔 코드 실행
// 주소 0x68 (104) 확인 필요
```
- [ ] I2C 주소 0x68 감지 성공
- [ ] 센서 연결 상태 확인

### Day 5-7: 기본 센서 데이터 읽기

#### ✅ 원시 데이터 읽기
```cpp
// 가속도계 및 자이로스코프 원시 값 읽기
#include "I2Cdev.h"
#include "MPU6050.h"
#include "Wire.h"

MPU6050 mpu;
int16_t ax, ay, az;
int16_t gx, gy, gz;

void setup() {
    Wire.begin();
    Serial.begin(9600);
    mpu.initialize();
    Serial.println(mpu.testConnection() ? "연결 성공" : "연결 실패");
}

void loop() {
    mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
    
    Serial.print("가속도: ");
    Serial.print(ax); Serial.print("\t");
    Serial.print(ay); Serial.print("\t");
    Serial.print(az); Serial.print("\t");
    
    Serial.print("자이로: ");
    Serial.print(gx); Serial.print("\t");
    Serial.print(gy); Serial.print("\t");
    Serial.println(gz);
    
    delay(100);
}
```

#### ✅ 1주차 목표 달성 체크
- [ ] Arduino 개발 환경 완벽 작동
- [ ] MPU-6050 센서 정상 연결 및 데이터 읽기
- [ ] 시리얼 모니터로 실시간 데이터 확인
- [ ] 센서 방향별 데이터 변화 관찰

---

## 🔧 2주차: 센서 데이터 처리 및 필터링

### Day 8-10: 데이터 변환 및 단위 변환

#### ✅ 물리적 단위로 변환
```cpp
// 원시 값을 g(중력가속도)와 °/s로 변환
float accelScale = 16384.0;  // ±2g 범위
float gyroScale = 131.0;     // ±250°/s 범위

float accel_x = ax / accelScale;  // g 단위
float accel_y = ay / accelScale;
float accel_z = az / accelScale;

float gyro_x = gx / gyroScale;    // °/s 단위
float gyro_y = gy / gyroScale;
float gyro_z = gz / gyroScale;
```

#### ✅ 각도 계산 (가속도계 기반)
```cpp
// 피치(Pitch)와 롤(Roll) 각도 계산
float pitch = atan2(-accel_x, sqrt(accel_y*accel_y + accel_z*accel_z)) * 180/PI;
float roll = atan2(accel_y, accel_z) * 180/PI;
```

- [ ] g 단위 가속도 값 출력 확인
- [ ] °/s 단위 각속도 값 출력 확인
- [ ] 피치/롤 각도 계산 결과 확인

### Day 11-12: 센서 캘리브레이션

#### ✅ 오프셋 캘리브레이션
```cpp
// 센서를 평평한 곳에 1분간 놓고 오프셋 측정
void calibrateSensor() {
    long ax_offset = 0, ay_offset = 0, az_offset = 0;
    long gx_offset = 0, gy_offset = 0, gz_offset = 0;
    
    for(int i = 0; i < 1000; i++) {
        mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
        ax_offset += ax;
        ay_offset += ay;
        az_offset += (az - 16384); // 중력 보정
        gx_offset += gx;
        gy_offset += gy;
        gz_offset += gz;
        delay(3);
    }
    
    ax_offset /= 1000;
    ay_offset /= 1000;
    // ... 오프셋 값 저장
}
```

- [ ] 정적 상태에서 오프셋 값 계산
- [ ] 오프셋 적용 후 데이터 안정성 확인
- [ ] EEPROM에 캘리브레이션 값 저장 (선택)

### Day 13-14: 노이즈 필터링

#### ✅ 이동평균 필터
```cpp
#define WINDOW_SIZE 10

float accel_x_buffer[WINDOW_SIZE];
int buffer_index = 0;

float movingAverage(float new_value, float* buffer) {
    buffer[buffer_index] = new_value;
    buffer_index = (buffer_index + 1) % WINDOW_SIZE;
    
    float sum = 0;
    for(int i = 0; i < WINDOW_SIZE; i++) {
        sum += buffer[i];
    }
    return sum / WINDOW_SIZE;
}
```

#### ✅ 로우패스 필터
```cpp
// 간단한 1차 로우패스 필터
float alpha = 0.1;  // 필터 강도 (0~1)
float filtered_ax = alpha * ax + (1-alpha) * prev_ax;
```

- [ ] 이동평균 필터 적용 테스트
- [ ] 로우패스 필터 적용 테스트  
- [ ] 필터링 전후 데이터 비교

---

## 🔧 3주차: 자세 분류 알고리즘 개발

### Day 15-17: 기본 자세 정의 및 임계값 설정

#### ✅ 자세 카테고리 정의
```cpp
enum PostureType {
    GOOD_POSTURE = 0,
    FORWARD_HEAD = 1,
    SLOUCHING = 2,
    LEANING_LEFT = 3,
    LEANING_RIGHT = 4,
    UNKNOWN = 5
};
```

#### ✅ 임계값 기반 분류
```cpp
PostureType classifyPosture(float pitch, float roll) {
    // 정상 자세 범위 정의
    if(abs(pitch) < 15 && abs(roll) < 15) {
        return GOOD_POSTURE;
    }
    else if(pitch > 30) {  // 앞으로 숙임
        return FORWARD_HEAD;
    }
    else if(pitch < -20) {  // 뒤로 젖힘  
        return SLOUCHING;
    }
    else if(roll > 20) {   // 좌측 기울임
        return LEANING_LEFT;
    }
    else if(roll < -20) {  // 우측 기울임
        return LEANING_RIGHT;
    }
    
    return UNKNOWN;
}
```

- [ ] 각 자세별 데이터 100개씩 수집
- [ ] 임계값 튜닝 및 검증
- [ ] 분류 정확도 측정

### Day 18-19: 피드백 시스템 구현

#### ✅ LED 피드백
```cpp
#define GREEN_LED 8
#define RED_LED 9
#define BUZZER 10

void provideFeedback(PostureType posture) {
    switch(posture) {
        case GOOD_POSTURE:
            digitalWrite(GREEN_LED, HIGH);
            digitalWrite(RED_LED, LOW);
            noTone(BUZZER);
            break;
            
        case FORWARD_HEAD:
        case SLOUCHING:
        case LEANING_LEFT:
        case LEANING_RIGHT:
            digitalWrite(GREEN_LED, LOW);
            digitalWrite(RED_LED, HIGH);
            tone(BUZZER, 1000, 200);  // 짧은 경고음
            break;
            
        default:
            // 모든 LED 끄기
            digitalWrite(GREEN_LED, LOW);
            digitalWrite(RED_LED, LOW);
            noTone(BUZZER);
    }
}
```

#### ✅ 스마트 알림 시스템
```cpp
// 나쁜 자세 지속 시간 추적
unsigned long bad_posture_start = 0;
bool is_bad_posture = false;
const unsigned long WARNING_DELAY = 30000; // 30초

void smartAlert(PostureType posture) {
    if(posture != GOOD_POSTURE) {
        if(!is_bad_posture) {
            bad_posture_start = millis();
            is_bad_posture = true;
        }
        else if(millis() - bad_posture_start > WARNING_DELAY) {
            // 30초 이상 나쁜 자세 → 강한 알림
            tone(BUZZER, 1500, 1000);
        }
    }
    else {
        is_bad_posture = false;
    }
}
```

- [ ] LED 상태 표시 테스트
- [ ] 부저 알림 기능 테스트
- [ ] 시간 기반 스마트 알림 테스트

### Day 20-21: 데이터 로깅 및 통계

#### ✅ 자세 통계 계산
```cpp
unsigned long good_posture_time = 0;
unsigned long total_time = 0;
int posture_changes = 0;
PostureType prev_posture = UNKNOWN;

void updateStatistics(PostureType current_posture) {
    total_time++;
    
    if(current_posture == GOOD_POSTURE) {
        good_posture_time++;
    }
    
    if(current_posture != prev_posture) {
        posture_changes++;
        prev_posture = current_posture;
    }
}

void printStatistics() {
    float good_posture_percentage = (good_posture_time * 100.0) / total_time;
    Serial.print("좋은 자세 비율: ");
    Serial.print(good_posture_percentage);
    Serial.println("%");
}
```

- [ ] 실시간 통계 계산 구현
- [ ] 시간별 자세 로그 저장
- [ ] 일일 리포트 기능 추가

---

## 🔧 4주차: 통합 테스트 및 최적화

### Day 22-24: 전체 시스템 통합

#### ✅ 메인 루프 최적화
```cpp
// 완전한 시스템 통합 코드
void loop() {
    // 1. 센서 데이터 읽기
    mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
    
    // 2. 데이터 전처리
    float accel_x = (ax - ax_offset) / accelScale;
    float accel_y = (ay - ay_offset) / accelScale;
    float accel_z = (az - az_offset) / accelScale;
    
    // 3. 각도 계산
    float pitch = atan2(-accel_x, sqrt(accel_y*accel_y + accel_z*accel_z)) * 180/PI;
    float roll = atan2(accel_y, accel_z) * 180/PI;
    
    // 4. 자세 분류
    PostureType posture = classifyPosture(pitch, roll);
    
    // 5. 피드백 제공
    provideFeedback(posture);
    smartAlert(posture);
    
    // 6. 통계 업데이트
    updateStatistics(posture);
    
    // 7. 데이터 출력 (1초마다)
    static unsigned long last_print = 0;
    if(millis() - last_print > 1000) {
        Serial.print("Pitch: "); Serial.print(pitch);
        Serial.print(" Roll: "); Serial.print(roll);
        Serial.print(" Posture: "); Serial.println(posture);
        last_print = millis();
    }
    
    delay(50);  // 20Hz 업데이트
}
```

### Day 25-26: 성능 테스트

#### ✅ 정확도 테스트
- [ ] 각 자세별 50회 테스트 수행
- [ ] 분류 정확도 90% 이상 달성
- [ ] 오분류 케이스 분석 및 개선

#### ✅ 안정성 테스트  
- [ ] 6시간 연속 동작 테스트
- [ ] 다양한 환경 조건에서 테스트
- [ ] 전력 소모 측정

### Day 27-28: 최종 최적화 및 문서화

#### ✅ 코드 최적화
- [ ] 메모리 사용량 최소화
- [ ] 처리 속도 향상
- [ ] 주석 및 문서 추가

#### ✅ 최종 검증
- [ ] 전체 기능 테스트 체크리스트 완료
- [ ] 사용자 시나리오 테스트
- [ ] Phase 2 준비 사항 정리

---

## 📊 Phase 1 완료 기준

### ✅ 기능 요구사항
- [ ] 실시간 자세 모니터링 (20Hz 이상)
- [ ] 5가지 자세 분류 (정확도 90% 이상)
- [ ] 즉각적 피드백 (LED + 부저)
- [ ] 기본 통계 기능
- [ ] 6시간 이상 안정적 동작

### ✅ 성능 요구사항  
- [ ] 응답 시간 100ms 이내
- [ ] 분류 정확도 90% 이상
- [ ] 메모리 사용량 80% 이내
- [ ] 안정적 센서 통신

### ✅ 문서화
- [ ] 전체 소스코드 주석 완료
- [ ] 사용자 매뉴얼 작성
- [ ] 테스트 결과 리포트
- [ ] Phase 2 개발 계획

---

## 🐛 예상 문제점 및 해결책

### 센서 관련
| 문제 | 원인 | 해결책 |
|------|------|--------|
| 센서 인식 안됨 | I2C 연결 문제 | 연결 재확인, 풀업 저항 추가 |
| 데이터 노이즈 심함 | 전원 노이즈 | 필터링 강화, 전원 안정화 |
| 각도 계산 오류 | 캘리브레이션 부족 | 재캘리브레이션, 오프셋 조정 |

### 소프트웨어 관련
| 문제 | 원인 | 해결책 |
|------|------|--------|
| 처리 속도 느림 | 복잡한 계산 | 알고리즘 최적화, lookup table 사용 |
| 메모리 부족 | 큰 배열 사용 | 동적 할당, 버퍼 크기 조정 |
| 오분류 빈발 | 부적절한 임계값 | 데이터 재수집, 임계값 재조정 |

## 💡 추가 아이디어

### 개선 가능한 기능들
- [ ] 웹 대시보드로 실시간 모니터링
- [ ] SD카드에 데이터 로깅
- [ ] 개인별 맞춤 임계값 설정
- [ ] 운동 모드 (스트레칭 가이드)
- [ ] 스마트폰 앱 연동

**🎯 Phase 1 목표: 확실히 동작하는 기본 시스템을 만들어 Phase 2의 기반 마련하기!**
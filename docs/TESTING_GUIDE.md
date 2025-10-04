# 🧪 Testing Guide

Smart Posture Tracker 테스트 및 검증 가이드입니다.

## 🎯 Testing Overview

이 가이드는 다음 단계별 테스트를 다룹니다:
1. **Hardware Verification** - 하드웨어 연결 및 센서 동작 확인
2. **Data Collection** - Python 스크립트로 데이터 수집 테스트
3. **Posture Analysis** - 기본 자세 분석 알고리즘 검증
4. **Real-time Performance** - 실시간 모니터링 성능 테스트

## 📋 Prerequisites

### Software Requirements
```bash
# Python 환경 설정
pip install -r software/data-analysis/requirements.txt

# Arduino IDE 설정
- ESP32 board package 설치
- Adafruit MPU6050 라이브러리 설치
```

### Hardware Requirements
- ✅ ESP32 + MPU6050 하드웨어 조립 완료
- ✅ USB 케이블로 PC 연결
- ✅ Serial port 확인 (Device Manager에서 COM port 번호)

## 🔧 Test 1: Hardware Verification

### 목표
ESP32와 MPU6050 센서의 기본 통신 및 데이터 읽기 확인

### 실행 방법
```bash
# 1. Arduino 코드 업로드
# hardware/arduino/mpu6050_basic_test/mpu6050_basic_test.ino 열기
# ESP32 보드 선택 후 업로드

# 2. Serial Monitor 확인 (115200 baud)
```

### 성공 기준
```
✅ Expected Output:
Smart Posture Tracker - MPU6050 Test
=====================================
MPU6050 Found!
Accelerometer range set to: +-8G
Gyro range set to: +- 500 deg/s
Filter bandwidth set to: 21 Hz

CSV Header: timestamp,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,temp
1000,0.123,0.456,9.789,0.001,0.002,0.003,25.67
1100,0.124,0.457,9.788,0.000,0.001,0.002,25.68
...
```

### 검증 포인트
- [ ] MPU6050 센서 인식됨
- [ ] 가속도계 데이터 수신 중 (~9.8 m/s²가 한 축에서 나타남)
- [ ] 자이로스코프 데이터 수신 중 (정지 시 ~0 rad/s)
- [ ] 온도 데이터 정상 (실온 근처)
- [ ] 10Hz 샘플링 레이트 유지## 📊 Test 2: Python Data Collection

### 목표
Python 스크립트가 시리얼 데이터를 정상적으로 수집하고 분석하는지 확인

### 실행 방법
```bash
# Terminal/Command Prompt에서 실행
cd C:\Users\82106\smart-posture-tracker\software\data-analysis
python sensor_data_collector.py
```

### 테스트 시나리오
```
1. COM port 입력: COM3 (또는 해당 포트)
2. 수집 시간 입력: 30 (30초간 테스트)
3. 센서를 다양한 자세로 움직이기:
   - 10초간 정상 자세 유지
   - 10초간 앞으로 기울이기 (forward head posture)
   - 10초간 좌우로 기울이기
```

### 성공 기준
```
✅ Expected Output:
Smart Posture Tracker - Data Collector
=====================================

Available COM ports:
  COM3: Silicon Labs CP210x USB to UART Bridge (COM3)

Enter COM port (default: COM3): COM3
Collection duration in seconds (Enter for indefinite): 30

Connected to COM3 at 115200 baud
Starting data collection...
Press Ctrl+C to stop collection
Collected 50 samples...
Collected 100 samples...
...
Data collection stopped by user
Data saved to: sensor_data_20241210_143022.csv
Total samples collected: 300

=== Posture Analysis Report ===
Analysis period: 2024-12-10 14:30:22 to 2024-12-10 14:30:52
Total samples: 300
Duration: 30.0 seconds

Accelerometer Statistics (m/s²):
  accel_x: mean=-0.123, std=1.456
  accel_y: mean=0.456, std=0.789
  accel_z: mean=9.789, std=0.234

=== Posture Alerts ===
⚠️  Forward head posture detected: 33.3% of time
✅ Good posture maintained!
```

### 검증 포인트
- [ ] 시리얼 포트 연결 성공
- [ ] CSV 파일 생성됨
- [ ] 300개 샘플 수집 (10Hz × 30초)
- [ ] 자세 분석 리포트 생성
- [ ] 전방 기울임 감지 작동
- [ ] 그래프 생성 옵션 작동

## 🎯 Test 3: Posture Detection Accuracy

### 목표
자세 분류 알고리즘의 정확도 검증

### 테스트 프로토콜
```
각 자세를 30초씩 유지하며 데이터 수집:

1. 정상 자세 (Good Posture)
   - 등을 곧게 펴고 앉기
   - 목을 중립 위치에 유지
   - 어깨를 뒤로 당기기

2. 전방 머리 자세 (Forward Head Posture)  
   - 목을 앞으로 내밀기 (거북목)
   - 15도 이상 앞으로 기울이기

3. 측면 기울임 (Side Lean)
   - 좌측 또는 우측으로 기울이기
   - 10도 이상 측면 기울임

4. 구부정한 자세 (Slouched Posture)
   - 등을 구부리고 앞으로 기울이기
   - 어깨를 앞으로 내밀기
```

### 수집 명령
```bash
# 각 자세별로 별도 데이터 수집
python sensor_data_collector.py
# 각각 30초씩, 4번 반복
```

### 성공 기준
```
✅ 정상 자세 (30초):
   - Forward head posture: < 10%
   - Side lean: < 10%
   - 결과: "Good posture maintained!"

✅ 전방 머리 자세 (30초):
   - Forward head posture: > 80%
   - 경고: "Forward head posture detected"

✅ 측면 기울임 (30초):
   - Side lean: > 80%
   - 경고: "Side lean detected"
```

## ⚡ Test 4: Real-time Performance

### 목표
실시간 데이터 처리 성능 및 지연시간 측정

### 실행 방법
```bash
# 장시간 데이터 수집 (5분)
python sensor_data_collector.py
# Duration: 300 seconds
```

### 성능 메트릭
- **샘플링 레이트**: 10Hz ± 0.5Hz
- **지연시간**: < 100ms (센서 → 분석)
- **메모리 사용량**: < 100MB (5분간)
- **CPU 사용률**: < 50%

### 검증 방법
```python
# 성능 분석 스크립트 (별도 실행)
import pandas as pd
import numpy as np

# CSV 파일 로드
df = pd.read_csv('sensor_data_YYYYMMDD_HHMMSS.csv')

# 샘플링 레이트 계산
df['time_diff'] = df['timestamp'].diff()
actual_rate = 1000 / df['time_diff'].mean()  # Hz
print(f"Actual sampling rate: {actual_rate:.2f} Hz")

# 지연시간 분석 (timestamp 간격의 표준편차)
jitter = df['time_diff'].std()
print(f"Timing jitter: {jitter:.2f} ms")
```

## 📈 Test 5: Data Visualization

### 목표
실시간 그래프 및 데이터 시각화 기능 검증

### 실행 방법
```bash
python sensor_data_collector.py
# 30초 데이터 수집 후
# "Show plots? (y/n): y" 선택
```

### 예상 결과
- **4개 서브플롯 생성**:
  1. 가속도계 데이터 (X, Y, Z축)
  2. 자이로스코프 데이터 (X, Y, Z축) 
  3. 온도 데이터
  4. 자세 각도 (Pitch, Roll) + 임계값 선

### 검증 포인트
- [ ] 모든 그래프가 정상 표시
- [ ] 데이터 범위가 합리적
- [ ] 임계값 선이 올바르게 표시
- [ ] PNG 파일로 저장됨

## ✅ 전체 테스트 체크리스트

### Phase 1: 기본 기능 (완료해야 할 항목)
- [ ] **Hardware Test**: ESP32 + MPU6050 연결 및 데이터 읽기
- [ ] **Serial Communication**: Python ↔ Arduino 통신
- [ ] **Data Collection**: CSV 파일 생성 및 저장
- [ ] **Basic Analysis**: 통계 분석 및 리포트 생성

### Phase 2: 자세 분석 (검증해야 할 항목)  
- [ ] **Good Posture Detection**: 정상 자세 올바르게 인식
- [ ] **Forward Head Detection**: 전방 머리 자세 감지
- [ ] **Side Lean Detection**: 측면 기울임 감지  
- [ ] **False Positive Rate**: 오탐지 < 10%

### Phase 3: 성능 최적화 (측정해야 할 항목)
- [ ] **Sampling Rate**: 10Hz ± 0.5Hz 유지
- [ ] **Real-time Processing**: 지연시간 < 100ms
- [ ] **Memory Usage**: 장시간 실행 시 메모리 누수 없음
- [ ] **Visualization**: 그래프 생성 및 저장

## 🐛 문제 해결 가이드

### 일반적인 오류
1. **"No module named 'serial'"**
   ```bash
   pip install pyserial
   ```

2. **"Could not open port 'COM3'"**
   - Arduino IDE Serial Monitor 종료
   - 다른 프로그램에서 COM port 사용 중인지 확인

3. **"No data collected"**
   - Arduino 코드가 업로드되었는지 확인
   - Serial Monitor에서 데이터 출력되는지 확인
   - Baud rate 115200 맞는지 확인

4. **그래프가 표시되지 않음**
   ```bash
   pip install matplotlib
   # 또는 백엔드 설정
   import matplotlib
   matplotlib.use('TkAgg')
   ```

## 📊 테스트 결과 기록

각 테스트 완료 후 결과를 기록하세요:

```
Test 1 - Hardware: ✅ PASS / ❌ FAIL
Test 2 - Data Collection: ✅ PASS / ❌ FAIL  
Test 3 - Posture Detection: ✅ PASS / ❌ FAIL
Test 4 - Performance: ✅ PASS / ❌ FAIL
Test 5 - Visualization: ✅ PASS / ❌ FAIL

Notes: 
- 
-
-
```

모든 테스트가 통과하면 **Phase 1 개발 완료**! 🎉
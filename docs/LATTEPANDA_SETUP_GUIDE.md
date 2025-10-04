# LattePanda 개발 환경 설정 가이드

## 하드웨어 구성
- **LattePanda Delta 432** (4GB RAM, 64GB eMMC)
- **Arduino UNO R3** (센서 인터페이스용)
- **IAHRS intellithings RB-SDA-v1** × 2개
- **충전기** (LattePanda 전원)

## LattePanda 초기 설정

### 1. 운영체제 설치 및 업데이트
```bash
# Windows 10/11이 사전 설치되어 있음
# Windows 업데이트 실행
```

### 2. Arduino IDE 설치
1. https://www.arduino.cc/en/software 에서 Arduino IDE 다운로드
2. 설치 후 보드 매니저에서 "Arduino AVR Boards" 설치
3. Tools > Board > Arduino UNO 선택

### 3. 필요한 드라이버 설치
```
- CH340/CH341 USB 드라이버 (UNO R3용)
- LattePanda 전용 드라이버 (자동 설치됨)
```

### 4. Python 환경 설정
```bash
# Python 3.x 설치 (Microsoft Store에서)
pip install pyserial pandas numpy matplotlib
```

## 센서 연결 가이드

### IAHRS 센서 → Arduino UNO 연결
```
센서 1:
- VCC → Arduino 5V
- GND → Arduino GND  
- TX → Arduino Pin 2 (RX)
- RX → Arduino Pin 3 (TX)

센서 2:
- VCC → Arduino 5V
- GND → Arduino GND
- TX → Arduino Pin 4 (RX)
- RX → Arduino Pin 5 (TX)
```

### Arduino UNO → LattePanda 연결
```
- USB 케이블로 Arduino UNO를 LattePanda USB 포트에 연결
- COM 포트 자동 인식 (보통 COM3 또는 COM4)
```

## 소프트웨어 개발

### 1. Arduino 코드 업로드
```cpp
// iahrs_dual_sensor_test.ino 파일 사용
// Tools > Port에서 올바른 COM 포트 선택
// Upload 버튼 클릭
```

### 2. Python 데이터 수집 스크립트
```python
import serial
import pandas as pd
import time

# 시리얼 포트 연결
arduino = serial.Serial('COM3', 115200)  # 포트 번호 확인 필요
data_list = []

try:
    while True:
        line = arduino.readline().decode('utf-8').strip()
        if line and not line.startswith('IAHRS'):
            data_list.append(line.split(','))
        time.sleep(0.1)
except KeyboardInterrupt:
    df = pd.DataFrame(data_list)
    df.to_csv('posture_data.csv', index=False)
```

## 개발 워크플로우

1. **센서 테스트**: Arduino Serial Monitor에서 데이터 확인
2. **데이터 수집**: Python 스크립트로 CSV 저장
3. **분석**: pandas/matplotlib로 자세 패턴 분석
4. **알고리즘 개선**: 실시간 피드백 시스템 구현
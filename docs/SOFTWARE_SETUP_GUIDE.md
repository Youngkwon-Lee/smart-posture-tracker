# 💻 Smart Posture Tracker 소프트웨어 개발 환경 가이드

> 프로젝트에 필요한 모든 소프트웨어와 설치 방법을 정리합니다.

## 🎯 필요한 소프트웨어 개요

### Phase별 소프트웨어 요구사항
- **Phase 1**: Arduino IDE, Python (데이터 분석)
- **Phase 2**: Flutter (모바일 앱), Firebase (선택)
- **Phase 3**: 머신러닝 라이브러리 (TensorFlow/PyTorch)
- **전체**: Git, VSCode, 시각화 도구

---

## 🔧 Phase 1: 기본 개발 도구

### 1. Arduino 개발환경

#### ✅ Arduino IDE (필수)
```
다운로드: https://www.arduino.cc/en/software
버전: 2.3.0 이상 권장
용도: Arduino 코드 작성 및 업로드
```

**설치 후 추가 작업:**
- [ ] MPU6050 라이브러리 설치 (`라이브러리 매니저`)
- [ ] I2Cdev 라이브러리 설치
- [ ] Wire 라이브러리 확인 (기본 내장)

#### 🔄 대안: PlatformIO (고급 사용자)
```
설치: VSCode Extension으로 설치
장점: 더 강력한 IDE, 라이브러리 관리 편리
단점: 초보자에게는 복잡할 수 있음
```

### 2. Python 데이터 분석 환경

#### ✅ Python 설치 (필수)
```
다운로드: https://www.python.org/downloads/
버전: Python 3.9+ 권장
용도: 센서 데이터 분석, 시각화, 머신러닝
```

#### ✅ Anaconda 설치 (강력 권장)
```
다운로드: https://www.anaconda.com/products/distribution
포함: Python + 주요 라이브러리 + Jupyter Notebook
장점: 라이브러리 의존성 관리가 쉬움
```

#### 📦 필수 Python 라이브러리
```bash
# 기본 데이터 분석
pip install numpy pandas matplotlib seaborn

# 센서 데이터 처리
pip install scipy scikit-learn

# 시리얼 통신
pip install pyserial

# 실시간 플롯
pip install matplotlib-animation plotly dash

# Jupyter Notebook (Anaconda에 포함)
pip install jupyter
```

### 3. 코드 에디터

#### ✅ Visual Studio Code (권장)
```
다운로드: https://code.visualstudio.com/
무료: Yes
용도: 모든 코드 작성 (Python, JavaScript, Arduino)
```

**유용한 VSCode 확장팩:**
- [ ] Python
- [ ] Arduino
- [ ] PlatformIO IDE
- [ ] Git History
- [ ] Python Docstring Generator

#### 🔄 대안 에디터들
```
PyCharm Community (Python 전용): 무료
Sublime Text: 가볍고 빠름
Atom: GitHub 기반 (개발 중단됨)
```

---

## 📱 Phase 2: 모바일 앱 개발

### 1. Flutter 개발환경

#### ✅ Flutter SDK 설치
```
다운로드: https://flutter.dev/docs/get-started/install
지원 OS: Windows, macOS, Linux
용도: 크로스플랫폼 모바일 앱 개발
```

**설치 단계:**
```bash
# 1. Flutter SDK 압축 해제
# 2. 환경변수 PATH에 flutter/bin 추가
# 3. 의존성 확인
flutter doctor

# 4. Android 개발환경 설정
```

#### ✅ Android Studio (Android 개발용)
```
다운로드: https://developer.android.com/studio
용도: Android 에뮬레이터, SDK 관리
필수: Android SDK, 에뮬레이터
```

#### 🍎 iOS 개발 (Mac만 가능)
```
Xcode: Mac App Store에서 설치
iOS Simulator: Xcode에 포함
Apple Developer Account: 실제 기기 테스트시 필요
```

### 2. 백엔드 서비스 (선택)

#### ✅ Firebase (Google)
```
웹사이트: https://firebase.google.com/
무료 플랜: Spark (제한적이지만 개발용 충분)
기능: 데이터베이스, 인증, 푸시알림, 호스팅
```

#### 🔄 대안 서비스들
```
AWS Amplify: 아마존 클라우드
Supabase: 오픈소스 Firebase 대안  
MongoDB Atlas: 클라우드 데이터베이스
```

---

## 🤖 Phase 3: 머신러닝 및 고급 분석

### 1. 머신러닝 라이브러리

#### ✅ TensorFlow (권장)
```bash
# CPU 버전
pip install tensorflow

# GPU 버전 (NVIDIA GPU 있을 때)
pip install tensorflow-gpu

# 모바일용 경량화
pip install tensorflow-lite
```

#### 🔄 PyTorch (대안)
```bash
# CPU 버전
pip install torch torchvision torchaudio

# GPU 버전 설치는 공식 사이트 참조
# https://pytorch.org/get-started/locally/
```

#### ✅ 추가 ML 라이브러리
```bash
# 전통적인 머신러닝
pip install scikit-learn xgboost

# 딥러닝 도구
pip install keras

# 모델 시각화
pip install tensorboard

# 하이퍼파라미터 튜닝
pip install optuna hyperopt
```

### 2. 데이터 처리 및 시각화

#### ✅ 고급 데이터 처리
```bash
# 대용량 데이터 처리
pip install dask

# 시계열 분석
pip install statsmodels

# 신호 처리
pip install scipy pywavelets

# 3D 플롯
pip install matplotlib mpl_toolkits
```

#### ✅ 웹 대시보드 (선택)
```bash
# 인터랙티브 대시보드
pip install streamlit

# 웹 프레임워크
pip install fastapi uvicorn

# 실시간 웹앱
pip install flask socketio
```

---

## 🛠️ 개발 도구 및 유틸리티

### 1. 버전 관리

#### ✅ Git (필수)
```
다운로드: https://git-scm.com/downloads
용도: 소스코드 버전 관리
GUI: GitHub Desktop, SourceTree (선택)
```

**기본 Git 설정:**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2. 데이터베이스 (로컬)

#### ✅ SQLite (권장)
```
설치: Python sqlite3 모듈 (기본 내장)
용도: 로컬 데이터 저장
GUI: DB Browser for SQLite
```

### 3. 시리얼 통신 도구

#### ✅ Arduino Serial Monitor (기본)
```
Arduino IDE에 내장
기본적인 시리얼 데이터 모니터링
```

#### 🔄 고급 시리얼 도구들
```
PuTTY: Windows용 터미널
CoolTerm: 크로스플랫폼
Serial Studio: 실시간 데이터 시각화
```

---

## 📊 개발 환경 체크리스트

### ✅ Phase 1 필수 설치
- [ ] Arduino IDE + MPU6050 라이브러리
- [ ] Python 3.9+ (Anaconda 권장)
- [ ] VSCode + Python 확장
- [ ] Git 설치 및 설정

### ✅ Python 라이브러리 설치 확인
```bash
# 설치 확인 스크립트
python -c "
import numpy
import pandas  
import matplotlib
import serial
import scipy
print('모든 라이브러리 설치 완료!')
"
```

### ✅ Phase 2 준비 (모바일 앱)
- [ ] Flutter SDK 설치
- [ ] Android Studio + SDK
- [ ] 에뮬레이터 설정
- [ ] `flutter doctor` 통과

### ✅ Phase 3 준비 (머신러닝)  
- [ ] TensorFlow 또는 PyTorch
- [ ] Jupyter Notebook 환경
- [ ] GPU 설정 (있는 경우)

---

## 💡 개발 환경별 추천 구성

### 🖥️ Windows 사용자
```
필수: Arduino IDE, Anaconda, VSCode, Git
모바일: Android Studio (Flutter)
선택: PuTTY (시리얼 통신)
```

### 🍎 macOS 사용자  
```
필수: Arduino IDE, Anaconda, VSCode, Git
모바일: Xcode + Android Studio (Flutter)
장점: iOS 앱 개발 가능
```

### 🐧 Linux 사용자
```
필수: Arduino IDE, Python, VSCode, Git  
모바일: Android Studio (Flutter)
장점: 개발 환경 커스터마이징 자유도 높음
```

---

## 🚀 빠른 시작 가이드

### 1단계: 기본 환경 (30분)
```bash
# 1. Arduino IDE 설치
# 2. Anaconda 설치  
# 3. VSCode 설치
# 4. Git 설치
```

### 2단계: Python 라이브러리 (10분)
```bash
conda create -n posture-tracker python=3.9
conda activate posture-tracker
pip install numpy pandas matplotlib pyserial scipy scikit-learn jupyter
```

### 3단계: Arduino 라이브러리 (5분)
```
Arduino IDE → 라이브러리 매니저 → 'MPU6050' 검색 설치
```

### 4단계: 테스트 (5분)
```python
# Python 테스트
python -c "import numpy; print('Python 준비 완료!')"

# Arduino 테스트: Blink 예제 업로드
```

---

## ⚠️ 주의사항 및 팁

### 설치 시 주의점
- **Python**: PATH 환경변수 추가 체크 필수
- **Arduino**: 관리자 권한으로 실행 권장
- **Flutter**: 안정적인 인터넷 연결 필요 (다운로드 용량 큼)
- **Git**: 초기 설정 (이름, 이메일) 필수

### 메모리 및 디스크 요구사항
```
기본 환경: ~5GB
Flutter 추가: ~3GB  
Android Studio: ~4GB
머신러닝 라이브러리: ~2GB
총 필요 용량: ~15GB
```

### 성능 권장사항
```
RAM: 8GB 이상 (16GB 권장)
저장공간: SSD 권장 (컴파일 속도 향상)
인터넷: 초기 설치시 안정적 연결 필요
```

**💡 Tip: 가상환경(conda/venv) 사용으로 라이브러리 충돌 방지!**
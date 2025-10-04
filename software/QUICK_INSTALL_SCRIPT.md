# 🚀 빠른 소프트웨어 설치 스크립트

> 개발환경을 빠르게 구축할 수 있는 스크립트와 명령어들

## 💻 Windows 자동 설치 스크립트

### 1단계: 필수 소프트웨어 자동 설치 (PowerShell)

```powershell
# PowerShell을 관리자 권한으로 실행 후 아래 실행

# Chocolatey 설치 (Windows 패키지 매니저)
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# 기본 개발 도구 설치
choco install -y git vscode arduino python anaconda3

# Chrome 설치 (Flutter 웹 테스트용)
choco install -y googlechrome

Write-Host "기본 소프트웨어 설치 완료!" -ForegroundColor Green
Write-Host "컴퓨터 재시작을 권장합니다." -ForegroundColor Yellow
```

### 2단계: Python 환경 설정 (Anaconda Prompt)

```bash
# Anaconda Prompt 실행 후 아래 명령어 실행

# 프로젝트용 가상환경 생성
conda create -n smart-posture python=3.9 -y
conda activate smart-posture

# 기본 라이브러리 설치
conda install -y numpy pandas matplotlib seaborn jupyter
pip install pyserial scipy scikit-learn plotly dash streamlit

# 설치 확인
python -c "
import numpy, pandas, matplotlib, serial, scipy, sklearn
print('✅ Python 환경 설정 완료!')
print('가상환경:', 'smart-posture')
"
```

---

## 🐧 Linux/macOS 자동 설치 스크립트

### Ubuntu/Debian 계열
```bash
#!/bin/bash
# install_dev_env.sh

echo "🚀 Smart Posture Tracker 개발환경 설치 시작..."

# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 기본 개발 도구
sudo apt install -y git curl wget build-essential

# Python 개발환경
sudo apt install -y python3 python3-pip python3-venv

# VSCode 설치
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list
sudo apt update
sudo apt install -y code

# Arduino IDE 설치
wget https://downloads.arduino.cc/arduino-1.8.19-linux64.tar.xz
tar -xf arduino-1.8.19-linux64.tar.xz
sudo mv arduino-1.8.19 /opt/arduino
sudo /opt/arduino/install.sh

# Python 가상환경 및 라이브러리
python3 -m venv smart-posture-env
source smart-posture-env/bin/activate
pip install numpy pandas matplotlib pyserial scipy scikit-learn jupyter plotly

echo "✅ 기본 개발환경 설치 완료!"
echo "가상환경 활성화: source smart-posture-env/bin/activate"
```

### macOS (Homebrew)
```bash
#!/bin/bash
# install_macos.sh

echo "🚀 macOS 개발환경 설치 시작..."

# Homebrew 설치 (없는 경우)
if ! command -v brew &> /dev/null; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# 기본 도구 설치
brew install git python@3.9
brew install --cask visual-studio-code arduino

# Python 가상환경 설정
python3 -m venv smart-posture-env
source smart-posture-env/bin/activate
pip install numpy pandas matplotlib pyserial scipy scikit-learn jupyter

echo "✅ macOS 개발환경 설치 완료!"
```

---

## 📱 Flutter 개발환경 자동 설정

### Windows (PowerShell)
```powershell
# Flutter SDK 다운로드 및 설치
$flutterPath = "C:\flutter"
Invoke-WebRequest -Uri "https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.13.0-stable.zip" -OutFile "flutter.zip"
Expand-Archive -Path "flutter.zip" -DestinationPath "C:\"

# PATH 환경변수에 추가
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$flutterPath\bin", [EnvironmentVariableTarget]::User)

# Android Studio 설치 (Chocolatey)
choco install -y androidstudio

Write-Host "Flutter 설치 완료! 새 터미널에서 'flutter doctor' 실행하세요." -ForegroundColor Green
```

### Linux/macOS
```bash
# Flutter SDK 설치
cd ~/
git clone https://github.com/flutter/flutter.git -b stable
export PATH="$PATH:`pwd`/flutter/bin"

# bashrc/zshrc에 PATH 추가
echo 'export PATH="$PATH:$HOME/flutter/bin"' >> ~/.bashrc

# Android Studio 설치 (Linux)
sudo snap install android-studio --classic

# 의존성 확인
flutter doctor
```

---

## 🔧 개발 도구 자동 설정

### VSCode 확장팩 자동 설치
```bash
# 필수 확장팩들
code --install-extension ms-python.python
code --install-extension vsciot-vscode.vscode-arduino
code --install-extension dart-code.flutter
code --install-extension ms-vscode.cpptools
code --install-extension github.github-vscode-theme
code --install-extension ms-python.pylint

echo "✅ VSCode 확장팩 설치 완료!"
```

### Git 초기 설정 자동화
```bash
#!/bin/bash
# git_setup.sh

read -p "Git 사용자 이름을 입력하세요: " username
read -p "Git 이메일을 입력하세요: " email

git config --global user.name "$username"
git config --global user.email "$email"
git config --global init.defaultBranch main
git config --global core.autocrlf true

echo "✅ Git 설정 완료!"
echo "사용자: $username"
echo "이메일: $email"
```

---

## 🧪 설치 검증 스크립트

### 전체 환경 테스트
```python
#!/usr/bin/env python3
# test_environment.py

import sys
import subprocess

def test_installation():
    """개발 환경 설치 상태 검증"""
    
    print("🔍 Smart Posture Tracker 개발환경 검증 시작...\n")
    
    tests = {
        "Python": test_python,
        "필수 라이브러리": test_libraries, 
        "Arduino CLI": test_arduino,
        "Git": test_git,
        "Flutter": test_flutter
    }
    
    results = {}
    for name, test_func in tests.items():
        try:
            test_func()
            results[name] = "✅ 통과"
        except Exception as e:
            results[name] = f"❌ 실패: {str(e)}"
    
    print("\n📊 검증 결과:")
    print("-" * 40)
    for name, result in results.items():
        print(f"{name:15}: {result}")
    
    print("\n" + "="*50)
    passed = sum(1 for r in results.values() if "✅" in r)
    total = len(results)
    print(f"통과: {passed}/{total}")
    
    if passed == total:
        print("🎉 모든 환경이 정상적으로 설정되었습니다!")
    else:
        print("⚠️  일부 환경에 문제가 있습니다. 위 결과를 확인하세요.")

def test_python():
    """Python 설치 확인"""
    version = sys.version_info
    if version.major < 3 or version.minor < 8:
        raise Exception(f"Python 3.8+ 필요 (현재: {version.major}.{version.minor})")
    print(f"Python {version.major}.{version.minor}.{version.micro}")

def test_libraries():
    """필수 라이브러리 확인"""
    libraries = ['numpy', 'pandas', 'matplotlib', 'serial', 'scipy']
    for lib in libraries:
        try:
            __import__(lib)
        except ImportError:
            raise Exception(f"라이브러리 '{lib}' 설치 필요")
    print(f"필수 라이브러리 {len(libraries)}개 모두 설치됨")

def test_arduino():
    """Arduino CLI 확인"""
    try:
        result = subprocess.run(['arduino-cli', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("Arduino CLI 설치됨")
        else:
            raise Exception("Arduino CLI 실행 실패")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Arduino IDE는 있지만 CLI가 없을 수 있음
        print("Arduino IDE는 수동 확인 필요")

def test_git():
    """Git 설치 확인"""
    result = subprocess.run(['git', '--version'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception("Git 설치 필요")
    print(result.stdout.strip())

def test_flutter():
    """Flutter 설치 확인 (선택)"""
    try:
        result = subprocess.run(['flutter', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("Flutter 설치됨")
        else:
            print("Flutter 미설치 (Phase 2에서 필요)")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("Flutter 미설치 (Phase 2에서 필요)")

if __name__ == "__main__":
    test_installation()
```

---

## 📋 설치 체크리스트

### ✅ Phase 1 필수 설치 확인
- [ ] Python 3.8+ 설치됨
- [ ] Arduino IDE 설치됨
- [ ] VSCode + Python 확장 설치됨
- [ ] Git 설치 및 설정 완료
- [ ] 가상환경 `smart-posture` 생성됨
- [ ] 필수 라이브러리 설치됨 (numpy, pandas, matplotlib, pyserial, scipy)

### ✅ 설치 검증
```bash
# Python 가상환경 활성화
conda activate smart-posture  # 또는 source smart-posture-env/bin/activate

# 검증 스크립트 실행  
python test_environment.py

# Arduino IDE 실행 테스트
# VSCode 실행 테스트
# Git 명령어 테스트: git --version
```

### ✅ Phase 2 준비 (선택적)
- [ ] Flutter SDK 설치
- [ ] Android Studio 설치
- [ ] `flutter doctor` 통과
- [ ] 에뮬레이터 설정

---

## ⚡ 빠른 시작 명령어 모음

### 일일 개발 시작
```bash
# 1. 가상환경 활성화
conda activate smart-posture

# 2. VSCode에서 프로젝트 열기
code smart-posture-tracker/

# 3. Jupyter Notebook 시작 (데이터 분석용)
jupyter notebook

# 4. Arduino IDE 실행
arduino
```

### 프로젝트 클론 및 설정 (나중에 공유할 때)
```bash
# GitHub에서 클론
git clone https://github.com/yourusername/smart-posture-tracker.git
cd smart-posture-tracker

# 가상환경 생성 및 의존성 설치
conda env create -f environment.yml  # 또는
pip install -r requirements.txt

# 환경 활성화
conda activate smart-posture
```

**💡 Tip: 이 스크립트들을 실행하기 전에 각 OS별 권한 설정을 확인하세요!**
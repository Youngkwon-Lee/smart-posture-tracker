# 🔧 Hardware Setup Guide

Smart Posture Tracker 하드웨어 설정 가이드입니다.

## 📋 Required Components

### Essential Hardware
- **ESP32 Development Board** (1개)
- **MPU6050 6-DOF IMU Sensor** (1개) 
- **Breadboard** (400 tie-points)
- **Jumper Wires** (Male-to-Male, 최소 4개)
- **USB Cable** (ESP32 연결용)

### Optional Components
- **LED** (상태 표시용)
- **Buzzer** (알림용)  
- **Resistors** (220Ω for LED, 10kΩ pull-up)
- **Case/Enclosure** (프로토타입 보호)

## 🔌 Wiring Connections

### ESP32 ↔ MPU6050 Connection
```
ESP32 Pin    →    MPU6050 Pin    →    Function
-------------------------------------------------
3.3V         →    VCC             →    Power Supply
GND          →    GND             →    Ground
GPIO21       →    SDA             →    I2C Data Line
GPIO22       →    SCL             →    I2C Clock Line
```

### Wiring Diagram
```
ESP32                    MPU6050
┌─────────────┐         ┌─────────┐
│         3.3V├─────────┤VCC      │
│          GND├─────────┤GND      │
│      GPIO21 ├─────────┤SDA      │
│      GPIO22 ├─────────┤SCL      │
└─────────────┘         └─────────┘
```

## ⚙️ Setup Instructions

### Step 1: Hardware Assembly
1. **Power Off** ESP32 before making connections
2. Connect **VCC** to **3.3V** (⚠️ NOT 5V - can damage sensor)
3. Connect **GND** to **GND**
4. Connect **SDA** to **GPIO21** 
5. Connect **SCL** to **GPIO22**
6. Double-check all connections

### Step 2: Software Setup
1. **Install Arduino IDE**
   - Download: https://arduino.cc/downloads
   - Install ESP32 board support

2. **Add ESP32 Board Manager URL**
   ```
   https://espressif.github.io/arduino-esp32/package_esp32_index.json
   ```

3. **Install Required Libraries**
   - Adafruit MPU6050
   - Adafruit Unified Sensor
   - Wire (built-in)

### Step 3: Upload Test Code
1. Open `hardware/arduino/mpu6050_basic_test/mpu6050_basic_test.ino`
2. Select Board: **ESP32 Dev Module**
3. Select Port: **COM3** (or your ESP32 port)
4. Click **Upload**

## 🧪 Testing & Verification

### Power-On Test
1. **Connect USB** cable to ESP32
2. **Open Serial Monitor** (115200 baud)
3. **Press Reset** button on ESP32
4. **Expected Output**:
   ```
   Smart Posture Tracker - MPU6050 Test
   =====================================
   MPU6050 Found!
   Accelerometer range set to: +-8G
   Gyro range set to: +- 500 deg/s
   Filter bandwidth set to: 21 Hz
   
   CSV Header: timestamp,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,temp
   1234,0.123,-0.456,9.789,0.001,-0.002,0.003,25.67
   ```

### Movement Test
1. **Keep sensor still** - should see ~9.8 m/s² on one axis (gravity)
2. **Tilt sensor** - watch acceleration values change
3. **Rotate sensor** - observe gyroscope readings
4. **Temperature** should be ~25°C (room temperature)

## 🐛 Troubleshooting

### ❌ "Failed to find MPU6050 chip"
**Possible Causes:**
- Loose wiring connections
- Wrong I2C pins (should be 21/22)
- Power supply issue (check 3.3V)
- Faulty MPU6050 module

**Solutions:**
1. Check all wiring connections
2. Use multimeter to verify 3.3V supply
3. Try different jumper wires
4. Test with I2C scanner code

### ❌ ESP32 Not Detected
**Possible Causes:**
- USB cable issue (some cables are power-only)
- Driver not installed
- Wrong COM port selected

**Solutions:**
1. Try different USB cable
2. Install CP210x or CH340 drivers
3. Check Device Manager for COM ports
4. Press and hold BOOT button while uploading

### ❌ Erratic Sensor Readings
**Possible Causes:**
- Electrical interference
- Poor connections
- Sensor calibration needed

**Solutions:**
1. Keep sensor steady during initialization
2. Add power filtering capacitors
3. Check for loose connections
4. Increase I2C pull-up resistors (4.7kΩ)

## 📊 Data Output Format

The sensor outputs CSV data in this format:
```csv
timestamp,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,temp
1000,0.123,-0.456,9.789,0.001,-0.002,0.003,25.67
```

**Column Descriptions:**
- `timestamp`: Milliseconds since startup
- `accel_x/y/z`: Acceleration in m/s² (X=forward/back, Y=left/right, Z=up/down)
- `gyro_x/y/z`: Angular velocity in rad/s 
- `temp`: Temperature in Celsius

## ⚡ Power Considerations

### USB Power
- **Current Draw**: ~100mA typical
- **Suitable for**: Desktop testing and development

### Battery Power  
- **Recommended**: 3.7V Li-Po battery with voltage regulator
- **Capacity**: 1000mAh+ for several hours operation
- **Future**: Add sleep modes for extended battery life

## 🔄 Next Steps

After successful hardware setup:
1. ✅ Hardware working correctly
2. ⏭️ Run Python data analysis script
3. ⏭️ Collect baseline posture data  
4. ⏭️ Develop real-time feedback system
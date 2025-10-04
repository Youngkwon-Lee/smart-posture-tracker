/*
 * Smart Posture Tracker - MPU6050 Basic Test
 * 
 * This sketch tests basic MPU6050 sensor functionality
 * Reads accelerometer and gyroscope data and outputs to Serial
 * 
 * Hardware Connections:
 * - MPU6050 VCC -> ESP32 3.3V
 * - MPU6050 GND -> ESP32 GND  
 * - MPU6050 SDA -> ESP32 GPIO21 (default)
 * - MPU6050 SCL -> ESP32 GPIO22 (default)
 */

#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

Adafruit_MPU6050 mpu;

void setup(void) {
  Serial.begin(115200);
  while (!Serial)
    delay(10); // Wait for Serial to be ready

  Serial.println("Smart Posture Tracker - MPU6050 Test");
  Serial.println("=====================================");

  // Initialize I2C communication
  Wire.begin();

  // Try to initialize MPU6050
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("MPU6050 Found!");  // Set up motion detection
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  Serial.print("Accelerometer range set to: ");
  switch (mpu.getAccelerometerRange()) {
  case MPU6050_RANGE_2_G:
    Serial.println("+-2G");
    break;
  case MPU6050_RANGE_4_G:
    Serial.println("+-4G");
    break;
  case MPU6050_RANGE_8_G:
    Serial.println("+-8G");
    break;
  case MPU6050_RANGE_16_G:
    Serial.println("+-16G");
    break;
  }

  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  Serial.print("Gyro range set to: ");
  switch (mpu.getGyroRange()) {
  case MPU6050_RANGE_250_DEG:
    Serial.println("+- 250 deg/s");
    break;
  case MPU6050_RANGE_500_DEG:
    Serial.println("+- 500 deg/s");
    break;
  case MPU6050_RANGE_1000_DEG:
    Serial.println("+- 1000 deg/s");
    break;
  case MPU6050_RANGE_2000_DEG:
    Serial.println("+- 2000 deg/s");
    break;
  }  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  Serial.print("Filter bandwidth set to: ");
  switch (mpu.getFilterBandwidth()) {
  case MPU6050_BAND_260_HZ:
    Serial.println("260 Hz");
    break;
  case MPU6050_BAND_184_HZ:
    Serial.println("184 Hz");
    break;
  case MPU6050_BAND_94_HZ:
    Serial.println("94 Hz");
    break;
  case MPU6050_BAND_44_HZ:
    Serial.println("44 Hz");
    break;
  case MPU6050_BAND_21_HZ:
    Serial.println("21 Hz");
    break;
  case MPU6050_BAND_10_HZ:
    Serial.println("10 Hz");
    break;
  case MPU6050_BAND_5_HZ:
    Serial.println("5 Hz");
    break;
  }

  Serial.println();
  Serial.println("CSV Header: timestamp,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,temp");
  delay(100);
}

void loop() {
  // Get sensor readings
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  // Get current timestamp
  unsigned long timestamp = millis();
  
  // Output data in CSV format for easy analysis with pandas
  Serial.print(timestamp);
  Serial.print(",");
  Serial.print(a.acceleration.x, 3);
  Serial.print(",");
  Serial.print(a.acceleration.y, 3);
  Serial.print(",");
  Serial.print(a.acceleration.z, 3);
  Serial.print(",");
  Serial.print(g.gyro.x, 3);
  Serial.print(",");
  Serial.print(g.gyro.y, 3);
  Serial.print(",");
  Serial.print(g.gyro.z, 3);
  Serial.print(",");
  Serial.println(temp.temperature, 2);

  // Sample at 10Hz (100ms delay)
  delay(100);
}
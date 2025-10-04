/*
 * Smart Posture Tracker - Dual MPU6050 System
 * 
 * This sketch reads from two MPU6050 sensors to track:
 * - Sensor 1 (0x68): Upper spine/neck movement  
 * - Sensor 2 (0x69): Mid spine movement
 * 
 * Hardware Connections:
 * ESP32 -> Both MPU6050 sensors
 * - 3.3V  -> VCC (both sensors)
 * - GND   -> GND (both sensors)  
 * - GPIO21 -> SDA (both sensors)
 * - GPIO22 -> SCL (both sensors)
 * 
 * Important: Connect AD0 pin on second sensor to 3.3V for address 0x69
 */

#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

// Create two sensor objects with different I2C addresses
Adafruit_MPU6050 sensor1;  // Default address 0x68
Adafruit_MPU6050 sensor2;  // Address 0x69 (AD0 connected to HIGH)

// Calibration offsets (will be calculated during setup)
float accel1_offset[3] = {0, 0, 0};
float gyro1_offset[3] = {0, 0, 0};
float accel2_offset[3] = {0, 0, 0}; 
float gyro2_offset[3] = {0, 0, 0};

void setup(void) {
  Serial.begin(115200);
  while (!Serial) delay(10);

  Serial.println("Smart Posture Tracker - Dual MPU6050 System");
  Serial.println("===========================================");

  Wire.begin();

  // Initialize first sensor (default address 0x68)
  if (!sensor1.begin(0x68)) {
    Serial.println("Failed to find MPU6050 sensor 1 at 0x68!");
    while (1) delay(10);
  }
  Serial.println("MPU6050 Sensor 1 (0x68) Found!");

  // Initialize second sensor (address 0x69)  
  if (!sensor2.begin(0x69)) {
    Serial.println("Failed to find MPU6050 sensor 2 at 0x69!");
    Serial.println("Check that AD0 pin is connected to 3.3V on sensor 2");
    while (1) delay(10);
  }
  Serial.println("MPU6050 Sensor 2 (0x69) Found!");

  // Configure both sensors identically
  configureSensor(sensor1, "Sensor 1");
  configureSensor(sensor2, "Sensor 2");

  // Calibrate sensors
  Serial.println("Calibrating sensors... Keep sensors still!");
  calibrateSensors();
  
  Serial.println();
  Serial.println("CSV Header: timestamp,s1_ax,s1_ay,s1_az,s1_gx,s1_gy,s1_gz,s1_temp,s2_ax,s2_ay,s2_az,s2_gx,s2_gy,s2_gz,s2_temp");
  delay(1000);
}void configureSensor(Adafruit_MPU6050 &sensor, const char* name) {
  // Set accelerometer range
  sensor.setAccelerometerRange(MPU6050_RANGE_8_G);
  Serial.print(name);
  Serial.print(" - Accelerometer range: ");
  switch (sensor.getAccelerometerRange()) {
    case MPU6050_RANGE_2_G: Serial.println("±2G"); break;
    case MPU6050_RANGE_4_G: Serial.println("±4G"); break;
    case MPU6050_RANGE_8_G: Serial.println("±8G"); break;
    case MPU6050_RANGE_16_G: Serial.println("±16G"); break;
  }

  // Set gyro range  
  sensor.setGyroRange(MPU6050_RANGE_500_DEG);
  Serial.print(name);
  Serial.print(" - Gyro range: ");
  switch (sensor.getGyroRange()) {
    case MPU6050_RANGE_250_DEG: Serial.println("±250°/s"); break;
    case MPU6050_RANGE_500_DEG: Serial.println("±500°/s"); break;
    case MPU6050_RANGE_1000_DEG: Serial.println("±1000°/s"); break;
    case MPU6050_RANGE_2000_DEG: Serial.println("±2000°/s"); break;
  }

  // Set filter bandwidth
  sensor.setFilterBandwidth(MPU6050_BAND_21_HZ);
  Serial.print(name);
  Serial.println(" - Filter: 21 Hz");
}

void calibrateSensors() {
  const int calibrationSamples = 100;
  float sum1_accel[3] = {0, 0, 0};
  float sum1_gyro[3] = {0, 0, 0};
  float sum2_accel[3] = {0, 0, 0};
  float sum2_gyro[3] = {0, 0, 0};
  
  Serial.print("Calibrating");
  
  for (int i = 0; i < calibrationSamples; i++) {
    sensors_event_t a1, g1, temp1;
    sensors_event_t a2, g2, temp2;
    
    sensor1.getEvent(&a1, &g1, &temp1);
    sensor2.getEvent(&a2, &g2, &temp2);
    
    // Accumulate sensor 1 readings
    sum1_accel[0] += a1.acceleration.x;
    sum1_accel[1] += a1.acceleration.y; 
    sum1_accel[2] += a1.acceleration.z;
    sum1_gyro[0] += g1.gyro.x;
    sum1_gyro[1] += g1.gyro.y;
    sum1_gyro[2] += g1.gyro.z;
    
    // Accumulate sensor 2 readings
    sum2_accel[0] += a2.acceleration.x;
    sum2_accel[1] += a2.acceleration.y;
    sum2_accel[2] += a2.acceleration.z; 
    sum2_gyro[0] += g2.gyro.x;
    sum2_gyro[1] += g2.gyro.y;
    sum2_gyro[2] += g2.gyro.z;
    
    if (i % 20 == 0) Serial.print(".");
    delay(10);
  }
  
  // Calculate offsets (average of samples)
  for (int i = 0; i < 3; i++) {
    accel1_offset[i] = sum1_accel[i] / calibrationSamples;
    gyro1_offset[i] = sum1_gyro[i] / calibrationSamples;
    accel2_offset[i] = sum2_accel[i] / calibrationSamples;  
    gyro2_offset[i] = sum2_gyro[i] / calibrationSamples;
  }
  
  // Don't remove gravity from Z-axis (keep it for orientation reference)
  accel1_offset[2] = 0;  // Keep gravity on Z-axis
  accel2_offset[2] = 0;  // Keep gravity on Z-axis
  
  Serial.println(" Done!");
  Serial.println("Calibration complete. Starting data collection...");
}void loop() {
  // Read from both sensors
  sensors_event_t a1, g1, temp1;
  sensors_event_t a2, g2, temp2;
  
  sensor1.getEvent(&a1, &g1, &temp1);
  sensor2.getEvent(&a2, &g2, &temp2);
  
  // Apply calibration offsets
  float s1_ax = a1.acceleration.x - accel1_offset[0];
  float s1_ay = a1.acceleration.y - accel1_offset[1];
  float s1_az = a1.acceleration.z - accel1_offset[2];
  float s1_gx = g1.gyro.x - gyro1_offset[0];
  float s1_gy = g1.gyro.y - gyro1_offset[1];
  float s1_gz = g1.gyro.z - gyro1_offset[2];
  
  float s2_ax = a2.acceleration.x - accel2_offset[0];
  float s2_ay = a2.acceleration.y - accel2_offset[1];  
  float s2_az = a2.acceleration.z - accel2_offset[2];
  float s2_gx = g2.gyro.x - gyro2_offset[0];
  float s2_gy = g2.gyro.y - gyro2_offset[1];
  float s2_gz = g2.gyro.z - gyro2_offset[2];
  
  // Get timestamp
  unsigned long timestamp = millis();
  
  // Output CSV format: timestamp,s1_data(6),s1_temp,s2_data(6),s2_temp
  Serial.print(timestamp);
  
  // Sensor 1 data
  Serial.print(","); Serial.print(s1_ax, 3);
  Serial.print(","); Serial.print(s1_ay, 3);
  Serial.print(","); Serial.print(s1_az, 3);
  Serial.print(","); Serial.print(s1_gx, 3);
  Serial.print(","); Serial.print(s1_gy, 3);
  Serial.print(","); Serial.print(s1_gz, 3);
  Serial.print(","); Serial.print(temp1.temperature, 2);
  
  // Sensor 2 data
  Serial.print(","); Serial.print(s2_ax, 3);
  Serial.print(","); Serial.print(s2_ay, 3);
  Serial.print(","); Serial.print(s2_az, 3);
  Serial.print(","); Serial.print(s2_gx, 3);
  Serial.print(","); Serial.print(s2_gy, 3);
  Serial.print(","); Serial.print(s2_gz, 3);
  Serial.print(","); Serial.println(temp2.temperature, 2);
  
  // Sample at 10Hz
  delay(100);
}
/*
 * IAHRS Dual Sensor Code for LattePanda + Arduino UNO R3
 * Smart Posture Tracker - IAHRS intellithings RB-SDA-v1 integration
 * 
 * Hardware Setup:
 * - LattePanda 4GB/64GB (main processing unit)
 * - Arduino UNO R3 (sensor interface)
 * - 2x IAHRS intellithings RB-SDA-v1 IMU sensors
 * 
 * IAHRS Specifications:
 * - UART communication at 9600 baud
 * - Voltage: 4.2-12V (use 5V from Arduino)
 * - Output: Roll/Pitch/Yaw with 0.001° resolution
 */

#include <SoftwareSerial.h>

// UART connections for dual IAHRS sensors
SoftwareSerial sensor1(2, 3);  // RX=2, TX=3 for Sensor 1
SoftwareSerial sensor2(4, 5);  // RX=4, TX=5 for Sensor 2

// Data structure for IAHRS sensor data
struct IAHRSData {
  float roll, pitch, yaw;
  float accel_x, accel_y, accel_z;
  float gyro_x, gyro_y, gyro_z;
  unsigned long timestamp;
  bool data_valid;
};

IAHRSData sensor1_data, sensor2_data;
String sensor1_buffer = "";
String sensor2_buffer = "";

void setup() {
  Serial.begin(115200);
  sensor1.begin(9600);  // IAHRS default baud rate
  sensor2.begin(9600);
  
  delay(2000);
  
  Serial.println("IAHRS Dual Sensor - Smart Posture Tracker");
  Serial.println("Initializing IAHRS sensors...");
  
  // Initialize both sensors
  initIAHRSSensor(sensor1, "Sensor1");
  initIAHRSSensor(sensor2, "Sensor2");
  
  // CSV header for data logging
  Serial.println("timestamp,s1_roll,s1_pitch,s1_yaw,s2_roll,s2_pitch,s2_yaw,spine_curvature,posture_status");
  
  delay(1000);
}void loop() {
  unsigned long currentTime = millis();
  
  // Read data from both sensors
  readIAHRSData(sensor1, sensor1_buffer, sensor1_data, currentTime);
  readIAHRSData(sensor2, sensor2_buffer, sensor2_data, currentTime);
  
  // Calculate spine curvature if both sensors have valid data
  if (sensor1_data.data_valid && sensor2_data.data_valid) {
    float spine_curvature = calculateSpineCurvature();
    String posture_status = evaluatePosture(spine_curvature);
    
    // Output CSV data
    Serial.print(currentTime);
    Serial.print(",");
    Serial.print(sensor1_data.roll, 3);
    Serial.print(",");
    Serial.print(sensor1_data.pitch, 3);
    Serial.print(",");
    Serial.print(sensor1_data.yaw, 3);
    Serial.print(",");
    Serial.print(sensor2_data.roll, 3);
    Serial.print(",");
    Serial.print(sensor2_data.pitch, 3);
    Serial.print(",");
    Serial.print(sensor2_data.yaw, 3);
    Serial.print(",");
    Serial.print(spine_curvature, 3);
    Serial.print(",");
    Serial.println(posture_status);
  }
  
  delay(100); // 10Hz sampling rate
}

void initIAHRSSensor(SoftwareSerial &sensor, String name) {
  Serial.println("Initializing " + name + "...");
  
  // Reset sensor to factory defaults
  sensor.println("fd");
  delay(100);
  
  // Set output data rate to 10Hz (100ms interval)
  sensor.println("od,100");
  delay(100);
  
  // Enable continuous output
  sensor.println("so,1");
  delay(100);
  
  // Request version info for verification
  sensor.println("vr");
  delay(500);
  
  Serial.println(name + " initialized");
}void readIAHRSData(SoftwareSerial &sensor, String &buffer, IAHRSData &data, unsigned long timestamp) {
  // Read available data from sensor
  while (sensor.available()) {
    char c = sensor.read();
    
    if (c == '\n' || c == '\r') {
      if (buffer.length() > 0) {
        parseIAHRSData(buffer, data, timestamp);
        buffer = "";
      }
    } else {
      buffer += c;
    }
  }
}

void parseIAHRSData(String dataString, IAHRSData &data, unsigned long timestamp) {
  // IAHRS typical output format: *YPR=yaw,pitch,roll
  // or other formats depending on configuration
  dataString.trim();
  
  if (dataString.startsWith("*YPR=")) {
    // Parse Yaw, Pitch, Roll data
    String values = dataString.substring(5); // Remove "*YPR="
    
    int comma1 = values.indexOf(',');
    int comma2 = values.indexOf(',', comma1 + 1);
    
    if (comma1 > 0 && comma2 > comma1) {
      data.yaw = values.substring(0, comma1).toFloat();
      data.pitch = values.substring(comma1 + 1, comma2).toFloat();
      data.roll = values.substring(comma2 + 1).toFloat();
      data.timestamp = timestamp;
      data.data_valid = true;
    }
  }
  // Add other parsing formats as needed based on IAHRS output
}

float calculateSpineCurvature() {
  // Calculate spine curvature between upper and lower sensors
  float pitch_diff = sensor1_data.pitch - sensor2_data.pitch;
  float roll_diff = sensor1_data.roll - sensor2_data.roll;
  
  // Combined curvature magnitude
  float curvature = sqrt(pitch_diff * pitch_diff + roll_diff * roll_diff);
  
  return curvature;
}

String evaluatePosture(float curvature) {
  if (curvature < 5.0) {
    return "GOOD";
  } else if (curvature < 10.0) {
    return "FAIR";
  } else if (curvature < 15.0) {
    return "POOR";
  } else {
    return "BAD";
  }
}
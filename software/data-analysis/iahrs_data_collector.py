"""
IAHRS Sensor Data Collector
Real-time data collection from IAHRS intellithings sensor via USB
"""

import serial
import csv
import time
from datetime import datetime

# Serial port configuration
PORT = 'COM3'  # IAHRS sensor port
BAUDRATE = 115200
OUTPUT_FILE = 'iahrs_posture_data.csv'

def collect_data():
    print("IAHRS Sensor Data Collector")
    print(f"Connecting to {PORT} at {BAUDRATE} baud...")
    
    try:
        # Open serial connection
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        time.sleep(2)  # Wait for connection
        
        print(f"✓ Connected! Saving data to {OUTPUT_FILE}")
        print("Press Ctrl+C to stop\n")
        
        # Open CSV file
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['timestamp', 'datetime', 'sensor_data'])
            
            # Collect data
            while True:
                if ser.in_waiting > 0:
                    # Read line from sensor
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    if line:  # Skip empty lines
                        timestamp = time.time()
                        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                        
                        # Save to CSV
                        writer.writerow([timestamp, dt, line])
                        
                        # Print to console
                        print(f"[{dt}] {line}")
                        
                        # Flush to ensure data is written
                        f.flush()
                
                time.sleep(0.01)  # 10ms delay
                
    except serial.SerialException as e:
        print(f"Error: Could not open port {PORT}")
        print(f"Details: {e}")
        print("\nMake sure:")
        print("1. IAHRS sensor is connected via USB")
        print("2. Correct COM port (check Device Manager)")
        print("3. Serial Monitor is closed")
        
    except KeyboardInterrupt:
        print("\n\nData collection stopped by user")
        print(f"Data saved to: {OUTPUT_FILE}")
        
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed")

if __name__ == "__main__":
    collect_data()

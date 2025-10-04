"""
Smart Posture Tracker - Sensor Data Collector

This script collects data from the MPU6050 sensor via serial communication
and provides real-time analysis and visualization capabilities.

Requirements:
- pyserial
- pandas
- matplotlib
- numpy

Install with: pip install pyserial pandas matplotlib numpy
"""

import serial
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import time
import csv
from collections import deque
import threading
import os

class MPU6050DataCollector:
    def __init__(self, port='COM3', baudrate=115200, buffer_size=1000):
        """
        Initialize the MPU6050 data collector
        
        Args:
            port (str): Serial port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
            baudrate (int): Serial communication speed
            buffer_size (int): Maximum number of data points to keep in memory
        """
        self.port = port
        self.baudrate = baudrate
        self.buffer_size = buffer_size
        self.serial_connection = None
        self.is_collecting = False
        
        # Data storage
        self.data_buffer = deque(maxlen=buffer_size)
        self.csv_filename = None
        
        # Column names for CSV data
        self.columns = ['timestamp', 'accel_x', 'accel_y', 'accel_z', 
                       'gyro_x', 'gyro_y', 'gyro_z', 'temperature']    def connect_serial(self):
        """Establish serial connection to Arduino"""
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            print(f"Connected to {self.port} at {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to {self.port}: {e}")
            return False
    
    def disconnect_serial(self):
        """Close serial connection"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Serial connection closed")
    
    def start_collection(self, duration_seconds=None, save_to_csv=True):
        """
        Start collecting sensor data
        
        Args:
            duration_seconds (int): How long to collect data (None = indefinite)
            save_to_csv (bool): Whether to save data to CSV file
        """
        if not self.connect_serial():
            return
        
        if save_to_csv:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.csv_filename = f"sensor_data_{timestamp}.csv"
            
        self.is_collecting = True
        start_time = time.time()
        
        print("Starting data collection...")
        print("Press Ctrl+C to stop collection")
        
        try:
            with open(self.csv_filename, 'w', newline='') if save_to_csv else open(os.devnull, 'w') as csvfile:
                if save_to_csv:
                    writer = csv.writer(csvfile)
                    writer.writerow(self.columns)  # Write header
                
                while self.is_collecting:
                    if duration_seconds and (time.time() - start_time > duration_seconds):
                        break
                    
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    
                    # Skip header lines and empty lines
                    if line and not line.startswith('Smart') and not line.startswith('=') and not line.startswith('MPU') and not line.startswith('CSV'):
                        try:
                            # Parse CSV data
                            data = [float(x) for x in line.split(',')]
                            if len(data) == 8:  # Ensure we have all expected columns
                                self.data_buffer.append(data)
                                
                                if save_to_csv:
                                    writer.writerow(data)
                                    csvfile.flush()  # Ensure data is written immediately
                                
                                # Print progress every 50 samples
                                if len(self.data_buffer) % 50 == 0:
                                    print(f"Collected {len(self.data_buffer)} samples...")
                        
                        except ValueError:
                            # Skip invalid data lines
                            continue
                            
        except KeyboardInterrupt:
            print("\nData collection stopped by user")
        except Exception as e:
            print(f"Error during data collection: {e}")
        finally:
            self.is_collecting = False
            self.disconnect_serial()
            
            if save_to_csv:
                print(f"Data saved to: {self.csv_filename}")
                print(f"Total samples collected: {len(self.data_buffer)}")
    
    def get_dataframe(self):
        """Convert collected data to pandas DataFrame"""
        if not self.data_buffer:
            print("No data collected yet")
            return None
            
        df = pd.DataFrame(list(self.data_buffer), columns=self.columns)
        
        # Convert timestamp to datetime
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        return df    def analyze_posture(self, window_size=50):
        """
        Perform basic posture analysis on collected data
        
        Args:
            window_size (int): Number of samples for moving average
        """
        df = self.get_dataframe()
        if df is None:
            return
        
        print("=== Posture Analysis Report ===")
        print(f"Analysis period: {df['datetime'].min()} to {df['datetime'].max()}")
        print(f"Total samples: {len(df)}")
        print(f"Duration: {(df['timestamp'].max() - df['timestamp'].min()) / 1000:.1f} seconds")
        print()
        
        # Calculate basic statistics
        print("Accelerometer Statistics (m/s²):")
        for axis in ['accel_x', 'accel_y', 'accel_z']:
            mean_val = df[axis].mean()
            std_val = df[axis].std()
            print(f"  {axis}: mean={mean_val:.3f}, std={std_val:.3f}")
        print()
        
        print("Gyroscope Statistics (rad/s):")
        for axis in ['gyro_x', 'gyro_y', 'gyro_z']:
            mean_val = df[axis].mean()
            std_val = df[axis].std()
            print(f"  {axis}: mean={mean_val:.3f}, std={std_val:.3f}")
        print()
        
        # Calculate approximate orientation
        # Simple tilt calculation using accelerometer
        df['pitch'] = np.arctan2(-df['accel_x'], np.sqrt(df['accel_y']**2 + df['accel_z']**2)) * 180 / np.pi
        df['roll'] = np.arctan2(df['accel_y'], df['accel_z']) * 180 / np.pi
        
        print("Orientation Statistics (degrees):")
        print(f"  Pitch: mean={df['pitch'].mean():.1f}°, std={df['pitch'].std():.1f}°")
        print(f"  Roll: mean={df['roll'].mean():.1f}°, std={df['roll'].std():.1f}°")
        print()
        
        # Detect potential posture issues
        forward_lean_threshold = 15  # degrees
        side_lean_threshold = 10    # degrees
        
        forward_lean = (df['pitch'] > forward_lean_threshold).sum()
        side_lean = (abs(df['roll']) > side_lean_threshold).sum()
        
        print("=== Posture Alerts ===")
        if forward_lean > len(df) * 0.1:  # More than 10% of time
            print(f"⚠️  Forward head posture detected: {forward_lean/len(df)*100:.1f}% of time")
        
        if side_lean > len(df) * 0.1:
            print(f"⚠️  Side lean detected: {side_lean/len(df)*100:.1f}% of time")
        
        if forward_lean <= len(df) * 0.1 and side_lean <= len(df) * 0.1:
            print("✅ Good posture maintained!")
        
        return df    def plot_realtime_data(self, plot_duration=30):
        """
        Create real-time plots of sensor data
        
        Args:
            plot_duration (int): How long to show each plot (seconds)
        """
        df = self.get_dataframe()
        if df is None:
            return
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('MPU6050 Sensor Data Analysis')
        
        # Accelerometer data
        axes[0, 0].plot(df['datetime'], df['accel_x'], label='X-axis', alpha=0.7)
        axes[0, 0].plot(df['datetime'], df['accel_y'], label='Y-axis', alpha=0.7)
        axes[0, 0].plot(df['datetime'], df['accel_z'], label='Z-axis', alpha=0.7)
        axes[0, 0].set_title('Accelerometer (m/s²)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Gyroscope data
        axes[0, 1].plot(df['datetime'], df['gyro_x'], label='X-axis', alpha=0.7)
        axes[0, 1].plot(df['datetime'], df['gyro_y'], label='Y-axis', alpha=0.7)
        axes[0, 1].plot(df['datetime'], df['gyro_z'], label='Z-axis', alpha=0.7)
        axes[0, 1].set_title('Gyroscope (rad/s)')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Temperature
        axes[1, 0].plot(df['datetime'], df['temperature'], color='red', alpha=0.7)
        axes[1, 0].set_title('Temperature (°C)')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Orientation (if calculated)
        if 'pitch' in df.columns and 'roll' in df.columns:
            axes[1, 1].plot(df['datetime'], df['pitch'], label='Pitch', alpha=0.7)
            axes[1, 1].plot(df['datetime'], df['roll'], label='Roll', alpha=0.7)
            axes[1, 1].axhline(y=15, color='red', linestyle='--', alpha=0.5, label='Forward lean threshold')
            axes[1, 1].axhline(y=-15, color='red', linestyle='--', alpha=0.5)
            axes[1, 1].axhline(y=10, color='orange', linestyle='--', alpha=0.5, label='Side lean threshold')
            axes[1, 1].axhline(y=-10, color='orange', linestyle='--', alpha=0.5)
            axes[1, 1].set_title('Orientation (degrees)')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_filename = f"sensor_plot_{timestamp}.png"
        fig.savefig(plot_filename, dpi=300, bbox_inches='tight')
        print(f"Plot saved as: {plot_filename}")

def main():
    """Main function for testing the data collector"""
    print("Smart Posture Tracker - Data Collector")
    print("=====================================")
    print()
    print("Available COM ports:")
    
    # List available serial ports
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"  {port.device}: {port.description}")
    
    if not ports:
        print("  No serial ports found")
        return
    
    # Get user input for port selection
    port = input(f"\nEnter COM port (default: COM3): ").strip() or "COM3"
    duration = input("Collection duration in seconds (Enter for indefinite): ").strip()
    duration = int(duration) if duration else None
    
    # Create collector and start collection
    collector = MPU6050DataCollector(port=port)
    
    try:
        collector.start_collection(duration_seconds=duration, save_to_csv=True)
        
        # Perform analysis if data was collected
        if collector.data_buffer:
            df = collector.analyze_posture()
            
            # Ask user if they want to see plots
            show_plots = input("\nShow plots? (y/n): ").strip().lower() == 'y'
            if show_plots:
                collector.plot_realtime_data()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
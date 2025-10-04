"""
Smart Posture Tracker - Dual Sensor Data Analyzer

Advanced posture analysis using two MPU6050 sensors:
- Sensor 1: Upper spine/neck tracking (T1-T3 vertebrae)
- Sensor 2: Mid spine tracking (T7-T9 vertebrae)

This provides much more accurate posture detection by measuring
spine curvature and relative movement between spine segments.

Requirements:
- pyserial, pandas, matplotlib, numpy, scipy
"""

import serial
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import time
import csv
from collections import deque
import os
from scipy.signal import butter, filtfilt
from scipy.spatial.transform import Rotation

class DualMPU6050Analyzer:
    def __init__(self, port='COM3', baudrate=115200, buffer_size=2000):
        """
        Initialize dual sensor analyzer
        
        Args:
            port (str): Serial port
            baudrate (int): Serial speed
            buffer_size (int): Data buffer size
        """
        self.port = port
        self.baudrate = baudrate
        self.buffer_size = buffer_size
        self.serial_connection = None
        self.is_collecting = False
        
        # Data storage
        self.data_buffer = deque(maxlen=buffer_size)
        self.csv_filename = None
        
        # Dual sensor column names
        self.columns = [
            'timestamp', 
            's1_accel_x', 's1_accel_y', 's1_accel_z',  # Upper spine sensor
            's1_gyro_x', 's1_gyro_y', 's1_gyro_z', 's1_temp',
            's2_accel_x', 's2_accel_y', 's2_accel_z',  # Mid spine sensor  
            's2_gyro_x', 's2_gyro_y', 's2_gyro_z', 's2_temp'
        ]    def connect_serial(self):
        """Establish serial connection"""
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)
            print(f"Connected to {self.port} at {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to {self.port}: {e}")
            return False
    
    def start_collection(self, duration_seconds=None, save_to_csv=True):
        """Start dual sensor data collection"""
        if not self.connect_serial():
            return
        
        if save_to_csv:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.csv_filename = f"dual_sensor_data_{timestamp}.csv"
            
        self.is_collecting = True
        start_time = time.time()
        
        print("Starting dual sensor data collection...")
        print("Press Ctrl+C to stop collection")
        
        try:
            with open(self.csv_filename, 'w', newline='') if save_to_csv else open(os.devnull, 'w') as csvfile:
                if save_to_csv:
                    writer = csv.writer(csvfile)
                    writer.writerow(self.columns)
                
                while self.is_collecting:
                    if duration_seconds and (time.time() - start_time > duration_seconds):
                        break
                    
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    
                    if line and not line.startswith(('Smart', '=', 'MPU', 'CSV', 'Sensor', 'Calibrating')):
                        try:
                            data = [float(x) for x in line.split(',')]
                            if len(data) == 15:  # timestamp + 14 sensor values
                                self.data_buffer.append(data)
                                
                                if save_to_csv:
                                    writer.writerow(data)
                                    csvfile.flush()
                                
                                if len(self.data_buffer) % 100 == 0:
                                    print(f"Collected {len(self.data_buffer)} dual sensor samples...")
                        
                        except ValueError:
                            continue
                            
        except KeyboardInterrupt:
            print("\nDual sensor data collection stopped")
        except Exception as e:
            print(f"Error during collection: {e}")
        finally:
            self.is_collecting = False
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
            
            if save_to_csv:
                print(f"Dual sensor data saved to: {self.csv_filename}")
                print(f"Total samples collected: {len(self.data_buffer)}")
    
    def get_dataframe(self):
        """Convert dual sensor data to DataFrame"""
        if not self.data_buffer:
            print("No dual sensor data collected")
            return None
            
        df = pd.DataFrame(list(self.data_buffer), columns=self.columns)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        return df    def calculate_spine_curvature(self, df):
        """Calculate spine curvature between two sensors"""
        # Calculate orientation for each sensor
        # Upper sensor (neck/upper spine)
        df['s1_pitch'] = np.arctan2(-df['s1_accel_x'], 
                                   np.sqrt(df['s1_accel_y']**2 + df['s1_accel_z']**2)) * 180/np.pi
        df['s1_roll'] = np.arctan2(df['s1_accel_y'], df['s1_accel_z']) * 180/np.pi
        
        # Mid sensor (thoracic spine)
        df['s2_pitch'] = np.arctan2(-df['s2_accel_x'],
                                   np.sqrt(df['s2_accel_y']**2 + df['s2_accel_z']**2)) * 180/np.pi
        df['s2_roll'] = np.arctan2(df['s2_accel_y'], df['s2_accel_z']) * 180/np.pi
        
        # Calculate relative angles (spine curvature)
        df['spine_curvature_pitch'] = df['s1_pitch'] - df['s2_pitch']  # Forward bend
        df['spine_curvature_roll'] = df['s1_roll'] - df['s2_roll']     # Side bend
        
        # Calculate spine flexibility/movement
        df['spine_movement'] = np.sqrt(df['spine_curvature_pitch']**2 + df['spine_curvature_roll']**2)
        
        return df
    
    def analyze_advanced_posture(self, window_size=50):
        """Advanced posture analysis using dual sensors"""
        df = self.get_dataframe()
        if df is None:
            return
        
        # Calculate spine curvature
        df = self.calculate_spine_curvature(df)
        
        print("=== Advanced Dual Sensor Posture Analysis ===")
        print(f"Analysis period: {df['datetime'].min()} to {df['datetime'].max()}")
        print(f"Total samples: {len(df)}")
        print(f"Duration: {(df['timestamp'].max() - df['timestamp'].min()) / 1000:.1f} seconds")
        print()
        
        # Upper spine analysis
        print("Upper Spine/Neck Sensor Statistics:")
        print(f"  Pitch (forward/back): mean={df['s1_pitch'].mean():.1f}°, std={df['s1_pitch'].std():.1f}°")
        print(f"  Roll (left/right): mean={df['s1_roll'].mean():.1f}°, std={df['s1_roll'].std():.1f}°")
        print()
        
        # Mid spine analysis  
        print("Mid Spine Sensor Statistics:")
        print(f"  Pitch (forward/back): mean={df['s2_pitch'].mean():.1f}°, std={df['s2_pitch'].std():.1f}°")
        print(f"  Roll (left/right): mean={df['s2_roll'].mean():.1f}°, std={df['s2_roll'].std():.1f}°")
        print()
        
        # Spine curvature analysis
        print("Spine Curvature Analysis:")
        print(f"  Forward curvature: mean={df['spine_curvature_pitch'].mean():.1f}°, std={df['spine_curvature_pitch'].std():.1f}°")
        print(f"  Side curvature: mean={df['spine_curvature_roll'].mean():.1f}°, std={df['spine_curvature_roll'].std():.1f}°")
        print(f"  Overall spine movement: mean={df['spine_movement'].mean():.1f}°, std={df['spine_movement'].std():.1f}°")
        print()
        
        # Advanced posture detection
        self.detect_posture_patterns(df)
        
        return df
    
    def detect_posture_patterns(self, df):
        """Detect specific posture patterns using dual sensors"""
        print("=== Advanced Posture Pattern Detection ===")
        
        # Thresholds for different posture issues
        forward_head_threshold = 15      # Upper sensor forward lean
        hunched_shoulders_threshold = 20 # Curvature difference
        side_lean_threshold = 10         # Side curvature
        excessive_movement_threshold = 5  # Too much fidgeting
        
        total_samples = len(df)
        
        # 1. Forward Head Posture (텀블목)
        forward_head = (df['s1_pitch'] > forward_head_threshold).sum()
        forward_head_pct = (forward_head / total_samples) * 100
        
        # 2. Hunched Shoulders (굽은 어깨)
        hunched = (df['spine_curvature_pitch'] > hunched_shoulders_threshold).sum()
        hunched_pct = (hunched / total_samples) * 100
        
        # 3. Side Lean (측면 기울임)
        side_lean = (abs(df['spine_curvature_roll']) > side_lean_threshold).sum()
        side_lean_pct = (side_lean / total_samples) * 100
        
        # 4. Excessive Movement (과도한 움직임)
        excessive_move = (df['spine_movement'] > excessive_movement_threshold).sum()
        excessive_move_pct = (excessive_move / total_samples) * 100
        
        # 5. Good Posture (좋은 자세)
        good_posture = total_samples - max(forward_head, hunched, side_lean)
        good_posture_pct = max(0, (good_posture / total_samples) * 100)
        
        # Report findings
        if forward_head_pct > 10:
            print(f"⚠️  Forward Head Posture: {forward_head_pct:.1f}% of time")
            print("   └─ Recommendation: Keep monitor at eye level, strengthen neck muscles")
            
        if hunched_pct > 10:
            print(f"⚠️  Hunched Shoulders: {hunched_pct:.1f}% of time")
            print("   └─ Recommendation: Shoulder blade squeezes, chest stretches")
            
        if side_lean_pct > 10:
            print(f"⚠️  Side Lean: {side_lean_pct:.1f}% of time")
            print("   └─ Recommendation: Check chair height, core strengthening")
            
        if excessive_move_pct > 30:
            print(f"💡 High Movement: {excessive_move_pct:.1f}% of time")
            print("   └─ This can be good (avoiding static posture) or indicate discomfort")
            
        if good_posture_pct > 70:
            print(f"✅ Excellent Posture: {good_posture_pct:.1f}% of time")
        elif good_posture_pct > 50:
            print(f"✅ Good Posture: {good_posture_pct:.1f}% of time")
        else:
            print(f"⚠️  Posture needs improvement: Only {good_posture_pct:.1f}% good posture")
        
        print()
        
        # Posture score calculation
        posture_score = max(0, 100 - (forward_head_pct + hunched_pct + side_lean_pct) / 3)
        print(f"📊 Overall Posture Score: {posture_score:.1f}/100")
        
        if posture_score >= 80:
            print("   Grade: A (Excellent)")
        elif posture_score >= 70:
            print("   Grade: B (Good)")
        elif posture_score >= 60:
            print("   Grade: C (Fair - needs improvement)")
        else:
            print("   Grade: D (Poor - significant improvement needed)")
        
        return {
            'forward_head_pct': forward_head_pct,
            'hunched_pct': hunched_pct,
            'side_lean_pct': side_lean_pct,
            'good_posture_pct': good_posture_pct,
            'posture_score': posture_score
        }    def plot_dual_sensor_data(self):
        """Create comprehensive dual sensor visualization"""
        df = self.get_dataframe()
        if df is None:
            return
        
        # Calculate spine curvature if not already done
        if 'spine_curvature_pitch' not in df.columns:
            df = self.calculate_spine_curvature(df)
        
        # Create comprehensive visualization
        fig, axes = plt.subplots(3, 2, figsize=(16, 12))
        fig.suptitle('Dual Sensor Posture Analysis Dashboard', fontsize=16)
        
        # 1. Upper Spine Accelerometer
        axes[0, 0].plot(df['datetime'], df['s1_accel_x'], label='X (forward/back)', alpha=0.7)
        axes[0, 0].plot(df['datetime'], df['s1_accel_y'], label='Y (left/right)', alpha=0.7)
        axes[0, 0].plot(df['datetime'], df['s1_accel_z'], label='Z (up/down)', alpha=0.7)
        axes[0, 0].set_title('Upper Spine - Accelerometer (m/s²)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Mid Spine Accelerometer
        axes[0, 1].plot(df['datetime'], df['s2_accel_x'], label='X (forward/back)', alpha=0.7)
        axes[0, 1].plot(df['datetime'], df['s2_accel_y'], label='Y (left/right)', alpha=0.7)
        axes[0, 1].plot(df['datetime'], df['s2_accel_z'], label='Z (up/down)', alpha=0.7)
        axes[0, 1].set_title('Mid Spine - Accelerometer (m/s²)')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Spine Orientation Comparison
        axes[1, 0].plot(df['datetime'], df['s1_pitch'], label='Upper Spine Pitch', alpha=0.8)
        axes[1, 0].plot(df['datetime'], df['s2_pitch'], label='Mid Spine Pitch', alpha=0.8)
        axes[1, 0].axhline(y=15, color='red', linestyle='--', alpha=0.5, label='Forward lean threshold')
        axes[1, 0].set_title('Spine Pitch Comparison (degrees)')
        axes[1, 0].set_ylabel('Pitch (degrees)')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Spine Curvature Analysis
        axes[1, 1].plot(df['datetime'], df['spine_curvature_pitch'], 
                       label='Forward Curvature', color='red', alpha=0.8)
        axes[1, 1].plot(df['datetime'], df['spine_curvature_roll'], 
                       label='Side Curvature', color='blue', alpha=0.8)
        axes[1, 1].axhline(y=20, color='red', linestyle='--', alpha=0.5, label='Hunched threshold')
        axes[1, 1].axhline(y=10, color='blue', linestyle='--', alpha=0.5, label='Side lean threshold')
        axes[1, 1].axhline(y=-10, color='blue', linestyle='--', alpha=0.5)
        axes[1, 1].set_title('Spine Curvature (degrees)')
        axes[1, 1].set_ylabel('Curvature (degrees)')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        # 5. Movement Analysis
        axes[2, 0].plot(df['datetime'], df['spine_movement'], 
                       color='purple', alpha=0.8, label='Spine Movement')
        axes[2, 0].axhline(y=5, color='orange', linestyle='--', alpha=0.5, 
                          label='High movement threshold')
        axes[2, 0].set_title('Spine Movement Intensity')
        axes[2, 0].set_ylabel('Movement (degrees)')
        axes[2, 0].legend()
        axes[2, 0].grid(True, alpha=0.3)
        
        # 6. Temperature Monitoring
        axes[2, 1].plot(df['datetime'], df['s1_temp'], label='Upper Sensor', alpha=0.8)
        axes[2, 1].plot(df['datetime'], df['s2_temp'], label='Mid Sensor', alpha=0.8)
        axes[2, 1].set_title('Sensor Temperature (°C)')
        axes[2, 1].set_ylabel('Temperature (°C)')
        axes[2, 1].legend()
        axes[2, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_filename = f"dual_sensor_analysis_{timestamp}.png"
        fig.savefig(plot_filename, dpi=300, bbox_inches='tight')
        print(f"Dual sensor analysis plot saved: {plot_filename}")

def main():
    """Main function for dual sensor testing"""
    print("Smart Posture Tracker - Dual Sensor Analysis")
    print("============================================")
    print()
    
    # List available ports
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    print("Available COM ports:")
    for port in ports:
        print(f"  {port.device}: {port.description}")
    
    if not ports:
        print("  No serial ports found")
        return
    
    # Get user input
    port = input(f"\nEnter COM port (default: COM3): ").strip() or "COM3"
    duration = input("Collection duration in seconds (Enter for indefinite): ").strip()
    duration = int(duration) if duration else None
    
    # Create dual sensor analyzer
    analyzer = DualMPU6050Analyzer(port=port)
    
    try:
        print("\nMake sure both sensors are properly connected:")
        print("- Sensor 1 (Upper): AD0 = LOW (default 0x68)")
        print("- Sensor 2 (Mid): AD0 = HIGH (connect to 3.3V for 0x69)")
        print("- Both sensors share SDA, SCL, VCC, GND connections")
        input("\nPress Enter when ready...")
        
        analyzer.start_collection(duration_seconds=duration, save_to_csv=True)
        
        if analyzer.data_buffer:
            df = analyzer.analyze_advanced_posture()
            
            show_plots = input("\nShow dual sensor analysis plots? (y/n): ").strip().lower() == 'y'
            if show_plots:
                analyzer.plot_dual_sensor_data()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
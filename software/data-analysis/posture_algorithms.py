"""
Smart Posture Tracker - Advanced Posture Analysis Algorithms

This module implements sophisticated algorithms for posture analysis:
1. Data preprocessing and noise filtering
2. Feature extraction from dual sensors
3. Real-time posture classification
4. Pattern recognition and trend analysis
5. Intelligent feedback generation

Author: Smart Posture Tracker Team
Version: 1.0
"""

import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, savgol_filter
from scipy.spatial.transform import Rotation
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from collections import deque
import warnings
warnings.filterwarnings('ignore')

class PostureAlgorithms:
    def __init__(self, sample_rate=10, window_size=50):
        """
        Initialize posture analysis algorithms
        
        Args:
            sample_rate (int): Data sampling rate in Hz
            window_size (int): Moving window size for analysis
        """
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.dt = 1.0 / sample_rate
        
        # Algorithm parameters
        self.filter_params = {
            'lowpass_cutoff': 3.0,  # Hz - Remove high frequency noise
            'order': 4
        }
        
        # Posture thresholds (degrees)
        self.thresholds = {
            'forward_head_mild': 10,
            'forward_head_severe': 20,
            'hunched_shoulders_mild': 15,
            'hunched_shoulders_severe': 25,
            'side_lean_mild': 8,
            'side_lean_severe': 15,
            'movement_threshold': 3,
            'stability_threshold': 2
        }
        
        # Feature extraction parameters
        self.feature_window = 30  # seconds for feature calculation
        
        # Machine learning model (will be trained)
        self.ml_model = None
        self.scaler = StandardScaler()
        self.is_trained = False    def preprocess_data(self, df):
        """
        Level 1: Raw Data Processing
        - Remove noise and outliers
        - Apply low-pass filtering
        - Handle missing data
        """
        df_clean = df.copy()
        
        # 1. Remove outliers (3-sigma rule)
        for col in ['s1_accel_x', 's1_accel_y', 's1_accel_z', 
                   's2_accel_x', 's2_accel_y', 's2_accel_z']:
            mean = df_clean[col].mean()
            std = df_clean[col].std()
            outlier_mask = np.abs(df_clean[col] - mean) > 3 * std
            df_clean.loc[outlier_mask, col] = mean
        
        # 2. Apply low-pass filter to remove high-frequency noise
        nyquist = self.sample_rate / 2
        if self.filter_params['lowpass_cutoff'] < nyquist:
            b, a = butter(self.filter_params['order'], 
                         self.filter_params['lowpass_cutoff'] / nyquist, 
                         btype='low')
            
            for col in ['s1_accel_x', 's1_accel_y', 's1_accel_z',
                       's1_gyro_x', 's1_gyro_y', 's1_gyro_z',
                       's2_accel_x', 's2_accel_y', 's2_accel_z',
                       's2_gyro_x', 's2_gyro_y', 's2_gyro_z']:
                if len(df_clean) > 2 * self.filter_params['order']:
                    df_clean[col] = filtfilt(b, a, df_clean[col])
        
        # 3. Smooth gyroscope data (more sensitive to noise)
        if len(df_clean) >= 5:
            for col in ['s1_gyro_x', 's1_gyro_y', 's1_gyro_z',
                       's2_gyro_x', 's2_gyro_y', 's2_gyro_z']:
                df_clean[col] = savgol_filter(df_clean[col], 
                                            window_length=min(5, len(df_clean)), 
                                            polyorder=2)
        
        return df_clean
    
    def extract_orientation(self, df):
        """
        Level 2: Feature Extraction - Calculate orientation angles
        """
        df_oriented = df.copy()
        
        # Calculate pitch and roll for both sensors using accelerometer
        # Sensor 1 (Upper spine/neck)
        df_oriented['s1_pitch'] = np.arctan2(
            -df_oriented['s1_accel_x'],
            np.sqrt(df_oriented['s1_accel_y']**2 + df_oriented['s1_accel_z']**2)
        ) * 180 / np.pi
        
        df_oriented['s1_roll'] = np.arctan2(
            df_oriented['s1_accel_y'],
            df_oriented['s1_accel_z']
        ) * 180 / np.pi
        
        # Sensor 2 (Mid spine) 
        df_oriented['s2_pitch'] = np.arctan2(
            -df_oriented['s2_accel_x'],
            np.sqrt(df_oriented['s2_accel_y']**2 + df_oriented['s2_accel_z']**2)
        ) * 180 / np.pi
        
        df_oriented['s2_roll'] = np.arctan2(
            df_oriented['s2_accel_y'],
            df_oriented['s2_accel_z']
        ) * 180 / np.pi
        
        # Calculate relative angles (spine curvature)
        df_oriented['spine_pitch_curvature'] = df_oriented['s1_pitch'] - df_oriented['s2_pitch']
        df_oriented['spine_roll_curvature'] = df_oriented['s1_roll'] - df_oriented['s2_roll']
        
        # Calculate total spine curvature magnitude
        df_oriented['spine_curvature_magnitude'] = np.sqrt(
            df_oriented['spine_pitch_curvature']**2 + 
            df_oriented['spine_roll_curvature']**2
        )
        
        return df_oriented    def extract_advanced_features(self, df):
        """
        Level 2: Advanced Feature Extraction
        - Statistical features over time windows
        - Movement patterns and dynamics
        - Frequency domain analysis
        """
        df_features = df.copy()
        
        # Rolling window statistics (30-second windows)
        window_samples = min(self.feature_window * self.sample_rate, len(df))
        
        if window_samples >= 10:
            # 1. Movement variability (standard deviation over time)
            df_features['s1_movement_variability'] = df['s1_pitch'].rolling(
                window=window_samples, min_periods=5).std().fillna(0)
            df_features['s2_movement_variability'] = df['s2_pitch'].rolling(
                window=window_samples, min_periods=5).std().fillna(0)
            
            # 2. Posture stability (how much the spine curvature changes)
            df_features['spine_stability'] = df['spine_curvature_magnitude'].rolling(
                window=window_samples, min_periods=5).std().fillna(0)
            
            # 3. Movement velocity (rate of change)
            df_features['s1_pitch_velocity'] = df['s1_pitch'].diff().rolling(
                window=5, min_periods=2).mean().fillna(0)
            df_features['s2_pitch_velocity'] = df['s2_pitch'].diff().rolling(
                window=5, min_periods=2).mean().fillna(0)
            
            # 4. Movement acceleration (second derivative)
            df_features['s1_pitch_acceleration'] = df_features['s1_pitch_velocity'].diff().fillna(0)
            df_features['s2_pitch_acceleration'] = df_features['s2_pitch_velocity'].diff().fillna(0)
            
            # 5. Gyroscope integration for dynamic movement
            df_features['s1_cumulative_rotation'] = np.cumsum(np.abs(df['s1_gyro_x']) + 
                                                             np.abs(df['s1_gyro_y']) + 
                                                             np.abs(df['s1_gyro_z'])) * self.dt
            df_features['s2_cumulative_rotation'] = np.cumsum(np.abs(df['s2_gyro_x']) + 
                                                             np.abs(df['s2_gyro_y']) + 
                                                             np.abs(df['s2_gyro_z'])) * self.dt
        else:
            # Fill with zeros if not enough data
            for col in ['s1_movement_variability', 's2_movement_variability', 
                       'spine_stability', 's1_pitch_velocity', 's2_pitch_velocity',
                       's1_pitch_acceleration', 's2_pitch_acceleration',
                       's1_cumulative_rotation', 's2_cumulative_rotation']:
                df_features[col] = 0
        
        return df_features
    
    def classify_posture_realtime(self, df):
        """
        Level 3: Real-time Posture Classification
        Rule-based classification for immediate feedback
        """
        df_classified = df.copy()
        
        # Initialize posture labels
        df_classified['posture_label'] = 'unknown'
        df_classified['severity_score'] = 0
        df_classified['confidence'] = 0
        
        # Rule-based classification
        for i in range(len(df_classified)):
            posture_issues = []
            severity = 0
            
            # 1. Forward Head Posture Detection
            if df_classified.iloc[i]['s1_pitch'] > self.thresholds['forward_head_severe']:
                posture_issues.append('severe_forward_head')
                severity += 3
            elif df_classified.iloc[i]['s1_pitch'] > self.thresholds['forward_head_mild']:
                posture_issues.append('mild_forward_head')
                severity += 1
            
            # 2. Hunched Shoulders Detection
            if df_classified.iloc[i]['spine_pitch_curvature'] > self.thresholds['hunched_shoulders_severe']:
                posture_issues.append('severe_hunched')
                severity += 3
            elif df_classified.iloc[i]['spine_pitch_curvature'] > self.thresholds['hunched_shoulders_mild']:
                posture_issues.append('mild_hunched')
                severity += 1
            
            # 3. Side Lean Detection
            if abs(df_classified.iloc[i]['spine_roll_curvature']) > self.thresholds['side_lean_severe']:
                posture_issues.append('severe_side_lean')
                severity += 2
            elif abs(df_classified.iloc[i]['spine_roll_curvature']) > self.thresholds['side_lean_mild']:
                posture_issues.append('mild_side_lean')
                severity += 1
            
            # 4. Movement Analysis
            if 'spine_stability' in df_classified.columns:
                if df_classified.iloc[i]['spine_stability'] > self.thresholds['movement_threshold']:
                    posture_issues.append('excessive_movement')
                elif df_classified.iloc[i]['spine_stability'] < self.thresholds['stability_threshold']:
                    posture_issues.append('static_posture')
            
            # Determine primary posture label
            if not posture_issues:
                df_classified.iloc[i, df_classified.columns.get_loc('posture_label')] = 'good_posture'
                df_classified.iloc[i, df_classified.columns.get_loc('confidence')] = 0.9
            elif len(posture_issues) == 1:
                df_classified.iloc[i, df_classified.columns.get_loc('posture_label')] = posture_issues[0]
                df_classified.iloc[i, df_classified.columns.get_loc('confidence')] = 0.8
            else:
                df_classified.iloc[i, df_classified.columns.get_loc('posture_label')] = 'multiple_issues'
                df_classified.iloc[i, df_classified.columns.get_loc('confidence')] = 0.7
            
            df_classified.iloc[i, df_classified.columns.get_loc('severity_score')] = min(severity, 10)
        
        return df_classified    def analyze_patterns(self, df, analysis_window_minutes=5):
        """
        Level 4: Pattern Recognition and Trend Analysis
        Analyze posture patterns over longer time periods
        """
        if len(df) < self.sample_rate * 60:  # Less than 1 minute of data
            return {
                'pattern_analysis': 'insufficient_data',
                'trends': {},
                'recommendations': ['Collect more data for pattern analysis']
            }
        
        analysis_samples = min(analysis_window_minutes * 60 * self.sample_rate, len(df))
        recent_data = df.tail(analysis_samples).copy()
        
        analysis_results = {
            'time_period': f'{len(recent_data) / self.sample_rate / 60:.1f} minutes',
            'total_samples': len(recent_data),
        }
        
        # 1. Posture Distribution Analysis
        if 'posture_label' in recent_data.columns:
            posture_counts = recent_data['posture_label'].value_counts()
            total_samples = len(recent_data)
            
            posture_percentages = {}
            for posture, count in posture_counts.items():
                posture_percentages[posture] = (count / total_samples) * 100
            
            analysis_results['posture_distribution'] = posture_percentages
        
        # 2. Trend Analysis
        trends = {}
        
        # Forward head posture trend
        if 's1_pitch' in recent_data.columns:
            fh_trend = np.polyfit(range(len(recent_data)), recent_data['s1_pitch'], 1)[0]
            trends['forward_head_trend'] = 'improving' if fh_trend < -0.01 else 'worsening' if fh_trend > 0.01 else 'stable'
        
        # Spine curvature trend  
        if 'spine_curvature_magnitude' in recent_data.columns:
            curve_trend = np.polyfit(range(len(recent_data)), recent_data['spine_curvature_magnitude'], 1)[0]
            trends['spine_curvature_trend'] = 'improving' if curve_trend < -0.01 else 'worsening' if curve_trend > 0.01 else 'stable'
        
        # Movement pattern analysis
        if 'spine_stability' in recent_data.columns:
            avg_movement = recent_data['spine_stability'].mean()
            if avg_movement > 4:
                trends['movement_pattern'] = 'highly_dynamic'
            elif avg_movement > 2:
                trends['movement_pattern'] = 'moderately_active'
            elif avg_movement < 0.5:
                trends['movement_pattern'] = 'too_static'
            else:
                trends['movement_pattern'] = 'optimal'
        
        analysis_results['trends'] = trends
        
        # 3. Generate Recommendations
        recommendations = self.generate_recommendations(analysis_results)
        analysis_results['recommendations'] = recommendations
        
        return analysis_results
    
    def generate_recommendations(self, analysis_results):
        """
        Level 5: Intelligent Feedback Generation
        Generate personalized recommendations based on analysis
        """
        recommendations = []
        
        if 'posture_distribution' not in analysis_results:
            return ['Continue monitoring for personalized recommendations']
        
        posture_dist = analysis_results['posture_distribution']
        trends = analysis_results.get('trends', {})
        
        # Forward Head Posture recommendations
        fh_issues = posture_dist.get('severe_forward_head', 0) + posture_dist.get('mild_forward_head', 0)
        if fh_issues > 30:
            recommendations.append("🚨 Forward Head Posture Alert: Adjust monitor height to eye level")
            recommendations.append("💪 Exercise: Chin tucks (10 reps every hour)")
            
            if trends.get('forward_head_trend') == 'worsening':
                recommendations.append("📈 Trend Alert: Forward head posture is getting worse - take immediate action!")
        
        # Hunched Shoulders recommendations
        hunched_issues = posture_dist.get('severe_hunched', 0) + posture_dist.get('mild_hunched', 0)
        if hunched_issues > 25:
            recommendations.append("🚨 Hunched Shoulders Detected: Focus on shoulder blade squeezes")
            recommendations.append("🧘 Stretching: Doorway chest stretch (30 seconds, 3 times)")
        
        # Side Lean recommendations  
        side_issues = posture_dist.get('severe_side_lean', 0) + posture_dist.get('mild_side_lean', 0)
        if side_issues > 20:
            recommendations.append("⚖️ Side Lean Detected: Check chair height and desk setup")
            recommendations.append("🏋️ Exercise: Side planks for core strengthening")
        
        # Movement recommendations
        movement_pattern = trends.get('movement_pattern', 'unknown')
        if movement_pattern == 'too_static':
            recommendations.append("🚶 Movement Alert: Take a 2-minute movement break every 30 minutes")
            recommendations.append("⏰ Set hourly reminders to change position")
        elif movement_pattern == 'highly_dynamic':
            recommendations.append("🎯 Consider if discomfort is causing excessive movement")
            recommendations.append("🪑 Check ergonomic setup - chair and desk height")
        
        # Overall posture score
        good_posture = posture_dist.get('good_posture', 0)
        if good_posture > 70:
            recommendations.append("✅ Excellent work! Maintain current habits")
        elif good_posture > 50:
            recommendations.append("👍 Good progress - minor adjustments needed")
        elif good_posture < 30:
            recommendations.append("⚠️ Significant improvement needed - consider ergonomic assessment")
        
        # Trend-based recommendations
        if trends.get('spine_curvature_trend') == 'improving':
            recommendations.append("📈 Great news! Your posture is improving over time")
        elif trends.get('spine_curvature_trend') == 'worsening':
            recommendations.append("📉 Warning: Posture declining - review workspace setup")
        
        return recommendations[:6]  # Limit to top 6 recommendations    def train_ml_model(self, training_data):
        """
        Train machine learning model for enhanced posture classification
        """
        print("Training machine learning model...")
        
        # Prepare features for ML
        feature_columns = [
            's1_pitch', 's1_roll', 's2_pitch', 's2_roll',
            'spine_pitch_curvature', 'spine_roll_curvature', 'spine_curvature_magnitude',
            's1_movement_variability', 's2_movement_variability', 'spine_stability'
        ]
        
        # Filter available columns
        available_features = [col for col in feature_columns if col in training_data.columns]
        
        if len(available_features) < 5:
            print(f"Warning: Only {len(available_features)} features available. ML training skipped.")
            return False
        
        X = training_data[available_features].fillna(0)
        y = training_data['posture_label'] if 'posture_label' in training_data.columns else None
        
        if y is None or len(X) < 100:
            print("Insufficient labeled training data. ML training skipped.")
            return False
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest model
        self.ml_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.ml_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.ml_model.score(X_train_scaled, y_train)
        test_score = self.ml_model.score(X_test_scaled, y_test)
        
        print(f"ML Model trained successfully!")
        print(f"Training accuracy: {train_score:.3f}")
        print(f"Testing accuracy: {test_score:.3f}")
        
        self.is_trained = True
        return True
    
    def predict_posture_ml(self, df):
        """
        Use trained ML model for posture prediction
        """
        if not self.is_trained or self.ml_model is None:
            return df
        
        feature_columns = [
            's1_pitch', 's1_roll', 's2_pitch', 's2_roll',
            'spine_pitch_curvature', 'spine_roll_curvature', 'spine_curvature_magnitude',
            's1_movement_variability', 's2_movement_variability', 'spine_stability'
        ]
        
        available_features = [col for col in feature_columns if col in df.columns]
        
        if len(available_features) < 5:
            return df
        
        X = df[available_features].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        df_ml = df.copy()
        df_ml['ml_prediction'] = self.ml_model.predict(X_scaled)
        df_ml['ml_confidence'] = np.max(self.ml_model.predict_proba(X_scaled), axis=1)
        
        return df_ml
    
    def process_complete_analysis(self, df):
        """
        Complete end-to-end posture analysis pipeline
        """
        print("🔄 Running complete posture analysis...")
        
        # Level 1: Preprocess data
        df_clean = self.preprocess_data(df)
        print(f"✅ Data preprocessing complete ({len(df_clean)} samples)")
        
        # Level 2: Extract features
        df_oriented = self.extract_orientation(df_clean)
        df_features = self.extract_advanced_features(df_oriented)
        print("✅ Feature extraction complete")
        
        # Level 3: Classify posture
        df_classified = self.classify_posture_realtime(df_features)
        print("✅ Real-time posture classification complete")
        
        # Level 4: Pattern analysis
        pattern_results = self.analyze_patterns(df_classified)
        print("✅ Pattern recognition complete")
        
        # Level 5: ML prediction (if trained)
        if self.is_trained:
            df_final = self.predict_posture_ml(df_classified)
            print("✅ ML prediction complete")
        else:
            df_final = df_classified
        
        return df_final, pattern_results
    
    def generate_realtime_alert(self, current_data, alert_threshold=0.7):
        """
        Generate real-time alerts for immediate feedback
        """
        if 'severity_score' not in current_data.columns:
            return None
        
        latest_severity = current_data['severity_score'].iloc[-1]
        latest_posture = current_data['posture_label'].iloc[-1]
        
        if latest_severity >= 3:  # High severity
            return {
                'level': 'high',
                'message': f"🚨 Posture Alert: {latest_posture.replace('_', ' ').title()}",
                'action': 'Adjust posture immediately',
                'type': 'vibration'
            }
        elif latest_severity >= 1:  # Medium severity
            return {
                'level': 'medium', 
                'message': f"⚠️ Posture Notice: {latest_posture.replace('_', ' ').title()}",
                'action': 'Consider adjusting position',
                'type': 'notification'
            }
        else:
            return None

# Example usage and testing
def test_algorithms():
    """Test the posture algorithms with sample data"""
    print("🧪 Testing Posture Algorithms...")
    
    # Create sample data (simulating dual sensor readings)
    np.random.seed(42)
    n_samples = 300  # 30 seconds at 10Hz
    
    sample_data = {
        'timestamp': np.arange(n_samples) * 100,  # 100ms intervals
        's1_accel_x': np.random.normal(-1, 0.5, n_samples),  # Forward lean
        's1_accel_y': np.random.normal(0, 0.3, n_samples),
        's1_accel_z': np.random.normal(9.5, 0.2, n_samples),
        's1_gyro_x': np.random.normal(0, 0.1, n_samples),
        's1_gyro_y': np.random.normal(0, 0.1, n_samples),  
        's1_gyro_z': np.random.normal(0, 0.1, n_samples),
        's2_accel_x': np.random.normal(0, 0.4, n_samples),
        's2_accel_y': np.random.normal(0, 0.3, n_samples),
        's2_accel_z': np.random.normal(9.8, 0.2, n_samples),
        's2_gyro_x': np.random.normal(0, 0.08, n_samples),
        's2_gyro_y': np.random.normal(0, 0.08, n_samples),
        's2_gyro_z': np.random.normal(0, 0.08, n_samples),
    }
    
    df_test = pd.DataFrame(sample_data)
    
    # Initialize algorithms
    algorithms = PostureAlgorithms(sample_rate=10, window_size=50)
    
    # Run complete analysis
    df_result, pattern_results = algorithms.process_complete_analysis(df_test)
    
    print("\n📊 Analysis Results:")
    print(f"Pattern Analysis: {pattern_results['pattern_analysis']}")
    print(f"Recommendations: {len(pattern_results['recommendations'])}")
    for i, rec in enumerate(pattern_results['recommendations'][:3], 1):
        print(f"  {i}. {rec}")
    
    return df_result, pattern_results

if __name__ == "__main__":
    test_algorithms()
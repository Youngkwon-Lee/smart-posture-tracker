#!/usr/bin/env python3
"""
Simple Arduino MCP Server for Smart Posture Tracker
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
import serial
import serial.tools.list_ports
import subprocess
import os

class ArduinoMCPServer:
    def __init__(self):
        self.arduino_port = None
        self.serial_connection = None
        self.arduino_cli_path = "arduino-cli"
        
    def find_arduino_ports(self) -> List[Dict[str, str]]:
        """Find available Arduino ports"""
        ports = []
        for port in serial.tools.list_ports.comports():
            if any(x in port.description.lower() for x in ['arduino', 'ch340', 'ch341', 'ftdi', 'usb serial']):
                ports.append({
                    "device": port.device,
                    "description": port.description,
                    "hwid": port.hwid
                })
        return ports
    
    def connect_arduino(self, port: str, baudrate: int = 9600) -> bool:
        """Connect to Arduino on specified port"""
        try:
            if self.serial_connection:
                self.serial_connection.close()
            
            self.serial_connection = serial.Serial(port, baudrate, timeout=1)
            self.arduino_port = port
            return True
        except Exception as e:
            print(f"Failed to connect to Arduino: {e}", file=sys.stderr)
            return False
    
    def send_command(self, command: str) -> str:
        """Send command to Arduino and get response"""
        if not self.serial_connection:
            return "Error: Not connected to Arduino"
        
        try:
            self.serial_connection.write((command + '\n').encode())
            response = self.serial_connection.readline().decode().strip()
            return response or "No response"
        except Exception as e:
            return f"Error: {e}"
    
    def compile_and_upload(self, sketch_path: str, board: str = "arduino:avr:uno") -> str:
        """Compile and upload Arduino sketch"""
        try:
            # Compile
            compile_cmd = [self.arduino_cli_path, "compile", "--fqbn", board, sketch_path]
            result = subprocess.run(compile_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return f"Compile failed: {result.stderr}"
            
            if not self.arduino_port:
                return "Error: No Arduino port connected"
            
            # Upload
            upload_cmd = [self.arduino_cli_path, "upload", "--fqbn", board, "--port", self.arduino_port, sketch_path]
            result = subprocess.run(upload_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return f"Upload failed: {result.stderr}"
            
            return "Success: Sketch compiled and uploaded"
        except Exception as e:
            return f"Error: {e}"
    
    def create_basic_posture_sketch(self, output_path: str) -> str:
        """Create a basic posture tracking sketch"""
        sketch_content = '''
#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

// LED and Buzzer pins
#define GREEN_LED 8
#define RED_LED 9
#define BUZZER 10

// Posture thresholds
#define GOOD_POSTURE_THRESHOLD 15
#define BAD_POSTURE_WARNING_TIME 30000  // 30 seconds

unsigned long bad_posture_start = 0;
bool is_bad_posture = false;

void setup() {
  Serial.begin(9600);
  Wire.begin();
  
  // Initialize MPU6050
  mpu.initialize();
  if(mpu.testConnection()) {
    Serial.println("MPU6050 connected successfully");
  } else {
    Serial.println("MPU6050 connection failed");
  }
  
  // Setup pins
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  
  // Initial LED state
  digitalWrite(GREEN_LED, HIGH);
  digitalWrite(RED_LED, LOW);
}

void loop() {
  // Read accelerometer data
  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);
  
  // Calculate angles (simplified)
  float pitch = atan2(-ax, sqrt(ay*ay + az*az)) * 180.0 / PI;
  float roll = atan2(ay, az) * 180.0 / PI;
  
  // Determine posture
  bool good_posture = (abs(pitch) < GOOD_POSTURE_THRESHOLD && abs(roll) < GOOD_POSTURE_THRESHOLD);
  
  if(good_posture) {
    // Good posture
    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, LOW);
    noTone(BUZZER);
    is_bad_posture = false;
    
    Serial.print("GOOD,");
  } else {
    // Bad posture
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(RED_LED, HIGH);
    
    if(!is_bad_posture) {
      bad_posture_start = millis();
      is_bad_posture = true;
    } else if(millis() - bad_posture_start > BAD_POSTURE_WARNING_TIME) {
      // Sound alarm after 30 seconds of bad posture
      tone(BUZZER, 1000, 200);
    }
    
    Serial.print("BAD,");
  }
  
  // Output data
  Serial.print(pitch);
  Serial.print(",");
  Serial.print(roll);
  Serial.print(",");
  Serial.println(good_posture ? "1" : "0");
  
  delay(100);  // 10Hz update rate
}
'''
        
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(sketch_content)
            return f"Sketch created: {output_path}"
        except Exception as e:
            return f"Error creating sketch: {e}"

    async def handle_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol requests"""
        method = request.get('method', '')
        params = request.get('params', {})
        
        if method == 'tools/list':
            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "result": {
                    "tools": [
                        {
                            "name": "list_ports",
                            "description": "List available Arduino ports"
                        },
                        {
                            "name": "connect_arduino", 
                            "description": "Connect to Arduino on specified port",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "port": {"type": "string", "description": "Serial port (e.g., COM3)"},
                                    "baudrate": {"type": "integer", "default": 9600}
                                },
                                "required": ["port"]
                            }
                        },
                        {
                            "name": "send_command",
                            "description": "Send command to Arduino",
                            "inputSchema": {
                                "type": "object", 
                                "properties": {
                                    "command": {"type": "string", "description": "Command to send"}
                                },
                                "required": ["command"]
                            }
                        },
                        {
                            "name": "create_posture_sketch",
                            "description": "Create basic posture tracking sketch",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "output_path": {"type": "string", "description": "Output file path for sketch"}
                                },
                                "required": ["output_path"]
                            }
                        },
                        {
                            "name": "compile_upload",
                            "description": "Compile and upload sketch to Arduino",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "sketch_path": {"type": "string", "description": "Path to Arduino sketch"},
                                    "board": {"type": "string", "default": "arduino:avr:uno"}
                                },
                                "required": ["sketch_path"]
                            }
                        }
                    ]
                }
            }
        
        elif method == 'tools/call':
            tool_name = params.get('name')
            args = params.get('arguments', {})
            
            if tool_name == 'list_ports':
                ports = self.find_arduino_ports()
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(ports, indent=2)}]
                    }
                }
            
            elif tool_name == 'connect_arduino':
                port = args.get('port')
                baudrate = args.get('baudrate', 9600)
                success = self.connect_arduino(port, baudrate)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": {
                        "content": [{"type": "text", "text": f"Connected: {success}"}]
                    }
                }
            
            elif tool_name == 'send_command':
                command = args.get('command')
                response = self.send_command(command)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": {
                        "content": [{"type": "text", "text": response}]
                    }
                }
            
            elif tool_name == 'create_posture_sketch':
                output_path = args.get('output_path')
                result = self.create_basic_posture_sketch(output_path)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": {
                        "content": [{"type": "text", "text": result}]
                    }
                }
            
            elif tool_name == 'compile_upload':
                sketch_path = args.get('sketch_path')
                board = args.get('board', 'arduino:avr:uno')
                result = self.compile_and_upload(sketch_path, board)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": {
                        "content": [{"type": "text", "text": result}]
                    }
                }
        
        return {
            "jsonrpc": "2.0",
            "id": request.get('id'),
            "error": {"code": -32601, "message": "Method not found"}
        }

    async def run(self):
        """Run MCP server"""
        server = ArduinoMCPServer()
        
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                request = json.loads(line.strip())
                response = await server.handle_mcp_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
                
            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {e}"}
                }
                print(json.dumps(error_response))
                sys.stdout.flush()

if __name__ == "__main__":
    server = ArduinoMCPServer()
    asyncio.run(server.run())
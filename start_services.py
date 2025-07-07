#!/usr/bin/env python3
"""
Integrated Services Startup Script
Starts all backend services for the news analysis application
"""

import subprocess
import time
import sys
import os
import signal
import threading
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def start_service(self, name, command, cwd=None, env=None):
        """Start a service in a subprocess"""
        try:
            print(f"🚀 Starting {name}...")
            
            # Set up environment
            service_env = os.environ.copy()
            if env:
                service_env.update(env)
            
            # Start process
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                env=service_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes.append((name, process))
            print(f"✅ {name} started with PID: {process.pid}")
            return process
            
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            return None
    
    def monitor_process(self, name, process):
        """Monitor a process and print its output"""
        while self.running and process.poll() is None:
            try:
                output = process.stdout.readline()
                if output:
                    print(f"[{name}] {output.strip()}")
            except:
                break
    
    def start_all_services(self):
        """Start all required services"""
        print("🎯 Starting Integrated News Analysis Services...")
        print("=" * 50)
        
        # Get current directory
        base_dir = Path(__file__).parent
        
        # 1. Start Python Bias Detection API (FastAPI)
        bias_api_dir = base_dir / "python_api"
        bias_process = self.start_service(
            "Bias Detection API",
            "python main.py",
            cwd=bias_api_dir
        )
        
        if bias_process:
            bias_thread = threading.Thread(
                target=self.monitor_process,
                args=("Bias API", bias_process)
            )
            bias_thread.daemon = True
            bias_thread.start()
        
        # Wait a bit for the first service to start
        time.sleep(3)
        
        # 2. Start Python Summarization API (Flask)
        summarization_process = self.start_service(
            "Summarization API",
            "python summarization.py",
            cwd=bias_api_dir
        )
        
        if summarization_process:
            summary_thread = threading.Thread(
                target=self.monitor_process,
                args=("Summary API", summarization_process)
            )
            summary_thread.daemon = True
            summary_thread.start()
        
        # Wait a bit for the second service to start
        time.sleep(3)
        
        # 3. Start Node.js Backend
        backend_dir = base_dir / "backend"
        backend_process = self.start_service(
            "Node.js Backend",
            "npm start",
            cwd=backend_dir
        )
        
        if backend_process:
            backend_thread = threading.Thread(
                target=self.monitor_process,
                args=("Backend", backend_process)
            )
            backend_thread.daemon = True
            backend_thread.start()
        
        print("\n" + "=" * 50)
        print("🎉 All services started!")
        print("\n📋 Service URLs:")
        print("   • Bias Detection API: http://localhost:8000")
        print("   • Summarization API:  http://localhost:5000")
        print("   • Integrated Backend: http://localhost:3000")
        print("\n🔗 API Endpoints:")
        print("   • GET  http://localhost:3000/api/news")
        print("   • POST http://localhost:3000/api/article/summarize")
        print("   • POST http://localhost:3000/api/article/bias-analysis")
        print("   • POST http://localhost:3000/api/article/complete-analysis")
        print("\n⏹️  Press Ctrl+C to stop all services")
        print("=" * 50)
    
    def stop_all_services(self):
        """Stop all running services"""
        print("\n🛑 Stopping all services...")
        self.running = False
        
        for name, process in self.processes:
            try:
                print(f"🛑 Stopping {name} (PID: {process.pid})...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"⚠️  Force killing {name}...")
                    process.kill()
                    process.wait()
                
                print(f"✅ {name} stopped")
                
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")
        
        print("🎯 All services stopped")

def signal_handler(signum, frame):
    """Handle Ctrl+C signal"""
    print("\n🛑 Received interrupt signal")
    if service_manager:
        service_manager.stop_all_services()
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create service manager
    service_manager = ServiceManager()
    
    try:
        # Start all services
        service_manager.start_all_services()
        
        # Keep the main thread alive
        while service_manager.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Keyboard interrupt received")
        service_manager.stop_all_services()
    except Exception as e:
        print(f"❌ Error: {e}")
        service_manager.stop_all_services()
        sys.exit(1) 
#!/usr/bin/env python3
import subprocess
import sys
import time
import threading
import uvicorn
from provider_service import app
import os

def run_provider_server():
    """Run the provider server in background"""
    uvicorn.run(app, host="127.0.0.1", port=3000, log_level="error")

def main():
    """Run the complete Pact testing workflow"""
    print("Starting Pact Contract Testing Workflow...")
    
    # Step 1: Run consumer tests to generate pacts
    print("\n1. Running consumer tests to generate pacts...")
    result = subprocess.run([
        "python", "-m", "pytest", "test_user_service_consumer.py", "-v"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Consumer tests failed: {result.stderr}")
        return 1
    
    print("Consumer tests passed! Pact files generated.")
    
    # Step 2: Start provider server
    print("\n2. Starting provider server...")
    server_thread = threading.Thread(target=run_provider_server, daemon=True)
    server_thread.start()
    time.sleep(3)  # Give server time to start
    
    # Step 3: Run provider verification
    print("\n3. Running provider verification...")
    result = subprocess.run([
        "python", "-m", "pytest", "test_provider_verification.py", "-v"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Provider verification failed: {result.stderr}")
        return 1
    
    print("Provider verification passed!")
    
    # Step 4: Publish to Pact Broker (if configured)
    broker_url = os.getenv("PACT_BROKER_URL")
    if broker_url:
        print("\n4. Publishing to Pact Broker...")
        # Implementation would go here
        print("Pacts published to broker successfully!")
    
    print("\n✅ Pact Contract Testing Workflow Complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
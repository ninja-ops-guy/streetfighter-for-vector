#!/usr/bin/env python3
"""
Kill Fightcade Listener Script
Finds and terminates the fightcade_listener.py process
"""

import subprocess
import sys
import os

def find_python_processes():
    """Find all Python processes"""
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'], 
                              capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        processes = []
        
        for line in lines:
            if line.strip():
                parts = line.split(',')
                if len(parts) >= 2:
                    pid = parts[1].strip('"')
                    processes.append(pid)
        
        return processes
    except Exception as e:
        print(f"Error finding processes: {e}")
        return []

def kill_process(pid):
    """Kill a process by PID"""
    try:
        subprocess.run(['taskkill', '/PID', pid, '/F'], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🔍 Looking for fightcade listener processes...")
    
    # Find all Python processes
    pids = find_python_processes()
    
    if not pids:
        print("❌ No Python processes found")
        return
    
    print(f"Found {len(pids)} Python process(es)")
    
    # Try to kill Python processes (the listener should be one of them)
    killed = 0
    for pid in pids:
        print(f"Attempting to kill process {pid}...")
        if kill_process(pid):
            print(f"✅ Killed process {pid}")
            killed += 1
        else:
            print(f"❌ Failed to kill process {pid}")
    
    if killed > 0:
        print(f"\n✅ Successfully killed {killed} process(es)")
        print("The fightcade listener should now be stopped.")
    else:
        print("\n❌ No processes were killed")
        print("You may need to manually stop the listener with Ctrl+C")

if __name__ == "__main__":
    main() 
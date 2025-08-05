#!/usr/bin/env python3
"""
Interactive Tmux Manager - Shows tmux sessions as they're created
Provides visibility into the orchestration process for users
"""

import subprocess
import sys
import time
import argparse
from typing import List, Optional
from pathlib import Path

class InteractiveTmuxManager:
    """Manages tmux sessions with user visibility"""
    
    def __init__(self):
        self.sessions = []
        self.verbose = False
        
    def log(self, message: str):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[TMUX MANAGER] {message}")
    
    def create_session_with_visibility(self, session_name: str, window_name: str = "Main", 
                                      command: Optional[str] = None) -> bool:
        """
        Create a tmux session and optionally run a command in it
        Shows the user what's happening
        """
        try:
            # Check if session already exists
            if self.session_exists(session_name):
                self.log(f"Session {session_name} already exists")
                return True
            
            # Create new session in detached mode
            cmd = ["tmux", "new-session", "-d", "-s", session_name]
            if window_name:
                cmd.extend(["-n", window_name])
            
            self.log(f"Creating session: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error creating session {session_name}: {result.stderr}")
                return False
            
            self.sessions.append(session_name)
            print(f"✅ Created tmux session: {session_name}")
            
            # If command provided, send it to the session
            if command:
                self.send_command_to_session(session_name, window_name or "0", command)
            
            return True
            
        except Exception as e:
            print(f"Error creating session {session_name}: {e}")
            return False
    
    def send_command_to_session(self, session_name: str, window: str, command: str) -> bool:
        """Send a command to a tmux session and show what's happening"""
        try:
            # Send the command
            send_cmd = ["tmux", "send-keys", "-t", f"{session_name}:{window}", command, "C-m"]
            self.log(f"Sending command: {' '.join(send_cmd)}")
            result = subprocess.run(send_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error sending command to {session_name}:{window}: {result.stderr}")
                return False
            
            print(f"🚀 Executed in {session_name}:{window}: {command}")
            return True
            
        except Exception as e:
            print(f"Error sending command to {session_name}:{window}: {e}")
            return False
    
    def create_window_in_session(self, session_name: str, window_name: str) -> bool:
        """Create a new window in an existing session"""
        try:
            cmd = ["tmux", "new-window", "-t", session_name, "-n", window_name]
            self.log(f"Creating window: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error creating window {window_name} in session {session_name}: {result.stderr}")
                return False
            
            print(f"✅ Created window {window_name} in session {session_name}")
            return True
            
        except Exception as e:
            print(f"Error creating window {window_name} in session {session_name}: {e}")
            return False
    
    def session_exists(self, session_name: str) -> bool:
        """Check if a tmux session exists"""
        try:
            result = subprocess.run(["tmux", "has-session", "-t", session_name], 
                                  capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def list_sessions(self) -> List[str]:
        """List all tmux sessions"""
        try:
            result = subprocess.run(["tmux", "list-sessions"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                sessions = []
                for line in result.stdout.strip().split('\n'):
                    if line and ':' in line:
                        sessions.append(line.split(':')[0])
                return sessions
            return []
        except:
            return []
    
    def show_session_status(self):
        """Show current tmux session status"""
        sessions = self.list_sessions()
        if sessions:
            print(f"\n📊 Current tmux sessions ({len(sessions)} total):")
            for session in sessions:
                try:
                    # Get windows in session
                    result = subprocess.run(["tmux", "list-windows", "-t", session], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        windows = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                        print(f"  {session}: {windows} window(s)")
                    else:
                        print(f"  {session}: status unknown")
                except:
                    print(f"  {session}: status unknown")
        else:
            print("📭 No tmux sessions running")
    
    def attach_to_session(self, session_name: str):
        """Attach to a tmux session (user can detach with Ctrl+B, D)"""
        if self.session_exists(session_name):
            print(f"\n🔗 Attaching to session '{session_name}'")
            print("💡 To detach later: Press Ctrl+B, then D")
            time.sleep(2)
            subprocess.run(["tmux", "attach-session", "-t", session_name])
        else:
            print(f"❌ Session '{session_name}' not found")
    
    def kill_session(self, session_name: str) -> bool:
        """Kill a tmux session"""
        try:
            result = subprocess.run(["tmux", "kill-session", "-t", session_name], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                if session_name in self.sessions:
                    self.sessions.remove(session_name)
                print(f"💀 Killed session: {session_name}")
                return True
            else:
                print(f"Error killing session {session_name}: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error killing session {session_name}: {e}")
            return False

def main():
    """Main function for interactive tmux management"""
    parser = argparse.ArgumentParser(description="Interactive Tmux Manager")
    parser.add_argument("action", choices=["create", "window", "send", "list", "attach", "kill", "status"],
                       help="Action to perform")
    parser.add_argument("--session", "-s", help="Session name")
    parser.add_argument("--window", "-w", help="Window name")
    parser.add_argument("--command", "-c", help="Command to execute")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    manager = InteractiveTmuxManager()
    manager.verbose = args.verbose
    
    if args.action == "create":
        if not args.session:
            print("Error: --session required for create action")
            return 1
        manager.create_session_with_visibility(args.session, args.window or "Main", args.command)
        
    elif args.action == "window":
        if not args.session or not args.window:
            print("Error: --session and --window required for window action")
            return 1
        manager.create_window_in_session(args.session, args.window)
        
    elif args.action == "send":
        if not args.session or not args.command:
            print("Error: --session and --command required for send action")
            return 1
        manager.send_command_to_session(args.session, args.window or "0", args.command)
        
    elif args.action == "list":
        manager.show_session_status()
        
    elif args.action == "attach":
        if not args.session:
            print("Error: --session required for attach action")
            return 1
        manager.attach_to_session(args.session)
        
    elif args.action == "kill":
        if not args.session:
            print("Error: --session required for kill action")
            return 1
        manager.kill_session(args.session)
        
    elif args.action == "status":
        manager.show_session_status()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
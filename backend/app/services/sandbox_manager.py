import subprocess
import tempfile
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)

class SandboxExecutionResult:
    def __init__(self, success: bool, stdout: str, stderr: str, exit_code: int, duration: float, error: str = None):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.duration = duration
        self.error = error

class SandboxManager:
    """Manages ephemeral Docker containers for sandboxed code execution."""
    def __init__(self):
        self.image = os.getenv("SANDBOX_IMAGE", "python:3.11-alpine")
        self.timeout = int(os.getenv("SANDBOX_TIMEOUT_SECONDS", "10"))
        self.memory = os.getenv("SANDBOX_MEMORY_LIMIT", "128m")
        self.cpus = os.getenv("SANDBOX_CPU_LIMIT", "0.5")

    def execute_python(self, code: str, input_files: Dict[str, str] = None) -> SandboxExecutionResult:
        input_files = input_files or {}
        
        with tempfile.TemporaryDirectory(prefix="sih_sandbox_") as tmpdir:
            script_path = os.path.join(tmpdir, "main.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)
                
            for fname, fcontent in input_files.items():
                safe_fname = os.path.basename(fname)
                with open(os.path.join(tmpdir, safe_fname), "w", encoding="utf-8") as f:
                    f.write(fcontent)
            
            container_name = f"sandbox_{uuid.uuid4().hex[:8]}"
            
            cmd = [
                "docker", "run", "--rm",
                "--name", container_name,
                "--network", "none",                   # Explicitly disable network
                "--memory", self.memory,               # Memory limit
                "--cpus", self.cpus,                   # CPU limit
                "--pids-limit", "64",                  # Process limit to prevent fork bombs
                "--cap-drop", "ALL",                   # Drop all privileges
                "-v", f"{tmpdir}:/workspace:ro",       # Mount workspace read-only
                "-w", "/workspace",                    # Set working directory
                # Run as a non-root user (alpine python image usually has a default user, or we can use generic uid)
                "--user", "1000:1000",                 
                self.image,
                "python", "main.py"
            ]
            
            start_time = datetime.now(timezone.utc)
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                end_time = datetime.now(timezone.utc)
                duration = (end_time - start_time).total_seconds()
                
                return SandboxExecutionResult(
                    success=(result.returncode == 0),
                    stdout=result.stdout[:10000],
                    stderr=result.stderr[:10000],
                    exit_code=result.returncode,
                    duration=duration,
                    error=None if result.returncode == 0 else "Execution failed"
                )
                
            except subprocess.TimeoutExpired as e:
                end_time = datetime.now(timezone.utc)
                duration = (end_time - start_time).total_seconds()
                
                subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
                
                return SandboxExecutionResult(
                    success=False,
                    stdout=e.stdout.decode('utf-8')[:10000] if e.stdout else "",
                    stderr=e.stderr.decode('utf-8')[:10000] if e.stderr else "",
                    exit_code=-1,
                    duration=duration,
                    error=f"Execution timed out after {self.timeout} seconds."
                )
            except Exception as e:
                end_time = datetime.now(timezone.utc)
                duration = (end_time - start_time).total_seconds()
                
                subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
                
                return SandboxExecutionResult(
                    success=False,
                    stdout="",
                    stderr="",
                    exit_code=-2,
                    duration=duration,
                    error=f"Sandbox execution failed: {str(e)}"
                )

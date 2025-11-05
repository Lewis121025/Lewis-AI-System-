"""Isolated sandbox for executing generated Python code."""

from __future__ import annotations

import asyncio
import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path
from subprocess import TimeoutExpired
from typing import Optional

from app.config import get_settings

LOGGER = logging.getLogger(__name__)


@dataclass
class SandboxResult:
    """Outcome of sandboxed code execution."""

    success: bool
    stdout: str
    stderr: str
    return_code: int
    error: Optional[str] = None


class Sandbox:
    """Execute arbitrary Python code in a subprocess with timeouts."""

    def __init__(self, timeout: Optional[int] = None) -> None:
        settings = get_settings()
        self.python = settings.sandbox_python
        self.timeout = timeout or settings.sandbox_timeout_seconds

    async def run(self, code: str) -> SandboxResult:
        """Execute code asynchronously and return captured result."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            code_path = Path(tmp_dir) / "sandbox_exec.py"
            code_path.write_text(code, encoding="utf-8")
            process = await asyncio.create_subprocess_exec(
                self.python,
                str(code_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(), timeout=self.timeout
                )
                stdout = stdout_bytes.decode("utf-8")
                stderr = stderr_bytes.decode("utf-8")
                success = process.returncode == 0
                return SandboxResult(
                    success=success,
                    stdout=stdout,
                    stderr=stderr,
                    return_code=process.returncode or 0,
                    error=None if success else stderr.strip(),
                )
            except TimeoutExpired:
                process.kill()
                await process.communicate()
                LOGGER.warning("Sandbox execution timed out after %s seconds", self.timeout)
                return SandboxResult(
                    success=False,
                    stdout="",
                    stderr="Execution timed out",
                    return_code=-1,
                    error="timeout",
                )

    def run_sync(self, code: str) -> SandboxResult:
        """Synchronous wrapper for sandbox execution."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.run(code))
        else:
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self.run(code))
            finally:
                loop.close()

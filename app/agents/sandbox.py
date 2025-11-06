"""沙箱执行模块：在隔离的子进程中运行动态生成的 Python 代码。"""

from __future__ import annotations

import asyncio
import logging
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.config import get_settings

LOGGER = logging.getLogger(__name__)


@dataclass
class SandboxResult:
    """记录沙箱执行的结果，包括 stdout/stderr/返回码等。"""

    success: bool
    stdout: str
    stderr: str
    return_code: int
    error: Optional[str] = None


class Sandbox:
    """提供同步/异步接口，控制代码执行超时并捕获输出。"""

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
                stdout = stdout_bytes.decode("utf-8", errors="replace")
                stderr = stderr_bytes.decode("utf-8", errors="replace")
                success = process.returncode == 0
                return SandboxResult(
                    success=success,
                    stdout=stdout,
                    stderr=stderr,
                    return_code=process.returncode or 0,
                    error=None if success else stderr.strip(),
                )
            except asyncio.TimeoutError:
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
            result: SandboxResult | None = None
            error: BaseException | None = None

            def _worker() -> None:
                nonlocal result, error
                try:
                    result = asyncio.run(self.run(code))
                except BaseException as exc:  # pragma: no cover - defensive guard
                    error = exc

            thread = threading.Thread(target=_worker, daemon=True)
            thread.start()
            thread.join()

            if error is not None:
                raise error
            if result is None:  # pragma: no cover - safety fallback
                raise RuntimeError("Sandbox execution did not return a result.")
            return result

import sys

from app.agents.sandbox import Sandbox


def test_sandbox_executes_python_code_successfully():
    sandbox = Sandbox(timeout=3)
    result = sandbox.run_sync("print('hello sandbox')")
    assert result.success is True
    assert "hello sandbox" in result.stdout

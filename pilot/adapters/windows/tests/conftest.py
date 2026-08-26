"""Shared fixtures.

The unit suite runs on any platform against :mod:`..fakes`. The integration
suite is gated on Windows plus an explicit opt-in environment variable, because
it takes over the real desktop — mouse, keyboard, and foreground focus — and
must never start by surprise on a developer's machine or in CI.
"""

from __future__ import annotations

import os
import sys

import pytest

from ..adapter import WindowsOperatorAdapter
from ..fakes import FakeBackend, make_desktop

#: Set to "1" to allow the machine-dependent integration suite to run.
INTEGRATION_ENV_VAR = "KLEARFLOW_PILOT_WINDOWS_INTEGRATION"


def integration_enabled() -> bool:
    return sys.platform == "win32" and os.environ.get(INTEGRATION_ENV_VAR) == "1"


def integration_skip_reason() -> str:
    if sys.platform != "win32":
        return f"requires Windows (host is {sys.platform})"
    return f"set {INTEGRATION_ENV_VAR}=1 to run desktop integration tests"


requires_windows_desktop = pytest.mark.skipif(
    not integration_enabled(), reason=integration_skip_reason()
)


@pytest.fixture
def backend() -> FakeBackend:
    """A fake desktop that can launch simulated Notepad and Calculator."""
    return make_desktop()


@pytest.fixture
def adapter(backend: FakeBackend) -> WindowsOperatorAdapter:
    """Adapter wired to the fake backend and its virtual clock."""
    return WindowsOperatorAdapter(backend=backend, clock=backend.clock)


@pytest.fixture
def notepad(backend: FakeBackend):
    """A launched simulated Notepad."""
    from ..fakes import make_fake_notepad

    return backend.add_app(make_fake_notepad(backend))


@pytest.fixture
def calculator(backend: FakeBackend):
    """A launched simulated Calculator."""
    from ..fakes import make_fake_calculator

    return backend.add_app(make_fake_calculator(backend))

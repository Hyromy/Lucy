import pytest
from unittest.mock import (
    patch,
    MagicMock,
    AsyncMock,
)

class TestHelpModule:
    class TestCMDPackage:
        class TestHelp:
            def test_something(self):
                assert 1 == 1

    class TestElements:
        class TestBaseButton:
            def test_something(self):
                assert 1 == 1

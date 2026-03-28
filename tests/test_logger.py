"""Tests for the MemoryWeave logger module."""

import logging

import pytest

from memoryweave.logger import configure_logging, get_logger


class TestGetLogger:
    """Make sure get_logger returns properly namespaced loggers."""

    def test_returns_logger_instance(self) -> None:
        logger = get_logger(__name__)
        assert isinstance(logger, logging.Logger)

    def test_logger_name_under_memoryweave(self) -> None:
        # every module logger should live under the memoryweave namespace
        logger = get_logger("memoryweave.extractor")
        assert logger.name == "memoryweave.extractor"

    def test_different_names_give_different_loggers(self) -> None:
        logger1 = get_logger("memoryweave.store")
        logger2 = get_logger("memoryweave.graph")
        assert logger1 is not logger2


class TestConfigureLogging:
    """Test that configure_logging sets the right levels."""

    def test_accepts_string_level_info(self) -> None:
        configure_logging("info")
        root = logging.getLogger("memoryweave")
        assert root.level == logging.INFO

    def test_accepts_string_level_debug(self) -> None:
        configure_logging("debug")
        root = logging.getLogger("memoryweave")
        assert root.level == logging.DEBUG

    def test_accepts_string_level_warning(self) -> None:
        configure_logging("warning")
        root = logging.getLogger("memoryweave")
        assert root.level == logging.WARNING

    def test_accepts_int_level(self) -> None:
        configure_logging(logging.ERROR)
        root = logging.getLogger("memoryweave")
        assert root.level == logging.ERROR

    def test_invalid_level_raises(self) -> None:
        with pytest.raises(ValueError):
            configure_logging("nonsense")

    def test_uppercase_level_works(self) -> None:
        # users might type "INFO" or "Debug" — should handle both
        configure_logging("WARNING")
        root = logging.getLogger("memoryweave")
        assert root.level == logging.WARNING

import pytest

from silverback.serial_io import SerialError, iter_serial_lines


def test_missing_device_raises_serial_error():
    serial = pytest.importorskip("serial")
    assert serial is not None
    with pytest.raises(SerialError, match="could not open serial port"):
        next(iter_serial_lines("/dev/silverback-not-a-real-port", 115200))

"""
Trigger using an LPT port.
"""
import time
import threading
from pathlib import Path

from ._trigger import _Trigger
from .. import logger
from ..utils.io._imports import import_optional_dependency


class TriggerLPT(_Trigger):
    """
    Trigger using the LPT port on the motherboard.

    Parameters
    ----------
    portaddr : hex | int
        Port address in hexadecimal format (standard: 0x278, 0x378).
    delay : int
        Delay in milliseconds until which a new trigger cannot be sent.
    verbose : bool
        If True, display a logger.info message when a trigger is sent.
    """

    def __init__(self, portaddr: int, delay:int = 50, verbose: bool = True):
        super().__init__(verbose)
        self._portaddr = TriggerLPT._check_portaddr(portaddr)
        logger.debug("LPT port address: %d" % self._portaddr)

        self._lpt = TriggerLPT._load_dll()
        if self._lpt.init() == -1:
            logger.error(
                'Connecting to LPT port failed. Check the driver status.')
            raise IOError

        self._delay = delay / 1000.0
        self._offtimer = threading.Timer(self._delay, self._signal_off)

    def signal(self, value: int) -> bool:
        """
        Send a trigger value.
        """
        if self._offtimer.is_alive():
            logger.warning(
                'You are sending a new signal before the end of the last '
                'signal. Signal ignored. Delay required = {self.delay} ms.')
            return False
        self._set_data(value)
        super().signal(value)
        self._offtimer.start()
        return True

    def _signal_off(self):
        """
        Reset trigger signal to 0 and reset offtimer as Threads are one-call
        only.
        """
        self._set_data(0)
        self._offtimer = threading.Timer(self._delay, self._signal_off)

    def _set_data(self, value: int):
        """
        Set the trigger signal to value.
        """
        super()._set_data(value)
        self._lpt.setdata(self._portaddr, value)

    # --------------------------------------------------------------------
    @staticmethod
    def _check_portaddr(portaddr: int) -> int:
        """
        Checks the portaddr value against usual values.
        """
        if portaddr not in [0x278, 0x378]:
            logger.warning(f'LPT port address {portaddr} is unusual.')

        return int(portaddr)

    @staticmethod
    def _load_dll():
        """
        Load the correct .dll.
        """
        import ctypes

        if ctypes.sizeof(ctypes.c_voidp) == 4:
            extension = '32.dll'
        else:
            extension = '64.dll'
        dllname = 'LptControl_Desktop' + extension
        dllpath = Path(__file__).parent / 'lpt_libs' / dllname

        if not dllpath.exists():
            logger.error(f"Cannot find the required library '{dllname}'.")
            raise RuntimeError

        logger.info(f"Loading '{dllpath}'.")
        return ctypes.cdll.LoadLibrary(str(dllpath))

    # --------------------------------------------------------------------
    @property
    def portaddr(self):
        """
        Port address.
        """
        return self._portaddr

    @portaddr.setter
    def portaddr(self, portaddr: int):
        if not self._offtimer.is_alive():
            self._portaddr = TriggerLPT._check_portaddr(portaddr)
        else:
            logger.warning(
                'You are changing the port while an event has been sent less '
                'than {self.delay} ms ago. Skipping.')

    @property
    def delay(self):
        """
        Delay to wait between 2 .signal() call in milliseconds.
        """
        return self._delay * 1000.0

    @delay.setter
    def delay(self, delay: int):
        if not self._offtimer.is_alive():
            self._delay = delay / 1000.0
            self._offtimer = threading.Timer(self._delay, self._signal_off)
        else:
            logger.warning(
                'You are changing the delay while an event has been sent less '
                'than {self.delay} ms ago. Skipping.')


class TriggerUSB2LPT(_Trigger):
    """
    Trigger using a USB to LPT converter. Drivers can be found here:
    https://www-user.tu-chemnitz.de/~heha/bastelecke/Rund%20um%20den%20PC/USB2LPT/

    Parameters
    ----------
    delay : int
        Delay in milliseconds until which a new trigger cannot be sent.
    verbose : bool
        If True, display a logger.info message when a trigger is sent.
    """

    def __init__(self, delay: int = 50, verbose: bool = True):
        super().__init__(verbose)
        self._lpt = TriggerUSB2LPT._load_dll()
        if self._lpt.init() == -1:
            logger.error(
                'Connecting to LPT port failed. Check the driver status.')
            raise IOError

        self._delay = delay / 1000.0
        self._offtimer = threading.Timer(self._delay, self._signal_off)

    def signal(self, value:int) -> bool:
        """
        Send a trigger value.
        """
        if self._offtimer.is_alive():
            logger.warning(
                'You are sending a new signal before the end of the last '
                'signal. Signal ignored. Delay required = {self.delay} ms.')
            return False
        self._set_data(value)
        super().signal(value)
        self._offtimer.start()
        return True

    def _signal_off(self):
        """
        Reset trigger signal to 0 and reset offtimer as Threads are one-call
        only.
        """
        self._set_data(0)
        self._offtimer = threading.Timer(self._delay, self._signal_off)

    def _set_data(self, value: int):
        """
        Set the trigger signal to value.
        """
        super()._set_data(value)
        self._lpt.setdata(value)

    # --------------------------------------------------------------------
    @staticmethod
    def _load_dll():
        """
        Load the correct .dll.
        """
        import ctypes

        if ctypes.sizeof(ctypes.c_voidp) == 4:
            extension = '32.dll'
        else:
            extension = '64.dll'
        dllname = 'LptControl_USB2LPT' + extension
        dllpath = Path(__file__).parent / 'lpt_libs' / dllname

        if not dllpath.exists():
            logger.error(f"Cannot find the required library '{dllname}'.")
            raise RuntimeError

        logger.info(f"Loading '{dllpath}'.")
        return ctypes.cdll.LoadLibrary(str(dllpath))

    # --------------------------------------------------------------------
    @property
    def delay(self):
        """
        Delay to wait between 2 .signal() call in milliseconds.
        """
        return self._delay * 1000.0

    @delay.setter
    def delay(self, delay: int):
        if not self._offtimer.is_alive():
            self._delay = delay / 1000.0
            self._offtimer = threading.Timer(self._delay, self._signal_off)
        else:
            logger.warning(
                'You are changing the delay while an event has been sent less '
                'than {self.delay} ms ago. Skipping.')


class TriggerArduino2LPT(_Trigger):
    """
    Trigger using an ARDUINO to LPT converter. Design of the converter can be
    found here: https://github.com/fcbg-hnp/arduino-trigger

    Parameters
    ----------
    delay : int
        Delay in milliseconds until which a new trigger cannot be sent.
    verbose : bool
        If True, display a logger.info message when a trigger is sent.
    """
    BAUD_RATE = 115200

    def __init__(self, delay: int = 50, verbose: bool = True):
        import_optional_dependency(
            "serial", extra="Install pyserial for ARDUINO support.")
        super().__init__(verbose)

        self._com_port = TriggerArduino2LPT._find_arduino_port()
        self._connect_arduino(self._com_port, baud_rate=self.BAUD_RATE)

        self._delay = delay / 1000.0
        self._offtimer = threading.Timer(self._delay, self._signal_off)

    def _connect_arduino(self, com_port: str, baud_rate: int):
        """
        Connect to the Arduino LPT converter.

        Parameters
        ----------
        com_port : str
            Qrduino COM port.
        baud_rate : int
            Baud rate, determines the communication speed.
        """
        import serial

        try:
            self._ser = serial.Serial(com_port, self.BAUD_RATE)
        except serial.SerialException as error:
            logger.error(
                "Disconnect and reconnect the ARDUINO convertor because "
                f"{error}", exc_info=True)
            raise Exception from error

        time.sleep(1)
        logger.info(f'Connected to {com_port}.')

    def signal(self, value: int) -> bool:
        """
        Send a trigger value.
        """
        if self._offtimer.is_alive():
            logger.warning(
                'You are sending a new signal before the end of the last '
                'signal. Signal ignored. Delay required = {self.delay} ms.')
            return False
        self._set_data(value)
        super().signal(value)
        self._offtimer.start()
        return True

    def _signal_off(self):
        """
        Reset trigger signal to 0 and reset offtimer as Threads are one-call
        only.
        """
        self._set_data(0)
        self._offtimer = threading.Timer(self._delay, self._signal_off)

    def _set_data(self, value: int):
        """
        Set the trigger signal to value.
        """
        super()._set_data(value)
        self._ser.write(bytes([value]))

    def close(self):
        """
        Disconnects the Arduino and free the COM port.
        """
        try:
            self._ser.close()
        except Exception:
            pass

    def __del__(self):
        self.close()

    # --------------------------------------------------------------------
    @staticmethod
    def _find_arduino_port() -> str:
        """
        Automatic Arduino COM port detection.
        """
        from serial.tools import list_ports

        com_port = None
        for arduino in list_ports.grep(regexp='Arduino'):
            logger.info(f'Found {arduino}')
            com_port = arduino.device
            break
        if com_port is None:
            logger.error('No arduino found.')
            raise IOError

    # --------------------------------------------------------------------
    @property
    def com_port(self):
        """
        COM port to use.
        """
        return self._com_port

    @com_port.setter
    def com_port(self, com_port):
        self._connect_arduino(com_port, baud_rate=self.BAUD_RATE)
        self._com_port = com_port

    @property
    def delay(self):
        """
        Delay to wait between 2 .signal() call in milliseconds.
        """
        return self._delay * 1000.0

    @delay.setter
    def delay(self, delay):
        if not self._offtimer.is_alive():
            self._delay = delay / 1000.0
            self._offtimer = threading.Timer(self._delay, self._signal_off)
        else:
            logger.warning(
                'You are changing the delay while an event has been sent less '
                'than {self.delay} ms ago. Skipping.')

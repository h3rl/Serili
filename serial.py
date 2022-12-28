import serial
import serial.threaded
import serial.tools

# # thread imports
# from serial.threaded import LineReader, ReaderThread

# comport import
from serial.tools.list_ports import comports

class SerialLib():
    def __init__(self) -> None:
        pass

    def getBTports(self) -> list[str]:
        """Returns a list of bluetooth ports"""
        ports = []
        for port in comports():
            print(port.device, port.hwid)
            if port.hwid.startswith("BT"):
                ports.append(port.device)
        if len(ports) == 0:
            print("No bluetooth ports found")
            return None
        return ports
    
    def openPort(self, port: str) -> serial.Serial:
        """Opens a port and returns the serial object"""
        try:
            ser = serial.Serial(port, 9600, timeout=1)
            ser.close()
            ser.open()
            return ser
        except:
            print("Failed to open serial port")
            return None

# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

from pymodbus.client import ModbusTcpClient
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def input_data():
    host = '127.0.0.1'
    port = 502
    host_string = input("Please enter the host address (127.0.0.1): ")
    if host_string != "":
        host = host_string
    port_string = input("Please enter the port number (502 as default): ")
    if port_string != "":
        port = int(port_string)

class ModbusMaster:
    def __init__(self, host:str = '127.0.0.1', port:int = 502):
        self.host = host
        self.port = port
        self.client = ModbusTcpClient(host = host, port = port)
        self.is_connected = False

    def connect(self) -> bool:
        try:
            self.is_connected = self.client.connect()
            if self.is_connected:
                logger.info(f"Connected to Modbus server at {self.host}:{self.port}")
            else:
                logger.error(f"Failed to connect to {self.host}:{self.port}")
            return self.is_connected
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("Disconnected from Modbus server")







if __name__ == '__main__':
    input_data()
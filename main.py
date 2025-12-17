# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from typing import Dict, List, Tuple, Any, Optional
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def input_connection_parameters():
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

    def read_holding_registers(self, address: int, count: int = 1, slave_id: int = 1) -> List[int]:
        try:
            response = self.client.read_holding_registers(address, count = count, device_id = slave_id)
            if not response.isError():
                return list(response.registers)
            else:
                logger.error(f"Error reading holding registers at address {address}")
                return []
        except ModbusException as e:
            logger.error(f"Modbus exception reading holding registers: {e}")
            return []

    def write_register(self, address: int, value: int, slave_id: int = 1) -> bool:
        try:
            response = self.client.write_register(address, value, device_id = slave_id)
            return not response.isError()
        except ModbusException as e:
            logger.error(f"Modbus exception writing register: {e}")
            return False

if __name__ == '__main__':
    input_connection_parameters()
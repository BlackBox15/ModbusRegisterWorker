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
        self.connect()

    def connect(self) -> bool:
        try:
            self.is_connected = self.client.connect()
            if self.is_connected:
                pass
                # logger.info(f"Connected to Modbus server at {self.host}:{self.port}")
            else:
                pass
                # logger.error(f"Failed to connect to {self.host}:{self.port}")
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

    def scan_devices(self, start_id: int = 1, end_id: int = 247) -> Dict[int, bool]:
        devices = {}

        # logger.info(f"Scanning for Modbus devices from ID {start_id} to {end_id}")

        for slave_id in range(start_id, end_id + 1):
            try:
                # Try to read a single coil to check if device responds
                response = self.client.read_coils(0, device_id = slave_id)
                if not response.isError():
                    devices[slave_id] = True
                    logger.info(f"Device found at slave ID {slave_id}")
                else:
                    devices[slave_id] = False
                    logger.info(f"Device found with Exception at slave ID {slave_id}")
            except:
                logger.info(f"Not found at slave ID {slave_id}")
                devices[slave_id] = False

        return devices

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

def print_menu():
    print("\nAvailable commands:")
    print("  read [address] [count] [slave] - Read data")
    # print("  read [type] [address] [count] [slave] - Read data")
    print("  write [address] [value] [slave] - Write data")
    # print("  write [type] [address] [value] [slave] - Write data")
    print("  scan [start] [end] - Scan for devices")
    # print("  config - Read multiple addresses from config")
    # print("  save - Save data to file")
    print("  help - Show this help")
    print("  exit - Exit program")
    # print("\nTypes: holding")
    # print("\nTypes: coil, discrete, holding, input")


def main():
    print("ModbusRegisterWorker is here!")

    host = input("Enter Modbus server IP [127.0.0.1]: ").strip() or "127.0.0.1"
    port = input("Enter Modbus server port [502]: ").strip() or "502"

    master = ModbusMaster(host, int(port))

    if not master.is_connected:
        print("Failed to connect. Exiting.")
        return

    print(f"\nConnected to {host}:{port}")
    print_menu()

    while True:
        try:
            command = input("\n> ").strip().lower().split()

            if not command:
                continue

            if command[0] == 'exit':
                break
            elif command[0] == 'help':
                print_menu()
            elif command[0] == 'scan' and len(command) >= 3:
                start_id = int(command[1])
                end_id = int(command[2])
                found = False

                devices = master.scan_devices(start_id, end_id)

                print(f"Scan results ({start_id}-{end_id}):")

                for slave_id, is_active in devices.items():
                    if is_active:
                        print(f"  Device found at slave ID {slave_id}")
                        found = True

                if not found:
                    print("  No devices found")

            elif command[0] == 'read' and len(command) >= 3:
                # read_type = command[1]
                address = int(command[1])
                count = int(command[2])
                slave_id = int(command[3]) if len(command) > 3 else 1

                result = master.read_holding_registers(address, count, slave_id)
                print(f"Holding Registers [{address}:{address + count - 1}]: {result}")

                # if read_type == 'coil':
                #     result = master.read_coils(address, count, slave_id)
                #     print(f"Coils [{address}:{address + count - 1}]: {result}")
                # elif read_type == 'discrete':
                #     result = master.read_discrete_inputs(address, count, slave_id)
                #     print(f"Discrete Inputs [{address}:{address + count - 1}]: {result}")
                # elif read_type == 'holding':
                #     result = master.read_holding_registers(address, count, slave_id)
                #     print(f"Holding Registers [{address}:{address + count - 1}]: {result}")
                # elif read_type == 'input':
                #     result = master.read_input_registers(address, count, slave_id)
                #     print(f"Input Registers [{address}:{address + count - 1}]: {result}")
            elif command[0] == 'write' and len(command) >= 3:
                # write_type = command[1]
                address = int(command[1])
                value = command[2]
                slave_id = int(command[3]) if len(command) > 3 else 1

                int_value = int(value)
                success = master.write_register(address, int_value, slave_id)
                print(f"Write register {address}: {'Success' if success else 'Failed'}")
            else:
                print("Invalid command.")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

    master.disconnect()
    print("Disconnected from Modbus server")

if __name__ == '__main__':
    # input_connection_parameters()
    main()
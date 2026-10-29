from logging import exception

from pymodbus.client import ModbusTcpClient
import pymodbus.exceptions
from typing import Dict, List, Tuple, Any, Optional
import logging
import time
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
                # pass
                logger.info(f"Connected to Modbus server at {self.host}:{self.port}")
            else:
                # pass
                logger.error(f"Failed to connect to {self.host}:{self.port}")
            return self.is_connected
        except pymodbus.exceptions.ModbusException as e:
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

        logger.info(f"Scanning for Modbus devices from ID {start_id} to {end_id}")

        for slave_id in range(start_id, end_id + 1):
            try:
                # Try to read a single coil to check if device responds
                response = self.client.read_coils(0, device_id = slave_id)
                # response2 = self.client.diag_read_diagnostic_register(device_id=slave_id, no_response_expected=False)


                if not response.isError():
                    devices[slave_id] = True
                    logger.info(f"Device found at slave ID {slave_id}")
                else:
                    devices[slave_id] = False
                    # logger.info(f"Device found with Exception at slave ID {slave_id}")
            except pymodbus.exceptions.ModbusException as e:
                logger.info(f"Not found at slave ID {slave_id}")
                logger.info(f"Connection error: {e}")
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
        except pymodbus.ModbusException as e:
            logger.error(f"Modbus exception reading holding registers: {e}")
            return []

    def write_register(self, address: int, value: int, slave_id: int = 1) -> bool:
        try:
            response = self.client.write_register(address, value, device_id = slave_id, no_response_expected=False)
            return True
        except pymodbus.ModbusException as e:
            logger.error(f"Modbus exception writing register: {e}")
            return False

    def read_coils(self, address: int, count: int = 1, slave_id: int = 1) -> List[bool]:
        """Read coils (discrete outputs)"""
        try:
            response = self.client.read_coils(address, device_id=slave_id)
            if not response.isError():
                return [bool(bit) for bit in response.bits[:count]]
            else:
                logger.error(f"Error reading coils at address {address}")
                return []
        except pymodbus.ModbusException as e:
            logger.error(f"Modbus exception reading coils: {e}")
            return []

def print_menu():
    print("\nAvailable commands:")
    print("  read [address] [count] [slave = 1] - Read data")
    # print("  read [type] [address] [count] [slave] - Read data")
    print("  write [address] [value] [slave = 1] - Write data")
    print("  many [address] [value] [count] [delay = 0] [slave = 1] - [Experimental] write multiple values use 0x06 command")
    # print("  write [type] [address] [value] [slave] - Write data")
    print("  scan [start] [end] - Scan for devices")
    # print("  config - Read multiple addresses from config")
    # print("  save - Save data to file")
    print("  help - Show this help")
    print("  exit - Exit program")
    # print("\nTypes: holding")
    # print("\nTypes: coil, discrete, holding, input")

def task_read_coil(mb_master: ModbusMaster, stop_event):
    while not stop_event.is_set():
        mb_master.read_coils(0)
        # time.sleep()

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
    # stop_event_for_thread = threading.Event()
    # thread1 = threading.Thread(target=task_read_coil, args=(master, stop_event_for_thread))
    # thread1.start()

    while True:
        try:
            command = input("\n> ").strip().lower().split()

            # master.read_coils(address=0)

            if not command:
                continue

            if command[0] == 'exit':
                # stop_event_for_thread.set()
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
                address = int(command[1])
                count = int(command[2])
                slave_id = int(command[3]) if len(command) > 3 else 1

                result = master.read_holding_registers(address, count, slave_id)
                print(f"Holding Registers [{address}:{address + count - 1}]: {result}")

            elif command[0] == 'write' and len(command) >= 3:
                address = int(command[1])
                int_value = int(command[2])
                slave_id = int(command[3]) if len(command) > 3 else 1

                success = master.write_register(address, int_value, slave_id)
                print(f"Write register {address}: {'Success' if success else 'Failed'}")

            elif command[0] == 'many' and len(command) >= 4:
                address = int(command[1])
                int_value = int(command[2])
                count = int(command[3])
                delay = float(command[4]) if len(command) > 4 else 0
                slave_id = int(command[5]) if len(command) > 5 else 1
                successes = [0] * count

                for i in range(count):
                    successes[i] = master.write_register(address, int_value, slave_id)
                    time.sleep(delay)
                    address += 1
                    print(f"Write register {address}: {'Success' if successes[i] else 'Failed'}")

            else:
                print("Invalid command.")

        except KeyboardInterrupt:
            thread1.join()
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

    master.disconnect()
    print("Disconnected from Modbus server")

if __name__ == '__main__':
    # input_connection_parameters()
    main()
# assumes UART is connected to RPi5 and is outputting data at 115200 baud rate.

import serial
import time
import sys
import re
from typing import Optional
from rpi_types import RpiBootloaderInfo

version_pattern = re.compile(r"VERSION:\d+")
date_pattern = re.compile(r"DATE:\s\d{4}/\d{2}/\d{2}")
chip_pattern = re.compile(r"chip ID:\s\w+")

'''
This dumps UART info and grabs the following values:
- chip IDs
- firmware versions/dates
- other important info
'''
def uart_info_dump(device: str, obtain_firmware_info: bool = False, wait_for_login: bool = False) -> Optional[RpiBootloaderInfo]:
    port = serial.Serial(device, 115200, timeout=1)
    rpi_version = None
    rpi_date = None
    rpi_chip_id = None
    sdram_data = None
    ddr_data = None
    while True:
        data = port.readline().decode('utf-8').strip()
        if data:
            print(f"Received: {data}")
            if obtain_firmware_info:
                if version_pattern.search(data):
                    rpi_version = version_pattern.search(data).group().split(":")[1]
                    print(f"rpi_version: {rpi_version}")
                if date_pattern.search(data):
                    rpi_date = date_pattern.search(data).group().split(":")[1]
                    print(f"rpi_date: {rpi_date}")
                if chip_pattern.search(data):
                    rpi_chip_id = chip_pattern.search(data).group().split(":")[1].strip()
                    print(f"rpi_chip_id: {rpi_chip_id}")
                if "SDRAM" in data:
                    sdram_data = data
                    print(f"SRAM: {sdram_data}")
                if "DDR" in data:
                    ddr_data = data
                    print(f"ddr_data: {ddr_data}")

            if rpi_version and rpi_date and rpi_chip_id and sdram_data and ddr_data:
                print("Successfully obtained bootloader information from UART")
                return RpiBootloaderInfo({
                    "rpi_version": rpi_version,
                    "rpi_date": rpi_date,
                    "rpi_chip_id": rpi_chip_id,
                    "sdram_data": sdram_data,
                    "ddr_data": ddr_data
                })
            if wait_for_login:
                if "login:" in data:
                    print("Successfully reached login prompt")
                    return None
        else:
            print("No data received, waiting 3 seconds...")
            time.sleep(3)

    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 rpi_uart_info_dump.py <device> (e.g. /dev/ttyUSB0)")
        sys.exit(1)

    uart_info_dump(sys.argv[1])
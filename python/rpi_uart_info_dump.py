# assumes UART is connected to RPi5 and is outputting data at 115200 baud rate.

import serial
import time
import sys

'''
TODO: grab the following and compare to known values:
- device IDs
- firmware versions
- other important info
'''
def uart_info_dump(device: str):
    port = serial.Serial(device, 115200, timeout=1)
    while True:
        data = port.readline().decode('utf-8').strip()
        if data:
            print(f"Received: {data}")
        else:
            print("No data received, waiting 3 seconds...")
            time.sleep(3)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 rpi_uart_info_dump.py <device> (e.g. /dev/ttyUSB0)")
        sys.exit(1)

    uart_info_dump(sys.argv[1])
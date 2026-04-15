# This is the main file that tests everything together.
# it will run the UART info dump, the internals check, 
# and the stress test, and gather all the relevant information 
# from each of those tests to create a comprehensive report.
import sys
import subprocess
import rshell

from rpi_internals_check import check_hardware_info, check_io
from rpi_uart_info_dump import uart_info_dump
import rpi_stress_test
import rpi_uart_utils as utils

def _run_rshell_command(port, command):
    # -p defines the port, -c defines the command to run then exit
    full_cmd = ["rshell", "-p", port, "-c", command]
    
    try:
        result = subprocess.run(
            full_cmd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 rpi_uart_info_dump.py <device> (e.g. /dev/ttyUSB0)")
        sys.exit(1)

    # dump UART and obtain firmware info
    device = sys.argv[1]
    bootloader_info = uart_info_dump(device, True)
    # perform the check now that we have all the relevant data
    utils.firmware_comparison_dump(bootloader_info["rpi_version"], bootloader_info["rpi_date"], bootloader_info["rpi_chip_id"])
    # run uart info dump until OS is booted
    bootloader_info = uart_info_dump(device, False)

    '''
    Run the following code using rshell to effectively inject this code
    into the RPi5 and run it there. These tests are designed to run on 
    the RPi5 itself.
    '''
    _run_rshell_command(device, "cp rpi_internals_check.py /pyboard/home/pi/")
    _run_rshell_command(device, "python3 /pyboard/home/pi/rpi_internals_check.py")
    _run_rshell_command(device, "cp rpi_stress_test.py /pyboard/home/pi/")
    _run_rshell_command(device, "python3 /pyboard/home/pi/rpi_stress_test.py")
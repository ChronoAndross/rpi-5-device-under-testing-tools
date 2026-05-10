# This is the main file that tests everything together.
# it will run the UART info dump, the internals check, 
# and the stress test, and gather all the relevant information 
# from each of those tests to create a comprehensive report.
import sys
import subprocess

from rpi_uart_info_dump import uart_info_dump
import rpi_uart_utils as utils

def _run_scp_command(host: str, local_path: str, remote_path: str):
    try:
        process = subprocess.Popen(
            ["scp", local_path, f"{host}:{remote_path}"], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, error = process.communicate()
        print(f"SCP output: {output.decode()}")
        print(f"SCP error: {error.decode()}")
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

def _run_command_over_ssh(host: str, command: str):    
    try:
        process = subprocess.Popen(
            ["ssh", "-t", host, command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, error = process.communicate()
        print(f"Command output: {output.decode()}")
        print(f"Command error: {error.decode()}")
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 rpi_test_suite.py <device> (e.g. /dev/ttyUSB0) <ssh_host> (e.g. pi@raspberrypi)")
        sys.exit(1)

    # dump UART and obtain firmware info
    device = sys.argv[1]
    ssh_host = sys.argv[2]
    bootloader_info = uart_info_dump(device, True)
    # perform the check now that we have all the relevant data
    utils.firmware_comparison_dump(bootloader_info["rpi_version"], bootloader_info["rpi_date"], bootloader_info["rpi_chip_id"])
    # run uart info dump until OS is booted
    bootloader_info = uart_info_dump(device, False, True)

    '''
    Run the following code using scp/ssh to effectively inject this code
    into the RPi5 and run it there. These tests are designed to run on 
    the RPi5 itself.
    '''
    _run_scp_command(ssh_host, "./python/rpi_types.py", "/home/rpi-test/Documents/rpi_types.py")
    _run_scp_command(ssh_host, "./python/rpi_internals_check.py", "/home/rpi-test/Documents/rpi_internals_check.py")
    _run_command_over_ssh(ssh_host, "sudo python3 /home/rpi-test/Documents/rpi_internals_check.py")
    _run_scp_command(ssh_host, "./python/rpi_stress_test.py", "/home/rpi-test/Documents/rpi_stress_test.py")
    _run_command_over_ssh(ssh_host, "sudo python3 /home/rpi-test/Documents/rpi_stress_test.py")

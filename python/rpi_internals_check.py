# check for CPU, RAM, and other hardware information on the RPi5
import subprocess
import RPi.GPIO as GPIO

def check_hardware_info() -> tuple[str, str]:
    print("Checking hardware information...")
    cpu_info = subprocess.run(["cat", "/proc/cpuinfo"], capture_output=True, text=True)
    mem_info = subprocess.run(["cat", "/proc/meminfo"], capture_output=True, text=True)

    print("CPU Information:")
    print(cpu_info.stdout)
    print("Memory Information:")
    print(mem_info.stdout)
    return cpu_info.stdout, mem_info.stdout

def check_io() -> bool:
    print("Checking I/O behavior...")
    GPIO.setmode(GPIO.BCM)
    gpio_pins = range(2, 28)  # GPIO pins 2-27 are typically available on RPi5
    for pin in gpio_pins:
        try:
            GPIO.setup(pin, GPIO.IN)
        except RuntimeError as e:
            print(f"Error occurred while setting up GPIO pin {pin}: {e}")
            return False
    print("GPIO pins set up successfully.")
    return True

if __name__ == "__main__":
    check_hardware_info()
    io_working = check_io()
    if not io_working:
        raise RuntimeError("I/O check failed, terminating tests.")

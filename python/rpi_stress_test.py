# this should create a stress test for the RPi 5 for the following:
# - voltage
# - current
# - power
# - temperature
# after finishing, the test should provide min, max, mean, and standard deviation for each of the above parameters
# and compare them to the expected values for the RPi 5

import pip
import subprocess
import threading
import time

# this should run a simple interrupt for some indeterminate amount of time until cut off by main thread
# Use a thread-safe event to signal the interrupt thread to exit
exit_event = threading.Event()
def sample_interrupt():
    import GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)  # Use GPIO pin 17 for controlling interrupt
    # Loop until main thread signals to stop via `exit_event`
    while not exit_event.is_set():
        if GPIO.output(17, GPIO.HIGH):  # Trigger interrupt
            print("Interrupt triggered!")
        time.sleep(1)  # Wait for 1 second

def install_and_import_python_package(package):
    try:
        __import__(package)
    except ImportError:
        print(f"{package} not found, installing...")
        pip.install(package)
        __import__(package)

def power_consumption_stress_test(test_name: str = "RPi5_Power_Consumption_Stress_Test"):
    class PowerConsumptionResults(dict):
        type: str
        value: float
    print("Starting power consumption stress test...")
    # Start the interrupt in a separate thread
    consuming_function = threading.Thread(target=sample_interrupt, daemon=True)
    consuming_function.start()
    # Run the stress test for a certain duration (e.g., 15 minutes)
    time_start = time.time()
    while time.time() - time_start < 900:  # Run for 900 seconds (15 minutes)
        # Here you would add code to measure voltage, current, and power consumption
        # For example, you could read from a sensor or use a library that interfaces with the hardware
        results = subprocess.run(["vcgencmd", "pmic_read_adc", "temp"], capture_output=True, text=True)  # Example command to measure temperature
        print(f"Power consumption measurement: {results.stdout}")
        lines = results.stdout.split("\n")
        mapped_results : dict[str, list[PowerConsumptionResults]] = {}
        for line in lines:
            elements = line.split("=")
            key = elements[0].split()[0]
            value = float(elements[1].replace("V", "").replace("A", "").strip())
            if key.endswith("_A"):
                key = key[:-2]  # Remove the "_A" suffix
                if key not in mapped_results:
                    mapped_results[key] = []
                mapped_results[key].append({
                    "type": "current",
                    "value": value
                })
            elif key.endswith("_V"):
                key = key[:-2]  # Remove the "_V" suffix
                if key not in mapped_results:
                    mapped_results[key] = []
                mapped_results[key].append({
                    "type": "voltage",
                    "value": value
                })
            else:
                raise ValueError(f"Unexpected key format: {key}")
        time.sleep(1)  # Sleep for a short duration before the next measurement
    
    # signal the interrupt thread to stop and wait briefly for it to exit
    exit_event.set()
    consuming_function.join(timeout=2)
    print("Power consumption stress test completed.")

def temperature_stress_test(test_name: str = "RPi5_Temperature_Stress_Test"):
    install_and_import_python_package("numpy")
    install_and_import_python_package("stressberry")
    print("Starting temperature stress test...")
    results = subprocess.run(["stressberry-run", "-n", test_name, "--duration", "900", "-c", "4", "--output", "out.dat"], capture_output=True, text=True)
    print(f"Stress test completed. Output:\n{results.stdout}")
    
if __name__ == "__main__":
    power_consumption_stress_test()
    #temperature_stress_test()

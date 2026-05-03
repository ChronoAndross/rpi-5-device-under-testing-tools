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
import re

from rpi_types import RpiPowerConsumptionResults

# this should run a simple interrupt for some indeterminate amount of time until cut off by main thread
# Use a thread-safe event to signal the interrupt thread to exit
exit_event = threading.Event()
def sample_interrupt():
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)  # Use GPIO pin 17 for controlling interrupt
    # Loop until main thread signals to stop via `exit_event`
    while not exit_event.is_set():
        if GPIO.output(17, GPIO.HIGH):  # Trigger interrupt
            print("Interrupt triggered!")
        print("wait one second...")
        time.sleep(1)  # Wait for 1 second
    print("exiting sample_interrupt")

def install_and_import_python_package_apt(package: str):
    command = f"sudo apt install {package} -y"
    subprocess.run(command, bufsize=1, shell=True, capture_output=True, text=True)
        
def install_and_import_python_package_pip(package: str, is_app: bool):
    if is_app:
        command = f"pipx install {package}"
        subprocess.run(command, bufsize=1, shell=True)
    else:
        try:
            __import__(package)
        except ImportError:
            print(f"{package} not found, installing...")
            command = f"pipx install {package}"
            subprocess.run(command, bufsize=1, shell=True)
            __import__(package)
            
def ensure_path_pip():
    command = "pipx ensurepath"
    subprocess.run(command, bufsize=1, shell=True)

def start_stressberry(test_name: str, test_duration_sec: str, output_file: str):
    command = f"/root/.local/bin/stressberry-run -n {test_name} --duration {test_duration_sec} -c 4 {output_file}"
    results = subprocess.run(command, bufsize=1, shell=True)

def _graph_power_consumption_results(test_name: str, mapped_results : dict[str, list[RpiPowerConsumptionResults]]):
    print("printing power consumption results")
    install_and_import_python_package_apt("python3-matplotlib")
    import matplotlib.pyplot as plt
    now = time.strftime("%Y-%m-%d_%H-%M-%S")
    # Read the power consumption results from the file and parse them
    for key, results in mapped_results.items():
        _, ax = plt.subplots()
        sorted_results = sorted(results, key=lambda x: x["time"])
        times = list(dict.fromkeys([result["time"] for result in sorted_results]))
        voltage_values = [result["value"] for result in sorted_results if result["type"] == "voltage"]
        current_values = [result["value"] for result in sorted_results if result["type"] == "current"]
        power_values = [voltage * current for voltage, current in zip(voltage_values, current_values)]
        if not current_values or not voltage_values or not power_values:
            print(f"{key} does not have appropriate info to create graph, exiting.")
            continue
        ax.plot(times, current_values, label=f"{key} Current")
        ax.plot(times, voltage_values, label=f"{key} Voltage")
        ax.plot(times, power_values, label=f"{key} Power")
        ax.legend()
        ax.figure.savefig(f"{test_name}_{key}_power_consumption_{now}.png")
    
    # Create a mean for voltage, current, and power for all times in this run
    num_groups = len(mapped_results.values())
    time_voltage_summed = {}
    time_current_summed = {}
    for results in mapped_results.values():
        for result in results:
            if result["type"] == "voltage":
                time_voltage_summed[result["time"]] = time_voltage_summed.get(result["time"], 0) + result["value"]
            elif result["type"] == "current":
                time_current_summed[result["time"]] = time_current_summed.get(result["time"], 0) + result["value"]

    time_power_summed = {time: time_voltage_summed.get(time, 0) * time_current_summed.get(time, 0) for time in times}
    time_voltage_averaged = {time: voltage / num_groups for time, voltage in time_voltage_summed.items()}
    time_current_averaged = {time: current / num_groups for time, current in time_current_summed.items()}
    time_power_averaged = {time: power / num_groups for time, power in time_power_summed.items()}
    _, bx = plt.subplots()
    times = list(set([result["time"] for results in mapped_results.values() for result in results]))
    bx.plot(time_current_averaged.keys(), time_current_averaged.values(), label="Average Current")
    bx.plot(time_voltage_averaged.keys(), time_voltage_averaged.values(), label="Average Voltage")   
    bx.plot(time_power_averaged.keys(), time_power_averaged.values(), label="Average Power")
    bx.legend()
    bx.figure.savefig(f"{test_name}_average_power_consumption_{now}.png")
    print("finishing printing power consumption results")
        

def power_consumption_stress_test(test_name: str = "RPi5_Power_Consumption_Stress_Test"):
    print("Starting power consumption stress test...")
    # Start the interrupt in a separate thread
    consuming_function = threading.Thread(target=sample_interrupt, daemon=True)
    consuming_function.start()
    # Run the stress test for a certain duration (e.g., 15 minutes)
    time_start = time.time()
    # gather these results so we can plot voltage, current, and power together
    mapped_results : dict[str, list[RpiPowerConsumptionResults]] = {}
    while time.time() - time_start < 300:  # Run for 300 seconds (5 minutes)
        # Here you would add code to measure voltage, current, and power consumption
        # For example, you could read from a sensor or use a library that interfaces with the hardware
        results = subprocess.run(["vcgencmd", "pmic_read_adc", "temp"], capture_output=True, text=True)  # Example command to measure temperature
        print(f"Power consumption measurement: {results.stdout}")
        lines = results.stdout.split("\n")
        curr_time = time.time()
        for line in lines:
            if not line:
                continue
            elements = line.split("=")
            key = elements[0].split()[0]
            value = float(elements[1].replace("V", "").replace("A", "").strip())
            if key.endswith("_A"):
                key = key[:-2]  # Remove the "_A" suffix
                if key not in mapped_results:
                    mapped_results[key] = []
                mapped_results[key].append({
                    "type": "current",
                    "value": value,
                    "time": curr_time - time_start
                })
            elif key.endswith("_V"):
                key = key[:-2]  # Remove the "_V" suffix
                if key not in mapped_results:
                    mapped_results[key] = []
                mapped_results[key].append({
                    "type": "voltage",
                    "value": value,
                    "time": curr_time - time_start
                })
            else:
                raise ValueError(f"Unexpected key format: {key}")
        print("Sleeping for 10 seconds before the next measurement...")
        time.sleep(10)  # Sleep for 10 seconds before the next measurement
    
    # signal the interrupt thread to stop and wait briefly for it to exit
    exit_event.set()
    consuming_function.join(timeout=2)
    print("Power consumption stress test completed.")
    _graph_power_consumption_results(test_name, mapped_results)
    
def _temperature_stress_test_output_graph(file_name: str):
    cpu_freqs = []
    temps = []
    times = []
    f = open(file_name, "r")
    lines = f.readlines()
    read_freqs = False
    read_temps = False
    read_times = False
    for line in lines:
        if "cpu frequency:" in line:
            read_freqs = True
            read_temps = False
            read_times = False
        elif "temperature:" in line:
            read_freqs = False
            read_temps = True
            read_times = False
        elif "time:" in line:
            read_freqs = False
            read_temps = False
            read_times = True
        elif "- " in line:
            # read for the specified bool
            if read_freqs:
                cpu_freqs.append(float(line.replace("- ", "").strip()))
            elif read_temps:
                temps.append(float(line.replace("- ", "").strip()))
            elif read_times:
                times.append(float(line.replace("- ", "").strip()))
    
    # plot all accumulated values
    install_and_import_python_package_apt("python3-matplotlib")
    import matplotlib.pyplot as plt
    _, ax = plt.subplots()
    ax.plot(times, temps, label="Temperature (C)")
    ax.plot(times, cpu_freqs, label="CPU Frenquency (MHz)")
    ax.legend()
    file_name_amended = file_name.replace(".dat", "")
    ax.figure.savefig(f"{file_name_amended}.png")
    
        

def temperature_stress_test(test_name: str = "RPi5_Temperature_Stress_Test"):
    install_and_import_python_package_apt("stress")
    install_and_import_python_package_pip("stressberry", True)
    ensure_path_pip()
    print("Starting temperature stress test...")
    now = time.strftime("%Y-%m-%d_%H-%M-%S")
    test_output_file_name = f"{test_name}_{now}.dat"
    # Run stressberry for 5 minutes
    start_stressberry(test_name, "300", test_output_file_name)
    _temperature_stress_test_output_graph(test_output_file_name)
    print("Stress test completed.")

def run_all_tests():
    print("Running all stress tests...")
    install_and_import_python_package_apt("pipx")
    install_and_import_python_package_pip("numpy", False)
    power_consumption_stress_test()
    temperature_stress_test()
    
if __name__ == "__main__":
    run_all_tests()

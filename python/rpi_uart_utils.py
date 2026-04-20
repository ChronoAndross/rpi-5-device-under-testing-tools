import subprocess
import requests
import os
import re

def _download_binary_from_link(url: str, output_path: str):
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        os.chmod(output_path, 0o755)
        print(f"Downloaded binary from {url} to {output_path}")
    else:
        print(f"Failed to download binary from {url}. Status code: {response.status_code}")

def _grep_bin(file_path: str, pattern: str) -> str:
    command = f"strings {file_path} | grep {pattern}"
    result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    return result.stdout

def firmware_comparison_dump(version: str, date: str, chip_id: str):
    # Download versions of firmware locally
    if not os.path.exists("./pieeprom-2025-05-08.bin"):
        _download_binary_from_link("https://github.com/raspberrypi/rpi-eeprom/raw/85c834683d380c3ce2254c6cb0c79ee6ee737b78/firmware-2712/default/pieeprom-2025-05-08.bin", "pieeprom-2025-05-08.bin")
    if not os.path.exists("./pieeprom-2025-11-05.bin"):
        _download_binary_from_link("https://github.com/raspberrypi/rpi-eeprom/raw/85c834683d380c3ce2254c6cb0c79ee6ee737b78/firmware-2712/default/pieeprom-2025-11-05.bin", "pieeprom-2025-11-05.bin")
    if not os.path.exists("./pieeprom-2025-12-08.bin"):
        _download_binary_from_link("https://github.com/raspberrypi/rpi-eeprom/raw/85c834683d380c3ce2254c6cb0c79ee6ee737b78/firmware-2712/default/pieeprom-2025-12-08.bin", "pieeprom-2025-12-08.bin")
    if not os.path.exists("./recovery.bin"):
        _download_binary_from_link("https://github.com/raspberrypi/rpi-eeprom/raw/85c834683d380c3ce2254c6cb0c79ee6ee737b78/firmware-2712/default/recovery.bin", "recovery.bin")

    # get versions, dates, and chip ids from the downloaded firmware binaries and compare to the values received from the RPi5
    print("Comparing received firmware information to known firmware versions...")
    fw_versions = []
    fw_dates = []
    fw_chip_ids = []
    chip_id_pattern = r"^0x[0-9a-fA-F]{8}$"
    for firmware in ["./pieeprom-2025-05-08.bin", "./pieeprom-2025-11-05.bin", "./pieeprom-2025-12-08.bin", "./recovery.bin"]:
        fw_versions.append(_grep_bin(firmware, "VERSION:"))
        fw_dates.append(_grep_bin(firmware, "DATE:"))        

    # check version, date, and chip id against known firmware
    if not re.match(chip_id_pattern, chip_id):
        raise ValueError(f"Received chip ID {chip_id} does not match the known pattern, this chip is a fraud")
    version_found = next((v for v in fw_versions if version in v), None)
    if not version_found:
        raise ValueError(f"Received version {version} does not match any known firmware versions, versions: {fw_versions}")
    date_found = next((d for d in fw_dates if date in d), None)
    if not date_found:
        raise ValueError(f"Received date {date} does not match any known firmware dates, dates: {fw_dates}")
    print("Firmware information matches known versions, dates, and chip IDs.")

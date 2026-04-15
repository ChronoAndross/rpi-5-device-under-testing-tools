import subprocess
import requests

def _download_binary_from_link(url: str, output_path: str):
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded binary from {url} to {output_path}")
    else:
        print(f"Failed to download binary from {url}. Status code: {response.status_code}")

def _grep_bin(file_path: str, pattern: bytes) -> str:
    result = subprocess.run([file_path, "strings", "|", "grep", pattern], check=True, capture_output=True, text=True)
    return result.stdout

def firmware_comparison_dump(version: str, date: str, chip_id: str):
    # Download versions of firmware locally
    _download_binary_from_link("https://github.com/raspberrypi/rpi-eeprom/blob/85c834683d380c3ce2254c6cb0c79ee6ee737b78/firmware-2712/default/pieeprom-2025-05-08.bin", "pieeprom-2025-05-08.bin")
    _download_binary_from_link("https://github.com/raspberrypi/rpi-eeprom/blob/85c834683d380c3ce2254c6cb0c79ee6ee737b78/firmware-2712/default/pieeprom-2025-11-05.bin", "pieeprom-2025-11-05.bin")
    _download_binary_from_link("https://github.com/raspberrypi/rpi-eeprom/blob/85c834683d380c3ce2254c6cb0c79ee6ee737b78/firmware-2712/default/pieeprom-2025-12-08.bin", "pieeprom-2025-12-08.bin")
    _download_binary_from_link("https://github.com/raspberrypi/rpi-eeprom/blob/85c834683d380c3ce2254c6cb0c79ee6ee737b78/firmware-2712/default/recovery.bin", "recovery.bin")

    # get versions, dates, and chip ids from the downloaded firmware binaries and compare to the values received from the RPi5
    print("Comparing received firmware information to known firmware versions...")
    fw_versions = []
    fw_dates = []
    fw_chip_ids = []
    for firmware in ["pieeprom-2025-05-08.bin", "pieeprom-2025-11-05.bin", "pieeprom-2025-12-08.bin", "recovery.bin"]:
        fw_versions.append(_grep_bin(firmware, b"VERSION:"))
        fw_dates.append(_grep_bin(firmware, b"DATE:"))
        fw_chip_ids.append(_grep_bin(firmware, b"chip ID:"))

    # check version, date, and chip id against known firmware
    if not version in fw_versions:
        raise ValueError(f"Received version {version} does not match any known firmware versions, versions: {fw_versions}")
    if not date in fw_dates:
        raise ValueError(f"Received date {date} does not match any known firmware dates, dates: {fw_dates}")
    if not chip_id in fw_chip_ids:
        raise ValueError(f"Received chip ID {chip_id} does not match any known firmware chip IDs, chip IDs: {fw_chip_ids}")
    print("Firmware information matches known versions, dates, and chip IDs.")

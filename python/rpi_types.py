from typing import Optional

class RpiBootloaderInfo(dict):
    rpi_version: Optional[str]
    rpi_date: Optional[str]
    rpi_chip_id: Optional[str]
    sdram_data: Optional[str]
    ddr_data: Optional[str]

class RpiPowerConsumptionResults(dict):
    type: str
    value: float
    time: float
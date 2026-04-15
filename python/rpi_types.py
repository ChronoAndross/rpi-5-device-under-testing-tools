class RpiBootloaderInfo(dict):
    rpi_version: str | None
    rpi_date: str | None
    rpi_chip_id: str | None
    sdram_data: str | None
    ddr_data: str | None

class RpiPowerConsumptionResults(dict):
    type: str
    value: float
    time: float
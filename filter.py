import csv
import sys
import os

class pwrlogdata:
    
    def __init__(self, input_file):
        self.input_file = input_file

        with open(input_file, "r", newline="",
            encoding="utf-8-sig") as infile:

            reader = csv.reader(infile)
            self.header = next(reader)
            self.rows = list(reader)

    def trimmer(self, patterns, exclude_check=()):

        key_index = self.header.index("Key")

        return [
            row for row in self.rows
            if key_index < len(row)
            and any(p in row[key_index] for p in patterns)
            and not any(e in row[key_index] for e in exclude_check)
        ]

    def pwr_trim(self):

        self.pwr_raw = self.trimmer(
            patterns=("Supply Current", "SupplyCurrent",
                      "BatteryVoltage"),
            exclude_check=("DriveSupplyCurrent",)
        )

        return self.pwr_raw

    def pwr_filter(self, current_groups=None):
        # Uses self.battery_raw, NOT self.rows
        # Process and align battery signals here
        pass

"""def can(file):
    patterns = (
         # Utilization
        "BusUtilization",
        "CANUtilization",

        # Communication errors
        "BusOffCount",
        "TxFullCount",
        "BusErrorCount",
        "ArbitrationLostCount",
        "RestartCount",

        # Error counters
        "REC",
        "TEC",
        "receiveErrorCount",
        "transmitErrorCount",

        # Signal health
        "SignalAgeMs",
        "SignalStatusOK",

        # Bus state
        "CANState",
    )

    output_file = os.path.splitext(file)[0] + "_filter_can.csv"

    trimmer(file, output_file, patterns)"""
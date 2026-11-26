import csv
import sys
from openpyxl import Workbook
from openpyxl.chart import ScatterChart, Reference, Series
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
        
        if not hasattr(self, "pwr_raw"):
            raise RuntimeError("Run pwr_trim() before pwr_filter().")

        # Find column indexes
        timestamp_index = self.header.index("Timestamp")
        key_index = self.header.index("Key")
        value_index = self.header.index("Value")

        # Identify unique current and voltage signals
        current_keys = set()
        voltage_keys = set()

        events = {}

        for row in self.pwr_raw:

            if max(timestamp_index, key_index, value_index) >= len(row):
                continue

            timestamp = float(row[timestamp_index])
            key = row[key_index]

            try:
                value = float(row[value_index])
            except ValueError:
                continue

            events.setdefault(timestamp, {})[key] = value

            if "supply current" in key.lower() or "supplycurrent" in key.lower():
                current_keys.add(key)

            if "batteryvoltage" in key.lower() or "battery voltage" in key.lower():
                voltage_keys.add(key)

        current_keys = sorted(current_keys)
        voltage_keys = sorted(voltage_keys)

        # Print detected current signals and their sample counts
        print("\n--- Current Signal Diagnostics ---")

        for key in current_keys:
            sample_count = sum(
                1 for row in self.pwr_raw
                if len(row) > key_index and row[key_index] == key
            )

            print(f"{sample_count:5} samples | {key}")

        print(f"\nTotal unique current signals: {len(current_keys)}")
        print("----------------------------------\n")
        
        if not current_keys:
            raise ValueError("No Supply Current signals found.")

        if not voltage_keys:
            raise ValueError("No Battery Voltage signal found.")

        # Match optional current groups to actual signal paths
        matched_groups = {}

        if current_groups:
            for group_name, selectors in current_groups.items():

                matched = [
                    key for key in current_keys
                    if any(selector.lower() in key.lower()
                        for selector in selectors)
                ]

                if not matched:
                    raise ValueError(
                        f"No current signals found for {group_name}"
                    )

                matched_groups[group_name] = matched

        # Align signals by timestamp
        latest_values = {}
        chart_data = []

        for timestamp in sorted(events):

            latest_values.update(events[timestamp])

            # Wait until all current signals have an initial reading
            if not all(key in latest_values for key in current_keys):
                continue

            total_current = sum(
                latest_values[key] for key in current_keys
            )

            battery_voltage = latest_values[voltage_keys[0]]

            output_row = [
                timestamp,
                battery_voltage,
                total_current
            ]

            # Calculate optional current groups
            for group_name, keys in matched_groups.items():

                group_current = sum(
                    latest_values[key] for key in keys
                    if key in latest_values
                )

                output_row.append(group_current)

            chart_data.append(output_row)

        # Save chart data in the object
        self.pwr_chart_header = [
            "Timestamp (s)",
            "Battery Voltage (V)",
            "Total Current (A)"
        ]

        self.pwr_chart_header.extend(
            f"{name} (A)" for name in matched_groups
        )

        self.pwr_chart_data = chart_data

        return self.pwr_chart_data

    def pwr_export_csv(self, output_file):

        with open(output_file, "w", newline="", encoding="utf-8") as outfile:

            writer = csv.writer(outfile)

            writer.writerow(self.pwr_chart_header)
            writer.writerows(self.pwr_chart_data)

        print(f"Saved chart data to: {output_file}")

    def pwr_export_xlsx(self, output_file):

        if not hasattr(self, "pwr_raw"):
            raise RuntimeError("Run pwr_trim() first.")

        if not hasattr(self, "pwr_chart_data"):
            raise RuntimeError("Run pwr_filter() first.")

        workbook = Workbook()

        # Raw data worksheet
        raw_sheet = workbook.active
        raw_sheet.title = "Power Raw"

        raw_sheet.append(self.header)

        for row in self.pwr_raw:
            raw_sheet.append(row)

        # Chart data worksheet
        data_sheet = workbook.create_sheet("Power Chart Data")

        data_sheet.append(self.pwr_chart_header)

        for row in self.pwr_chart_data:
            data_sheet.append(row)

        # Timestamp reference
        timestamps = Reference(
            data_sheet,
            min_col=1,
            min_row=2,
            max_row=data_sheet.max_row
        )

        # Voltage data reference
        voltage_data = Reference(
            data_sheet,
            min_col=2,
            min_row=2,
            max_row=data_sheet.max_row
        )

        # Current data reference
        current_data = Reference(
            data_sheet,
            min_col=3,
            min_row=2,
            max_row=data_sheet.max_row
        )

        # Save workbook
        workbook.save(output_file)

        print(f"Saved Excel workbook to: {output_file}")
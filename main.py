from filter import pwrlogdata
import sys
import os

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py file.csv")
        sys.exit(1)

    log = pwrlogdata(sys.argv[1])

    # Process battery data
    log.pwr_trim()
    log.pwr_filter()

    # Generate Excel workbook
    output_file = os.path.splitext(sys.argv[1])[0] + "_analysis.xlsx"

    log.pwr_export_xlsx(output_file)

    print(f"Chart rows: {len(log.pwr_chart_data)}")

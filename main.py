from filter import pwrlogdata
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py file.csv")
        sys.exit(1)

    log = pwrlogdata(sys.argv[1])

    log.pwr_raw = log.pwr_trim()

    print(f"Selected {len(log.pwr_raw)} power signal rows.")
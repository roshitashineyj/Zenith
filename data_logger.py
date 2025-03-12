import serial
import time
import csv
import re  # Import regular expressions to extract pH value

SERIAL_PORT = "COM3"  # Update this with your correct COM port
BAUD_RATE = 9600
CSV_FILE_PATH = r"C:\Zenith\sensor_datas.csv"


def extract_ph_value(raw_ph):
    """Extracts only the numerical pH value from a string."""
    match = re.search(r"PH:\s*([\d.]+)", raw_ph)  # Find "PH: 37.65" and extract 37.65
    return match.group(1) if match else "N/A"  # Return extracted value or "N/A" if not found


def read_serial_data():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=5)
    time.sleep(2)  # Allow connection to establish

    # Overwrite file initially to ensure a fresh start
    with open(CSV_FILE_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["MoisturePercentage", "Temperature", "Humidity", "pH"])  # Column headers

    while True:
        try:
            raw_data = ser.readline().decode('ascii', errors='ignore').strip()
            print(f"Raw Data: {raw_data}")  # Debugging output

            if raw_data and not raw_data.startswith("MoisturePercentage"):
                values = raw_data.split(",")

                if len(values) >= 3:  # Ensure at least three values are present
                    moisture = values[0].strip()
                    temperature = values[1].strip()
                    humidity = values[2].strip()

                    # Extract only the numerical pH value if available
                    ph_value = extract_ph_value(values[3]) if len(values) > 3 else "N/A"

                    with open(CSV_FILE_PATH, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([moisture, temperature, humidity, ph_value])
                        print(f"Logged: {[moisture, temperature, humidity, ph_value]}")

            time.sleep(10)  # Log every 30 minutes
        except KeyboardInterrupt:
            print("Logging stopped.")
            break

    ser.close()


if __name__ == "__main__":
    read_serial_data()

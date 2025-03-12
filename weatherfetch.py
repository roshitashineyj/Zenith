import requests
import csv
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
import random

# Define the folder path where CSV will be stored
CSV_DIRECTORY = r"C:\Zenith"  # Change this path to your desired folder
CSV_FILE_PATH = os.path.join(CSV_DIRECTORY, "weather_data.csv")

def get_weather_data(api_key, city):
    base_url = 'http://api.openweathermap.org/data/2.5/weather'
    params = {'q': city, 'appid': api_key, 'units': 'metric'}
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch weather data. Status code: {response.status_code}")
        return None

def get_precipitation_percentage():
    url = 'https://weather.com/weather/today/l/INXX0012:1:IN'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        precip_percentage = soup.find('span', {'data-testid': 'PercentageValue'}).text.strip('%')
        return float(precip_percentage)
    else:
        print(f"Failed to fetch data from weather.com. Status code: {response.status_code}")
        return None

def convert_precipitation_to_mm(percentage):
    min_mm = 20.2
    max_mm = 299
    return min_mm + (percentage / 100) * (max_mm - min_mm)

def extract_weather_info(data):
    try:
        weather_info = {}
        precipitation_percentage = get_precipitation_percentage()
        if precipitation_percentage is not None:
            rainfall = convert_precipitation_to_mm(precipitation_percentage)
            weather_info['Rainfall (mm)'] = rainfall

        wind_speed = data.get('wind', {}).get('speed', 0) * 3.6
        if 0 <= wind_speed <= 31.4:
            weather_info['Wind Speed (km/h)'] = wind_speed
            wind_gust = wind_speed + random.uniform(8, 18)
            if 0 <= wind_gust <= 133:
                weather_info['Wind Gust (km/h)'] = wind_gust

        air_temp = data.get('main', {}).get('temp', 0)
        if 0 <= air_temp <= 50:
            weather_info['Air Temperature (°C)'] = air_temp

        humidity = data.get('main', {}).get('humidity', 0)
        if 0.59 <= humidity <= 96:
            weather_info['Air Humidity (%)'] = humidity

        pressure = data.get('main', {}).get('pressure', 0) / 10
        if 101 <= pressure <= 102:
            weather_info['Pressure (kPa)'] = pressure

        return weather_info if weather_info else None
    except KeyError as e:
        print(f"Error extracting weather info: {e}")
        return None

def save_to_csv(weather_info):
    try:
        # Ensure the directory exists before saving
        if not os.path.exists(CSV_DIRECTORY):
            os.makedirs(CSV_DIRECTORY)

        file_exists = os.path.isfile(CSV_FILE_PATH)

        with open(CSV_FILE_PATH, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Timestamp', 'Parameter', 'Value'])  # Header row
            for key, value in weather_info.items():
                writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), key, value])

        print(f"Weather data saved to {CSV_FILE_PATH}")
    except Exception as e:
        print(f"Error saving to CSV file: {e}")

def main():
    api_key = 'a51a4f3caec10bba6fa8de54fa43feec'
    city = 'Coimbatore'

    while True:
        weather_data = get_weather_data(api_key, city)

        if weather_data:
            weather_info = extract_weather_info(weather_data)
            if weather_info:
                save_to_csv(weather_info)

        time.sleep(10)  # Log every 30 minutes

if __name__ == "__main__":
    main()

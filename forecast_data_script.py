import requests
import mysql.connector
import logging
import time

# Set up logging for debugging purposes
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# MySQL Database Configuration
db_config = {
    "host": "XXXXX",
    "user": "root",
    "password": "XXXXXXX",
    "database": "weather_data"
}


# OpenWeatherMap API Configuration
openweather_api_key = 'XXXXXXXXXXX'

# Function to fetch all city names from the user_preferences table
def fetch_cities_from_db():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT DISTINCT city FROM user_preferences"
        cursor.execute(query)
        cities = [row[0] for row in cursor.fetchall()]
        logging.info(f"Fetched cities from user_preferences: {cities}")
        return cities
    except mysql.connector.Error as err:
        logging.error(f"MySQL error: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

# Function to get latitude and longitude of the city using Geocoding API
def get_lat_lon(city):
    try:
        geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={openweather_api_key}"
        response = requests.get(geocode_url)
        response.raise_for_status()
        geocode_data = response.json()

        if geocode_data and len(geocode_data) > 0:
            lat = geocode_data[0]['lat']
            lon = geocode_data[0]['lon']
            logging.info(f"Geocoded {city}: lat={lat}, lon={lon}")
            return lat, lon
        else:
            logging.warning(f"No geocoding results for city: {city}")
            return None, None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching geocoding for {city}: {e}")
        return None, None

# Function to fetch 5-day weather forecast for a given latitude and longitude
def fetch_5_day_forecast(lat, lon):
    try:
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={openweather_api_key}"
        response = requests.get(forecast_url)
        response.raise_for_status()
        forecast_data = response.json()
        logging.info(f"Successfully fetched forecast for lat={lat}, lon={lon}")
        return forecast_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching forecast data for lat={lat}, lon={lon}: {e}")
        return None

# Function to store forecast data in the weather_forecast table
def store_forecast_in_db(city, forecast_data):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        for forecast in forecast_data['list']:
            dt_txt = forecast['dt_txt']
            temperature = forecast['main']['temp']
            temp_min = forecast['main']['temp_min']
            temp_max = forecast['main']['temp_max']
            humidity = forecast['main']['humidity']
            wind_speed = forecast['wind']['speed']
            weather_condition = forecast['weather'][0]['description']

            query = """
                INSERT INTO weather_forecast (city, forecast_time, temperature, temp_min, temp_max, humidity, wind_speed, weather_condition)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (city, dt_txt, temperature, temp_min, temp_max, humidity, wind_speed, weather_condition)
            cursor.execute(query, values)

        conn.commit()
        logging.info(f"Stored forecast data for city: {city}")
    except mysql.connector.Error as err:
        logging.error(f"MySQL error: {err}")
    finally:
        cursor.close()
        conn.close()

# Main function to coordinate the process
def main():
    logging.info("Starting 5-day weather forecast data collection...")
    cities = fetch_cities_from_db()

    if not cities:
        logging.warning("No cities found in user preferences. Exiting script.")
        return

    for city in cities:
        try:
            logging.info(f"Processing city: {city}")
            lat, lon = get_lat_lon(city)
            if lat is None or lon is None:
                logging.warning(f"Skipping city {city} due to missing lat/lon.")
                continue

            forecast_data = fetch_5_day_forecast(lat, lon)
            if forecast_data:
                store_forecast_in_db(city, forecast_data)
        except Exception as e:
            logging.error(f"An error occurred while processing city {city}: {e}")
        time.sleep(2)  # Adding delay to avoid hitting API rate limits

    logging.info("Weather forecast data collection complete.")

if __name__ == "__main__":
    main()

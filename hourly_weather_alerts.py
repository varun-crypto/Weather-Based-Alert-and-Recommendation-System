import redis
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import mysql.connector
import json

# Redis Configuration
redis_host = "xxxxx"  # Replace with your Redis instance IP
redis_port = 6379

# OpenWeather API key
openweather_api_key = 'xxxxxxx'

# Email configuration
email_sender = "xxxxxxx"
email_password = "xxxxx"


# Database configuration
db_config = {
    "host": "xxxxx",
    "user": "root",
    "password": "xxxxx",
    "database": "weather_data"
}

# Connect to Redis
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = email_sender
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email_sender, email_password)
            server.sendmail(email_sender, to_email, msg.as_string())
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")

def fetch_weather_data(city):
    geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={openweather_api_key}"
    print(f"Fetching coordinates for city: {city} using {geocoding_url}")
    response = requests.get(geocoding_url)
    geo_data = response.json()
    
    if not geo_data:
        print("No coordinates found for the city.")
        return None
    
    lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]
    print(f"Coordinates for {city}: {lat}, {lon}")
    
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={openweather_api_key}&units=metric"
    print(f"Fetching weather data using URL: {weather_url}")
    weather_response = requests.get(weather_url)
    weather_data = weather_response.json()
    
    if weather_response.status_code != 200:
        print(f"Error fetching weather data: {weather_data}")
        return None
    
    print("Weather data fetched successfully")
    return weather_data

def process_weather_check():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM user_preferences")
        user_preferences = cursor.fetchall()
        
        print(f"User preferences retrieved: {user_preferences}")
        
        for user in user_preferences:
            city = user["city"]
            weather_data = fetch_weather_data(city)
            if not weather_data:
                continue
            
            temp = weather_data["main"]["temp"]
            wind_speed = weather_data["wind"]["speed"]
            rain_alert = 1 if "rain" in weather_data else 0
            
            print(f"Weather data for {city}: temp={temp}, wind_speed={wind_speed}, rain_alert={rain_alert}")
            
            if (
                temp >= user["temp_min"]
                and temp <= user["temp_max"]
                and wind_speed <= user["wind_max"]
                and (not user["rain_alert"] or rain_alert)
            ):
                print(f"Weather conditions match user preferences for {user['email']}")
                
                redis_key = f"weather_alert:{user['user_id']}"
                redis_value = {
                    "city": city,
                    "temp": temp,
                    "wind_speed": wind_speed,
                    "rain_alert": rain_alert
                }
                redis_client.set(redis_key, json.dumps(redis_value))
                print(f"Stored alert in Redis under key: {redis_key}")
                
                email_body = f"Weather Alert!\nCity: {city}\nTemperature: {temp}°C\nWind Speed: {wind_speed} m/s\nRain Alert: {'Yes' if rain_alert else 'No'}"
                send_email(user["email"], "Weather Alert", email_body)
            else:
                print(f"No matching conditions for {user['email']}")
    except Exception as e:
        print(f"Error during weather check: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Starting hourly weather check...")
    process_weather_check()
    print("Hourly weather check completed.")
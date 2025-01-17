import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Database Configuration
# Database configuration
db_config = {
    "host": "XXXXX",
    "user": "root",
    "password": "XXXXXX",
    "database": "weather_data"
}


# Email configuration
email_sender = "XXXXXXXX"
email_password = "XXXXXXXX"


# Email Sending Function
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
        print(f"Failed to send email to {to_email}: {e}")

# Daily Recommendations Function
def process_daily_recommendations():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Fetch user preferences
        cursor.execute("SELECT * FROM user_preferences")
        user_preferences = cursor.fetchall()
        
        print("Processing user preferences...")
        sent_emails = set()  # Track sent email-city pairs

        for user in user_preferences:
            city = user["city"]
            email = user["email"]
            
            # Create a unique key for email and city
            email_city_key = f"{email}-{city}"
            
            # Skip if email-city combination was already sent
            if email_city_key in sent_emails:
                print(f"Skipping duplicate email for {email} in city {city}")
                continue

            # Fetch forecast data for the city for the next day
            cursor.execute(
                """
                SELECT * FROM weather_forecast 
                WHERE city = %s AND forecast_time >= NOW() + INTERVAL 1 DAY 
                AND forecast_time < NOW() + INTERVAL 2 DAY
                """, 
                (city,)
            )
            forecast_data = cursor.fetchall()
            
            if not forecast_data:
                print(f"No forecast data available for {city} tomorrow.")
                continue
            
            recommendation_found = False
            for forecast in forecast_data:
                temp = forecast["temperature"]
                wind_speed = forecast["wind_speed"]
                weather_condition = forecast["weather_condition"]
                rain_alert = "rain" in weather_condition.lower()
                
                # Check user preferences
                if (
                    user["temp_min"] <= temp <= user["temp_max"]
                    and wind_speed <= user["wind_max"]
                    and (not user["rain_alert"] or rain_alert)
                ):
                    # Send recommendation email
                    recommendation_found = True
                    email_body = (
                        f"Good news! Tomorrow in {city} is a great day for outdoor activities.\n\n"
                        f"Temperature: {temp}°C\n"
                        f"Wind Speed: {wind_speed} m/s\n"
                        f"Weather Condition: {weather_condition.capitalize()}\n\n"
                        f"Enjoy your day!"
                    )
                    send_email(email, "Weather Recommendation", email_body)
                    sent_emails.add(email_city_key)  # Mark email-city as sent
                    print(f"Recommendation email sent to {email} for city {city}.")
                    break
            
            if not recommendation_found:
                # Send unfavorable conditions email
                email_body = (
                    f"Weather Alert for {city}:\n\n"
                    f"Unfortunately, weather conditions tomorrow do not seem favorable for outdoor activities.\n"
                    f"We recommend staying indoors or planning your activities accordingly.\n\n"
                    f"Stay safe!"
                )
                send_email(email, "Weather Update: Stay Indoors", email_body)
                sent_emails.add(email_city_key)  # Mark email-city as sent
                print(f"No suitable recommendations for {email} for city {city}. Alert email sent.")
    except Exception as e:
        print(f"Error during daily recommendations process: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Starting daily recommendations script...")
    process_daily_recommendations()
    print("Daily recommendations completed.")

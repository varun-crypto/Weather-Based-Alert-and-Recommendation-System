from flask import Flask, request, render_template, redirect, url_for, jsonify
import mysql.connector
import os

app = Flask(__name__)

# MySQL Database Configuration
db_config = {
    "host": "XXXXXX",
    "user": "root",
    "password": "XXXXXX",
    "database": "weather_data"
}

# Home route - displays the form
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# Route to set user preferences
@app.route('/set_preferences', methods=['POST'])
def set_preferences():
    user_id = request.form['user_id']
    city = request.form['city']
    email = request.form['email']
    temp_min = request.form['temp_min']
    temp_max = request.form['temp_max']
    wind_max = request.form['wind_max']
    rain_alert = request.form['rain_alert']

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = """
        INSERT INTO user_preferences (user_id, city, email, temp_min, temp_max, wind_max, rain_alert)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, city, email, temp_min, temp_max, wind_max, rain_alert))
        conn.commit()
        return redirect(url_for('confirmation'))
    except mysql.connector.Error as err:
        return f"Error: {str(err)}", 500
    finally:
        cursor.close()
        conn.close()

# Confirmation page
@app.route('/confirmation', methods=['GET'])
def confirmation():
    return render_template('confirmation.html')

# Route to retrieve user preferences
@app.route('/get_preferences/<user_id>', methods=['GET'])
def get_preferences(user_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM user_preferences WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result:
            return render_template('preferences.html', preferences=result)
        else:
            return "User not found", 404
    except mysql.connector.Error as err:
        return f"Error: {str(err)}", 500
    finally:
        cursor.close()
        conn.close()

# Test database connection route
@app.route('/test_db', methods=['GET'])
def test_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        return jsonify({"message": f"Connected to database: {db_name[0]}"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Route for hourly alerts
@app.route('/run_hourly_alerts', methods=['POST'])
def run_hourly_alerts():
    os.system("python3 hourly_weather_alerts.py")
    return jsonify({"message": "Hourly weather alerts script triggered"}), 200

# Route for daily recommendations
@app.route('/run_daily_recommendations', methods=['POST'])
def run_daily_recommendations():
    os.system("python3 daily_weather_recommendations.py")
    return jsonify({"message": "Daily recommendations script triggered"}), 200

# Route for forecast data update
@app.route('/run_forecast_update', methods=['POST'])
def run_forecast_update():
    os.system("python3 forecast_data_script.py")
    return jsonify({"message": "Forecast data update script triggered"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

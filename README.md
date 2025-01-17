# Weather Alert and Recommendation System
This project is a cloud-based weather notification system that sends personalized weather alerts and recommendations to users based on their preferences. It uses OpenWeather API to fetch real-time weather data and forecasts and integrates them with a Flask application hosted on Google Cloud.

# Team Member:

## Varun Mallela

### The key functionalities include:

- Hourly weather checks to send alerts when conditions match user preferences.
- Daily recommendations for outdoor activities based on the next day's weather forecast based on the set user preferences
- Dynamic front-end for users to set their preferences and view alerts.
  
#### The application is fully deployed on Google Cloud and uses the following components:

- Google Compute Engine: To host the Flask application and scripts.
- Google SQL: To store user preferences and weather data.
- Redis: For temporary storage of weather alerts.
- Google Cloud Scheduler: To automate the execution of scripts at scheduled times.

## Prerequisites and Requirements

TO get all the files, you can donwload the zip from github and then upload the app and script files into the VM instance by using ssh or you can use git clone to get the files into the VM instance. Specifically, we need the app.py, templates folder and the three scripts - daily_weather_recommendations.py, forecast_data_script.py, hourly_weather_alerts.py

Before setting up the application, ensure the following requirements are met:

Make sure replace various thinngs in the script with your username, password, API keys, instance external IP, redis Pivate Ip.

### 1. Google Cloud Platform (GCP) Project:

Create a new project in GCP specifically for this application to keep resources organized.

### 2. Compute Instance:

Instance Type: e2-micro

Region: us-central1

Operating System: Ubuntu 20.04 LTS or later

### 3. SQL Database:

Database Type: MySQL

MySQL Version: 8.0

Storage Capacity: 100 GB

Region: us-central1

Connections: Public IP must be enabled to allow the Compute Engine instance to access it.

Firewall Rule: A firewall rule must be set to allow access to the SQL instance from the Compute Engine instance.

### 4. MemoryStore Redis:

Capacity: 1 GB

Region: us-central1

Private IP: Private Service Access must be enabled.

### 5. Firewall Rules:

Redis: Create a firewall rule to allow traffic for TCP:6379.

Flask: Create a firewall rule to allow traffic for TCP:5000.

SQL: Ensure the SQL instance is configured to allow public IP access and authorize access to the Compute Engine's external IP.

### 6. OpenWeather API Key:

Register on OpenWeather and generate an API key to fetch weather data.

You can get the api key by signing up here: https://home.openweathermap.org/users/sign_up

### 7. SSH Access:

Enable SSH to access the Compute Engine instance for deploying and running the application.

#### First ssh to the vm instance and do the following:

Make sure to first install python:
```
sudo apt-get install -y python3 python3-pip
```

### 8. Python Environment:

Python Version: 3.8 or later

Required Libraries: Flask, mysql-connector-python, redis, smtplib, requests, email.mime

Using pip install the above mentioned packages.

## Cloud Deployment Setup

### Step 1: Create a VM Instance

1. Navigate to Compute Engine > VM Instances.
2. Click Create Instance and configure as follows:

- Name: flask-weather-app
- Machine Type: e2-micro
- Region: us-central1
- Operating System: Ubuntu 20.04 LTS
- Disk: 20 GB standard persistent disk
- Network Tags: Add the tag allow-flask
  
3. After creation, note the External IP Address as you will use it to access your app.

### Step 2: Set Up SQL Database

1. Navigate to SQL > Create Instance.
2. Select MySQL as the database type and configure:
   
- Name: weather-data
- MySQL Version: 8.0
- Region: us-central1
- Storage Capacity: 100 GB
- Connections: Enable Public IP under connections.
- Authorize Network: Allow access from the external IP of your Compute Engine instance.

3. Create a new database:
   
 - Go to Databases and click Create Database.
 - Name the database: weather_data.
   
4. Connect to SQL Database:
 
 - Open the Cloud Shell or use a MySQL client.
 - Run the following commands:
  ```
  mysql -h <INSTANCE_IP> -u root -p
  ```
5. Create Tables:
   - Select the database:
     ```
     USE weather_data;
     ```
   - Create the user_preferences table:
     ```
     CREATE TABLE user_preferences (
     user_id VARCHAR(255) PRIMARY KEY,
     city VARCHAR(255) NOT NULL,
     email VARCHAR(255) NOT NULL,
     temp_min FLOAT NOT NULL,
     temp_max FLOAT NOT NULL,
     wind_max FLOAT NOT NULL,
     rain_alert BOOLEAN NOT NULL
      );
     ```
   - Create the weather_forecast table:
     ```
       CREATE TABLE weather_forecast (
       id INT AUTO_INCREMENT PRIMARY KEY,
       city VARCHAR(255),
       forecast_time DATETIME,
       temperature FLOAT,
       temp_min FLOAT,
       temp_max FLOAT,
       humidity INT,
      wind_speed FLOAT,
      weather_condition VARCHAR(255)
       );
      ```

### Step 3: Create Redis Instance

1. Navigate to MemoryStore > Redis > Create Instance.
2. Configure the instance as follows:
- Name: weather-redis
- Capacity: 1 GB
- Region: us-central1
- Private Service Access: Enable this to restrict access to internal services only.
3. Note the Internal IP Address of the Redis instance. This will be used in your application code.

### Step 4: Set Up Firewall Rules

1. #### Redis:

- Navigate to Firewall Rules.
- Click Create Firewall Rule.
- Name: allow-redis
- Targets: All instances in the network.
- Source IP Ranges: 10.0.0.0/8
- Protocols and Ports: Allow TCP on port 6379.

2. #### Flask:

- Name: allow-flask
- Targets: All instances.
- Source IP Ranges: 0.0.0.0/0
- Protocols and Ports: Allow TCP on port 5000.

3. #### SQL:

- Ensure SQL instance is configured to allow public IP access.
- Add the external IP of your Compute Engine to the authorized networks.

### Step 5: Run the Flask Application

1. SSH into the VM instance and navigate to the folder where flask app is present.
2. Run the Flask app:
   ```
   nohup python3 app.py &
   ```
   The above command ensure that the flask keep running in backgroud. You can safely code the SHH window now.


## Cloud Scheduler Setup

#### Purpose: Automate the running of 3 Python scripts on a schedule.

### Step 1: Create 3 Jobs

1. Go to Cloud Scheduler and click Create Job.
   
### Job 1: Hourly Weather Alerts

- Name: hourly-weather-alerts
- Frequency: Every hour (e.g., 0 * * * * for once every hour)
- URL: http://<EXTERNAL_IP>:5000/run_hourly_alerts
- HTTP Method: POST

#### Job 2: Daily Weather Forecast

- Name: daily-weather-forecast
- Frequency: Once every day (e.g., 0 0 * * * for 12:00 AM daily)
- URL: http://<EXTERNAL_IP>:5000/run_daily_forecast
- HTTP Method: POST

### Job 3: Daily Recommendations

- Name: daily-weather-recommendations
- Frequency: Once every day (e.g., 0 8 * * * for 8:00 AM daily)
- URL: http://<EXTERNAL_IP>:5000/run_daily_recommendations
- HTTP Method: POST

### Step 2: Testing the Scheduled Jobs Using cURL

To test if the scheduled jobs are working as expected, you can manually trigger the jobs using cURL commands. This allows you to verify that the Flask endpoints are functioning correctly.

Before you proceed make sure to first set preference by visiting: 

```
http://<EXTERNAL_IP>:5000/
```

### Job 1: Hourly Weather Alerts

Run the following command to trigger the Hourly Weather Alerts:

```
curl -X POST http://<EXTERNAL_IP>:5000/run_hourly_alerts
```

Expected Result:

You should see a success message in the console.

Check your email (if you have alerts set up) to see if you received the weather alert.

#### Job 2: Daily Weather Forecast

Run the following command to trigger the Daily Weather Forecast:

```
curl -X POST http://<EXTERNAL_IP>:5000/run_forecast_update
```

Expected Result:

You should see a success message in the console.

Weather forecast data should be updated in the weather_forecast table in your MySQL database.

#### Job 3: Daily Recommendations

Run the following command to trigger the Daily Recommendations:

````
curl -X POST http://<EXTERNAL_IP>:5000/run_daily_recommendations
````

Expected Result:

You should see a success message in the console.
You will receive an email with daily recommendations for outdoor activities based on user preferences and weather forecasts.

## Verifying the Logs

After running the cURL commands, you can check if the endpoints ran successfully by viewing the logs.

1. View logs using Google Cloud Console:

- Go to Cloud Logging in GCP.
- Filter by resource type: Cloud Scheduler Job.

2. Check Email:
   
- Check if you received weather alerts or recommendations via email.

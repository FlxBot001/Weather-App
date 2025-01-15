# Imports
import os
import json
import boto3
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from a .env file
# This helps keep sensitive information like API keys secure and out of the codebase
load_dotenv()

class WeatherDashboard:
    """A class to fetch weather data from OpenWeather API and save it to an AWS S3 bucket."""

    def __init__(self):
        # Initialize the WeatherDashboard instance
        # Load the OpenWeather API key and AWS S3 bucket name from environment variables
        self.api_key = os.getenv('OPENWEATHER_API')
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')

        # Create an S3 client using boto3 to interact with AWS S3 service
        self.s3_client = boto3.client('s3', region_name=os.getenv('AWS_REGION'))

    def create_bucket_if_not_exists(self):
        """
        Create an S3 bucket if it doesn't already exist.
        AWS S3 buckets must have a unique name globally, so check if it exists first.
        """
        try:
            # Check if the bucket already exists by attempting to get its metadata
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"Bucket {self.bucket_name} exists")
        except:
            # If the bucket doesn't exist, create it
            print(f"Creating bucket {self.bucket_name}")
        
        try:
            # Create the bucket using the S3 client
            # In the 'us-east-1' region, you can use a simplified bucket creation method
            self.s3_client.create_bucket(Bucket=self.bucket_name)
            print(f"Successfully created bucket {self.bucket_name}")
        except Exception as e:
            # Handle any errors that occur during bucket creation
            print(f"Error creating bucket: {e}")

    def fetch_weather(self, city):
        """
        Fetch weather data for a given city from the OpenWeather API.
        
        Parameters:
            city (str): The name of the city to fetch weather data for.
        
        Returns:
            dict: The weather data in JSON format, or None if an error occurs.
        """
        # Define the base URL for the OpenWeather API's current weather endpoint
        base_url = "http://api.openweathermap.org/data/2.5/weather"

        # Set up the request parameters, including the city name, API key, and units (imperial for Fahrenheit)
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "imperial"
        }

        try:
            # Make a GET request to the OpenWeather API with the specified parameters
            response = requests.get(base_url, params=params)

            # Raise an exception if the response contains an HTTP error status
            response.raise_for_status()

            # Return the weather data as a JSON object
            return response.json()
        except requests.exceptions.RequestException as e:
            # Print an error message if the API request fails
            print(f"Error fetching weather data: {e}")
            return None

    def save_to_s3(self, weather_data, city):
        """
        Save weather data to an AWS S3 bucket.
        
        Parameters:
            weather_data (dict): The weather data to save.
            city (str): The name of the city for which the weather data was fetched.
        
        Returns:
            bool: True if the data was saved successfully, False otherwise.
        """
        # Check if the weather_data is None, indicating a previous error
        if not weather_data:
            return False

        # Generate a timestamp for the weather data file
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

        # Construct the file name for the weather data, including city and timestamp
        file_name = f"weather-data/{city}-{timestamp}.json"

        try:
            # Add the timestamp to the weather data
            weather_data['timestamp'] = timestamp

            # Upload the weather data to the specified S3 bucket
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=json.dumps(weather_data),
                ContentType='application/json'
            )

            # Print a success message
            print(f"Successfully saved data for {city} to S3")
            return True
        except Exception as e:
            # Print an error message if the upload to S3 fails
            print(f"Error saving to S3: {e}")
            return False

    @staticmethod
    def main():
        """
        The main function to execute the WeatherDashboard workflow.
        Fetches weather data for a list of cities and saves it to S3.
        """
        # Create an instance of the WeatherDashboard class
        dashboard = WeatherDashboard()

        # Ensure the S3 bucket exists before attempting to save data
        dashboard.create_bucket_if_not_exists()

        # Define a list of cities to fetch weather data for
        cities = ["Nairobi", "Machakos", "Chwele"]

        # Iterate over each city in the list
        for city in cities:
            print(f"\nFetching weather for {city}...")

            # Fetch the weather data from the API
            weather_data = dashboard.fetch_weather(city)

            if weather_data:
                # Extract relevant weather details from the API response
                temp = weather_data['main']['temp']
                feels_like = weather_data['main']['feels_like']
                humidity = weather_data['main']['humidity']
                description = weather_data['weather'][0]['description']

                # Print the weather details to the console
                print(f"Temperature: {temp}°F")
                print(f"Feels like: {feels_like}°F")
                print(f"Humidity: {humidity}%")
                print(f"Conditions: {description}")

                # Save the weather data to the S3 bucket
                success = dashboard.save_to_s3(weather_data, city)

                if success:
                    print(f"Weather data for {city} saved to S3!")
            else:
                # Print an error message if fetching weather data fails
                print(f"Failed to fetch weather data for {city}")

# Ensure that the script runs only when executed directly
if __name__ == "__main__":
    WeatherDashboard.main()
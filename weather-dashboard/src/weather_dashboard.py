# Imports

import os
import json
import boto3
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv

class WeatherDashboard:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API')
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')
        self.s3_client = boto3.client('s3')
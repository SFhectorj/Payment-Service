import os
import time
import json
import datetime
import random
import string

REQUEST_DIRECTORY = "requests"
RESPONSE_DIRECTORY = "responses"
RECEIPT_DIRECTORY = "reciepts"
LOG_DIRECTORY = "logs"
LOG_FILE = os.path.join(LOG_DIRECTORY, "payment_log.txt")

# Create needed files if not present
for folder in [REQUEST_DIRECTORY, RESPONSE_DIRECTORY, RECEIPT_DIRECTORY, LOG_DIRECTORY]:
    os.makedirs(folder, exist_ok=True)

def run_service():
    '''
    Main Service Loop
    '''
    print("Payment Service is running... (press CTR;+C to stop)")
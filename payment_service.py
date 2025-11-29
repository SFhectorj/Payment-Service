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

# Create needed folders if not present
for folder in [REQUEST_DIRECTORY, RESPONSE_DIRECTORY, RECEIPT_DIRECTORY, LOG_DIRECTORY]:
    os.makedirs(folder, exist_ok=True)

def log(message: str):
    '''
    Logging Utility:
    writes transaction log entries to payment_log.txt.
    '''
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def generate_payment_id():
    '''
    Generates a unique payment identifier
    Sets prefix "pay" and adds 6 random characters
    ex. "payx3hp0z"
    '''
    character_pool = string.ascii_lowercase + string.digits
    random_characters_list = random.choices(character_pool, k=6)

    combine_parts = "".join(random_characters_list)
    add_prefix = "pay" + combine_parts
    return add_prefix

def mask_card(card_number: str):
    """
    Security Masking Feature:
    Masks all but last 4 cc numbers.
    """
    digits_to_hide = len(card_number) - 4
    # Creates a string of 12 'x'
    masking_string = "x" * digits_to_hide
    last_four_digits = card_number[-4:]

    masked_number = masking_string + last_four_digits
    return masked_number

def parse_request(path):
    '''
    Read data, one line at a time and convert to dictionary.
    '''
    data = {}
    with open(path, "r") as f:
        # Splits line into 2 parts at the first "=".
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                data[key] = value
    return data



def run_service():
    '''
    Main Service Loop
    '''
    print("Payment Service is running... (press CTRL+C to stop)")
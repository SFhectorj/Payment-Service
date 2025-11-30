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

def validate_payment(request):
    '''
    Validates card information from request.
    Goes through CARD, EXP, CVV, Amount.
    Returns error messages if an issue is found.
    '''
    if "CARD" not in request or not request["CARD"].isdigit():
        print("Invalid CARD format")
        return False
    if "EXP" not in request or "/" not in request["EXP"]:
        print("Invalid EXP format")
        return False
    # attempts to convert expiration date, returning errors if conversion fails.
    try:
        month, year = request["EXP"].split("/")
        month = int(month)
        year = int("20" + year)
        exp_date = datetime.date(year, month, 1)
        if exp_date < datetime.date.today().replace(day=1):
            print("Card Expired")
            return False
    except:
        print("Invalid EXP format")
        return False
    
    if "CVV" not in request or not request["CVV"].isdigit():
        print("Invalid CVV format")
        return False
    
    if "AMOUNT" not in request:
        print("Missing AMOUNT")
        return False
    
    # Converts amount into float
    try:
        amount_valid = float(request["AMOUNT"])
        if amount_valid <= 0:
            print("Invalid amount value")
            return False
    except:
        print("Invalid amount value")
        return False
    
    return True

def process_payment(request, response_file):
    '''
    main controller for handling payments, using validate_payment, generate_payment_id, and mask_card to approve or deny transactions.
    '''
    is_valid = validate_payment(request)
    error = None

    if not is_valid:
        with open(response_file, "w") as f:
            f.write("STATUS=DENIED\n")
            f.write(f"REASON={error}\n")
        log(f"PAYMENT DENIED: {error}")
        return
    
    # When validation is passed
    payment_id = generate_payment_id()

    with open(response_file, "w") as f:
        f.write("STATUS=APPROVED\n")
        f.write(f"PAYMENT_ID={payment_id}\n")

    # Builds dict for receipt data
    receipt_data = {
        "payment_id": payment_id,
        "amount": float(request["AMOUNT"]),
        "masked_card": mask_card(request["CARD"]),
        "timestamp":datetime.datetime.now().isoformat()
    }

    # Save Reciept
    receipt_path = os.path.join(RECEIPT_DIRECTORY, f"receipt_{payment_id}.json")
    with open(receipt_path, "w") as f:
        json.dump(receipt_data, f, indent=2)

    log(f"PAYMENT APPROVED: {payment_id}, amount={request['AMOUNT']}")

def process_reciept_request(request, response_file):
    if "Payment_ID" not in request:
        with open(response_file, "w") as f:
            f.write("STATUS=ERROR\n")
            f.write("REASON=Missing PAYMENT_ID\n")
        log("RECEIPT ERROR: Missing PAYMENT_ID")
        return

    pay_id = request["PAYMENT_ID"]
    receipt_path = os.path.join(RECEIPT_DIRECTORY, f"receipt_{pay_id}.json")

    if not os.path.exists(receipt_path):
        with open(response_file, "w") as f:
            f.write("STATUS=ERROR\n")
            f.write("REASON=Receipt not found\n")
        log(f"RECEIPT ERROR: Receipt not found for {pay_id}")
        return
    
    with open(receipt_path, "r") as f:
        receipt = json.load(f)

    with open(response_file, "w") as f:
        f.write("STATUS=FOUND\n")
        f.write(f"PAYMENT_ID={receipt['payment_id']}\n")
        f.write(f"AMOUNT={receipt['amount']}\n")
        f.write(f"CARD={receipt['masked_card']}\n")

    log(f"RECEIPT FOUND: payment_id={pay_id}")     

def run_service():
    '''
    Main Service Loop
    '''
    print("Payment Service is running... (press CTRL+C to stop)")
    log("-----Payment Service Initiated -----")

    while True:
        files = os.listdir(REQUEST_DIRECTORY)

        for filename in files:
            path = os.path.join(REQUEST_DIRECTORY, filename)

            # Safety Check: checks for file
            if not os.path.isfile(path):
                continue

            request = parse_request(path)
            unique_id = filename.split("_")[-1].replace(".txt", "")

            # Determine type of request based on file name prefix
            if filename.startswith("payment_request"):
                response_file = os.path.join(RESPONSE_DIRECTORY, f"payment_response_{unique_id}.txt")
                process_payment(request, response_file)

            elif filename.startswith("receipt_request"):
                response_file = os.path.join(RESPONSE_DIRECTORY, f"receipt_response_{unique_id}.txt")
                process_reciept_request(request, response_file)

            os.remove(path)

        time.sleep(0.5)


if __name__ == "__main__":
    run_service()

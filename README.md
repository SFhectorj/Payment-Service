# Payment-Service
The Payment Simulator Microservice talks to each other using text files in two folders:
requests/ These are the files created by external program.
responses/ These are the files the Payment Service creates.
  
Example Request/Response Call:
# Request
{
  "payment_id": "payg66nis",
  "amount": 10.0,
  "masked_card": "xxxxxxxxxxxx1111",
  "timestamp": "2025-11-29T23:22:07.522823"
}

# Response
STATUS=APPROVED
PAYMENT_ID=paylh03hs

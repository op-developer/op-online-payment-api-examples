import os
import requests
import uuid
from datetime import datetime
import json
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

# PUT YOUR API KEY HERE
API_KEY = ""

SERVER = "https://sandbox.apis.op.fi/paymentbutton"

# The SANDBOX will recognise signatures generated with the private
# key used on the HMAC instructions page
PRIVATE_KEY_FILE = "private-key.pem"
if not os.path.isfile(PRIVATE_KEY_FILE):
    print("Downloading SANDBOX private key")
    response = requests.get("https://op-developer.fi/assets/private-key.pem")
    with open(PRIVATE_KEY_FILE, "wb") as f:
        f.write(response.content)

DATE = datetime.utcnow().strftime("%a, %d %b %Y %T GMT")
print(f"Working with DATE: {DATE}")

MERCHANT_ID = "c3efaaee-a6bb-449f-9213-e45e23a462ef"
print(f"Using merchant id: {MERCHANT_ID}")

print(f"Using API key: {API_KEY}")

SESSION_ID = str(uuid.uuid4()).lower()
print(f"Using session id: {SESSION_ID}")

REQUEST_ID = str(uuid.uuid4()).lower()
print(f"Using request id: {REQUEST_ID}")

REQUEST_BODY = '{"amount":"1.00","cancel":{"url":"https://shop.example.com/cancel/path"},"reject":{"url":"https://shop.example.com/reject/path"},"return":{"url":"https://shop.example.com/return/path"},"currency":"EUR","accountId":"8a5d4aac-8f8f-47ed-ae2f-36ffeaf57c79","reference":"RF3517834735"}'
print("Using request body:")
print(REQUEST_BODY)

URL = f"{SERVER}/v1/payments"

# No trailing newline at the end of the signature base!
# Only single LF (\n) characters used as newline characters

SIGNATURE_BASE = f"""POST
application/json
{DATE}
{MERCHANT_ID}
{API_KEY}
{SESSION_ID}
{REQUEST_ID}
{URL}
{REQUEST_BODY}"""

print("\nUsing signature base:")
print(SIGNATURE_BASE)

with open(PRIVATE_KEY_FILE, "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

signature = private_key.sign(SIGNATURE_BASE.encode(), padding.PKCS1v15(), hashes.SHA256()).hex()
print(f"Signature: {signature}")

print("Launching request")
headers = {
    "Authorization": f"{MERCHANT_ID}:1:0:{signature}",
    "Date": DATE,
    "Accept": "application/json",
    "Content-Type": "application/json",
    "x-session-id": SESSION_ID,
    "x-request-id": REQUEST_ID,
    "x-api-key": API_KEY,
}
response = requests.post(URL, headers=headers, data=REQUEST_BODY)
print(f"Response: {response.status_code} {response.reason}\n{response.text}")


payment_response = response.json()
print(json.dumps(payment_response, indent=2))



URL = f"{SERVER}/v1/payments/{payment_response['paymentId']}"

# No trailing newline at the end of the signature base!
# Only single LF (\n) characters used as newline characters

SIGNATURE_BASE = f"""GET
application/json
{DATE}
{MERCHANT_ID}
{API_KEY}
{SESSION_ID}
{REQUEST_ID}
{URL}
"""

print("\nUsing signature base:")
print(SIGNATURE_BASE)

with open(PRIVATE_KEY_FILE, "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

signature = private_key.sign(SIGNATURE_BASE.encode(), padding.PKCS1v15(), hashes.SHA256()).hex()
print(f"Signature: {signature}")

print("Launching request")
headers = {
    "Authorization": f"{MERCHANT_ID}:1:0:{signature}",
    "Date": DATE,
    "Accept": "application/json",
    "Content-Type": "application/json",
    "x-session-id": SESSION_ID,
    "x-request-id": REQUEST_ID,
    "x-api-key": API_KEY,
}
response = requests.get(URL, headers=headers)
print(f"Response: {response.status_code} {response.reason}\n{response.text}")
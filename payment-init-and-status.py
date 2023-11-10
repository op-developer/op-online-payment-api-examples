import os
import requests
import uuid
from datetime import datetime
import json
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import urllib.parse

# PUT YOUR API KEY HERE
API_KEY = ""

SERVER = "https://sandbox.apis.op.fi/paymentbutton"
SERVER_FRONT = "https://api.smn-sandbox.aws.op-palvelut.fi"

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

print("Launching payment creationg request")
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


URL = f"{SERVER_FRONT}/customer/payment/startPaymentConfirmation?paymentOperationId={payment_response['paymentOperationId']}&paymentOperationValidation={urllib.parse.quote(payment_response['paymentOperationValidation'])}"

print(f"Launching payment browser flow request to {URL}")
headers = {
    "Date": DATE,
    "Accept": "application/json",
    "Content-Type": "application/json",
    "x-session-id": SESSION_ID,
    "x-request-id": REQUEST_ID,
    "x-api-key": API_KEY,
}
response = requests.get(URL, headers=headers, allow_redirects=False)
print(f"Response: {response.status_code} {response.reason}\n{response.text}")


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

print("Launching request to get payment status")
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


print("getting all multibank payments providers")

URL = f"{SERVER}/v1/payments/multibank/providers"
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

print("Launching request to get all providers for multibank payments")
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

provider_response = response.json()
print(json.dumps(provider_response, indent=2))


bankId = provider_response['providers'][0]['bankId']
URL = f"{SERVER_FRONT}/customer/payment/multibank/direct/{bankId}/startPaymentConfirmation?paymentOperationId={payment_response['paymentOperationId']}&paymentOperationValidation={urllib.parse.quote(payment_response['paymentOperationValidation'])}"

print(f"Launching request to multibank payment browser flow {URL}")
headers = {
    #"Authorization": f"{MERCHANT_ID}:1:0:{signature}",
    "Date": DATE,
    "Accept": "application/json",
    "Content-Type": "application/json",
    "x-session-id": SESSION_ID,
    "x-request-id": REQUEST_ID,
    "x-api-key": API_KEY,
}
response = requests.get(URL, headers=headers, allow_redirects=False)
print(f"Response: {response.status_code} {response.reason}\n{response.text}")
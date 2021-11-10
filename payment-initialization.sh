#!/bin/bash
set -e

# To run this script you need wget, curl, openssl and uuidgen installed.

# Common pitfalls when generating the Authorization header value:
# - Newline characters other than LF (\n) in the signature base
# - Trailing newline character in the signature base
# - Different values used in the signature base than the ones sent in the request

# PUT YOUR API KEY HERE
API_KEY="YOUR_API_KEY_GOES_HERE"

SERVER="https://sandbox.apis.op.fi/paymentbutton"

# The SANDBOX will recognise signatures generated with the private
# key used on the HMAC instructions page
PRIVATE_KEY="payment-button.private"
if [ ! -f $PRIVATE_KEY ]; then
  echo "Downloading SANDBOX private key"
  wget -O $PRIVATE_KEY https://op-developer.fi/assets/private-key.pem
fi

#DATE=$(date -u +"%a, %d %m %Y %T GMT")
DATE=$(date --universal +"%a, %d %b %Y %T GMT")
echo "Working with DATE: $DATE"

MERCHANT_ID="c3efaaee-a6bb-449f-9213-e45e23a462ef"
echo "Using merchant id: $MERCHANT_ID"

echo "Using API key: $API_KEY"

SESSION_ID=$(uuidgen)
echo "Using session id: $SESSION_ID"

REQUEST_ID=$(uuidgen)
echo "Using request id: $REQUEST_ID"

REQUEST_BODY="{\"amount\":\"1.00\",\"cancel\":{\"url\":\"https://shop.example.com/cancel/path\"},\"reject\":{\"url\":\"https://shop.example.com/reject/path\"},\"return\":{\"url\":\"https://shop.example.com/return/path\"},\"currency\":\"EUR\",\"accountId\":\"8a5d4aac-8f8f-47ed-ae2f-36ffeaf57c79\",\"reference\":\"RF3517834735\"}"
echo "Using request body:"
echo $REQUEST_BODY

URL="$SERVER/v1/payments"

# No trailing newline at the end of the signature base!
# Only single LF (\n) characters used as newline characters

SIGNATURE_BASE="POST
application/json
$DATE
$MERCHANT_ID
$API_KEY
$SESSION_ID
$REQUEST_ID
$URL
$REQUEST_BODY"

printf "\nUsing signature base:\n"
echo "$SIGNATURE_BASE"
echo -n "$SIGNATURE_BASE" > signature-base.txt  # avoid a trailing \n character to the end of the file

printf "\nCalculating signature\n"
DIGEST=$(openssl dgst -sha256 -sign $PRIVATE_KEY -hex signature-base.txt | cut -d' ' -f2)
echo "Signature base's message digest: $DIGEST"

echo 'Signature=$MERCHANT_ID:1:0:$DIGEST'
SIGNATURE="$MERCHANT_ID:1:0:$DIGEST"
echo "Signature: $SIGNATURE"

echo Launching request
echo "curl -v -XPOST $URL \\
  -H \"Authorization: $SIGNATURE\" \\
  -H \"Date: $DATE\" \\
  -H 'Accept: application/json' \\
  -H 'Content-Type: application/json' \\
  -H \"x-session-id: $SESSION_ID\" \\
  -H \"x-request-id: $REQUEST_ID\" \\
  -H \"x-api-key: $API_KEY\" \\
  -d '$REQUEST_BODY'"

curl -v -XPOST $URL \
  -H "Authorization: $SIGNATURE" \
  -H "Date: $DATE" \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H "x-session-id: $SESSION_ID" \
  -H "x-request-id: $REQUEST_ID" \
  -H "x-api-key: $API_KEY" \
  -d "$REQUEST_BODY"

# op-online-payment-api-examples

A code sample repository for OP Online Payment API. The complete API documentation can be found on
the [OP Developer portal](https://op-developer.fi/docs/api/2b9CTBdcbizgOu55Ldoe3U/REST%20API).

## Contents

The repository contains the following samples:

### payment-initialization.sh

A Bash script demonstrating how to initiate a payment with API in the SANDBOX environment.
The script needs `wget`, `curl`, `openssl`, and `uuidgen` installed in order to run.

The script prints intermediate steps and their results while calculating the Authorization header value.
The API call is done via curl, and the command itself is printed before executing.

This reference script can be useful in identifying problems in generating the Authorization header value,
and constructing the set of headers for the request.

### payment-init-and-status.python

A python script demonstrating how to initiate a payment with API in the SANDBOX environment and getting
the status of the same payment

The script prints intermediate steps and their results while calculating the Authorization header value.

This reference script can be useful in identifying problems in generating the Authorization header value,
and constructing the set of headers for the request.
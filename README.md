# Microservice for BTC transaction creation
This repository was only used for learning purposes.
Tech Stack:
* Python 3.8
* bitcoinutils
* Flask
* py.test
* Docker

## Overview

This endpoint will be used to create a raw transaction that spends from a P2PKH address and that supports paying to mulitple addresses (either P2PKH or P2SH). The endpoint should return a transaction that spends from the source address and that pays to the output addresses.

URL: /payment_transactions Method: POST
  Request body (dictionary):
  source_address (string): The address to spend from
  outputs (dictionary): A dictionary that maps addresses to amounts (in SAT) fee_kb (int): The fee per kb in SAT
Response body (dictionary):
  raw (string): The unsigned raw transaction inputs (array of dicts): The inputs used
  txid (string): The transaction id
  vout (int): The output number
  script_pub_key (string): The script pub key amount (int): The amount in SAT

## How to run and test it?
In the main directory we use `docker-compose up` and it will spin up our microservice.

Sample cURL command:
```
curl http://localhost:5000/payment_transaction -X POST -i -H 'Content-Type: application/json' -d '{"source_address": "1Dorian4RoXcnBv9hnQ4Y2C1an6NJ4UrjX", "outputs":{"3KAQHLWZ9EX2Tuyda7V5mKCbtzHfe2oGHv": 10, "185pq5iKEXbLA1b7k9MCCfHKkzdTjFwbNz": 101000}, "fee_kb": 19000}'
```
Data for that command were taken from "Masterin Bitcoin" book.

To run tests use `py.test` in the main directory

You can decode raw transaction here: https://live.blockcypher.com/btc/decodetx/

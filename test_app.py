import pytest

from app import app
from flask import json


def test_payment_transaction():
    app.testing = True
    with app.app.test_client() as client:
        response = client.post(
            '/payment_transaction',
            data=json.dumps({'source_address': '1Dorian4RoXcnBv9hnQ4Y2C1an6NJ4UrjX', 'outputs': {
                            '3KAQHLWZ9EX2Tuyda7V5mKCbtzHfe2oGHv': 10, '185pq5iKEXbLA1b7k9MCCfHKkzdTjFwbNz': 101000}, 'fee_kb': 19000}),
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))
        assert response.status_code == 201


def test_payment_transaction_with_wrong_source_address():
    app.testing = True
    with app.app.test_client() as client:
        response = client.post(
            '/payment_transaction',
            data=json.dumps({'source_address': '2Dorian4RoXcnBv9hnQ4Y2C1an6NJ4UrjX', 'outputs': {
                            '3KAQHLWZ9EX2Tuyda7V5mKCbtzHfe2oGHv': 10, '185pq5iKEXbLA1b7k9MCCfHKkzdTjFwbNz': 101000}, 'fee_kb': 19000}),
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))
        assert response.status_code == 400


def test_payment_transaction_with_invalid_data():
    app.testing = True
    with app.app.test_client() as client:
        response = client.post(
            '/payment_transaction',
            data=json.dumps({'outputs': {
                            '3KAQHLWZ9EX2Tuyda7V5mKCbtzHfe2oGHv': 10, '185pq5iKEXbLA1b7k9MCCfHKkzdTjFwbNz': 101000}, 'fee_kb': 19000}),
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))
        assert response.status_code == 400

from flask import Flask, Blueprint, request, jsonify
from .btc_payment import btc_payment
from .errors import *

btc = Blueprint('btc_bp', __name__)


@btc.route('/payment_transaction', methods=['POST'])
def payment_transaction():
    tx_data = request.get_json()
    required_fields = ['source_address', 'outputs', 'fee_kb']

    for field in required_fields:
        if not tx_data.get(field):
            return jsonify(message='Invalid transaction data'), 400

    try:
        rawtx, inputs = btc_payment(tx_data['source_address'],
                                    tx_data['outputs'], tx_data['fee_kb'])
    except UnspentTransactionsError:
        return jsonify(message='Internal error with unspent transactions processing'), 400
    except BtcPaymentError:
        return jsonify(message='Internal error with raw transaction creation'), 500

    return jsonify(raw=rawtx, inputs=inputs), 201

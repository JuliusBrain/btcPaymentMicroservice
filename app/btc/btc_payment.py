import json
import requests
import sys

from .errors import *
from decimal import Decimal
from bitcoinutils.setup import setup
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.keys import P2pkhAddress, P2shAddress
from bitcoinutils.script import Script
from bitcoinutils.constants import P2PKH_ADDRESS, P2SH_ADDRESS, SATOSHIS_PER_BITCOIN


def btc_payment(source_address, outputs, fee_satoshi_kb, network='mainnet'):
    try:
        setup(network)
        outputs_list = []
        p2sh_num = 0
        p2pkh_num = 0
        total_amount_to_spend = _calculate_total_amount(outputs)
        print(total_amount_to_spend)
        txin = []
        utxo_amount = 0

        for address, value in outputs.items():
            addr_type = _check_address_type(address)
            addr = ''
            if addr_type is P2PKH_ADDRESS:
                addr = P2pkhAddress(address)
                txout = TxOutput(Decimal(value) / Decimal(SATOSHIS_PER_BITCOIN), Script(['OP_DUP', 'OP_HASH160', addr.to_hash160(),
                                                                                         'OP_EQUALVERIFY', 'OP_CHECKSIG']))
                outputs_list.append(txout)
                p2pkh_num += 1
            elif addr_type is P2SH_ADDRESS:
                addr = P2shAddress(address)
                txout = TxOutput(Decimal(value) / Decimal(SATOSHIS_PER_BITCOIN), Script(['OP_HASH160', addr.to_hash160(),
                                                                                         'OP_EQUAL']))
                outputs_list.append(txout)
                p2sh_num += 1

        utxo_set, fee = _get_unspent_transactions(
            source_address, total_amount_to_spend, p2pkh_num,
            p2sh_num, fee_satoshi_kb)

        for utxo in utxo_set:
            txin.append(TxInput(utxo['txid'], utxo['vout']))
            utxo_amount += utxo['amount']

        change = utxo_amount - fee - total_amount_to_spend
        change_addr = P2pkhAddress(source_address)
        change_txout = TxOutput(Decimal(change) / Decimal(SATOSHIS_PER_BITCOIN), Script(['OP_DUP', 'OP_HASH160',
                                                                                         change_addr.to_hash160(),
                                                                                         'OP_EQUALVERIFY', 'OP_CHECKSIG']))
        outputs_list.append(change_txout)
        tx = Transaction(txin, outputs_list)

        return tx.serialize(), utxo_set
    except UnspentTransactionsError:
        raise UnspentTransactionsError
    except:
        raise BtcPaymentError("Problem during creation of raw transaction")


def _get_unspent_transactions(address, amount_to_send, p2pkh_num, p2sh_num, fee_satoshi_kb):
    try:
        resp = requests.get(
            'https://blockchain.info/unspent?active={0}'.format(address))
        utxo_set = json.loads(resp.text)["unspent_outputs"]
        utxos = []
        # Fee calculated for at least 1 input and additional output transaction (change)
        fee = _calculate_fee(
            1, p2pkh_num + 1, p2sh_num, fee_satoshi_kb)
        lessers = [utxo for utxo in utxo_set if utxo['value']
                   < amount_to_send + fee]
        greaters = [utxo for utxo in utxo_set if utxo['value']
                    >= amount_to_send + fee]

        if greaters:
            utxos.append({'txid': greaters[0]['tx_hash_big_endian'],
                          'vout': greaters[0]['tx_output_n'],
                          'script_pub_key': greaters[0]['script'],
                          'amount': greaters[0]['value']
                          })
            return utxos, fee

        sum = 0
        for i, utxo in enumarate(lessers):
            utxos.append({'txid': utxo['tx_hash_big_endian'],
                          'vout': utxo['tx_output_n'],
                          'script_pub_key': utxo['script'],
                          'amount': utxo['value']
                          })
            sum += utxo['value']
            tmp_fee = _calculate_fee(
                i, p2pkh_num + 1, p2sh_num, fee_satoshi_kb)
            if sum >= amount_to_send + tmp_fee:
                return utxos, tmp_fee

        return None
    except requests.exceptions.RequestException as e:
        raise UnspentTransactionsError(
            "Problem during blockchain info request processing: {0}".format(e))
    except ValueError as e:
        raise UnspentTransactionsError(
            "Problem during json load: {0}".format(e))
    except:
        raise UnspentTransactionsError(
            "Error during choosing unspent transactions")


def _calculate_fee(input_len, p2pkh_num, p2sh_num, satoshi_per_kb):
    try:
        tx_size = input_len * 148 + p2pkh_num * 34 + p2sh_num * 32 + 10
        return tx_size * (satoshi_per_kb/1000)
    except ValueError as e:
        print(e)


def _calculate_total_amount(outputs):
    try:
        sum = 0
        for v in outputs.values():
            sum += v
        return sum
    except:
        raise Exception("Error {0} during calculating total amount".format(
            sys.exc_info()[0]))


def _check_address_type(address):
    try:
        if address[0] == '1':
            return P2PKH_ADDRESS
        elif address[0] == '3':
            return P2SH_ADDRESS
        else:
            return None
    except IndexError:
        raise AddressTypeError

from flask import Flask, request, jsonify
from .btc.btc_bp import btc

app = Flask(__name__)
app.register_blueprint(btc, url_prefix='')


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS
import _locale
from create_lines import create_lines
from update_lines import update_lines

_locale._getdefaultlocale = (lambda *args: ['en_US', 'UTF-8'])

app = Flask(__name__)
CORS(app, supports_credentials=True)


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    print('Received Data:', data)
    try:
        resultado = create_lines(data)
        return jsonify({'resultado': resultado})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    print('Received Data:', data)
    try:
        resultado = update_lines(data)
        return jsonify({'resultado': resultado})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

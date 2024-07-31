from flask import Flask, request, jsonify
from flask_cors import CORS
import _locale
import create_lines

_locale._getdefaultlocale = (lambda *args: ['en_US', 'UTF-8'])

app = Flask(__name__)
CORS(app, supports_credentials=True)


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    print('Received Data:', data)

    result = create_lines.create_lines(data)
    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

storage = {}
send_to_tb_data = {}

@app.route('/data', methods=['POST'])
def receive_data():
    global storage
    data = request.get_json()
    storage = data
    print("Data diterima:", data)
    return "Data diterima", 200

@app.route('/sendToTB', methods=['POST'])
def receive_send_to_tb():
    global send_to_tb_data
    data = request.get_json()
    send_to_tb_data = data
    print("Data sendToTB diterima:", data)
    return "Data sendToTB diterima", 200

@app.route('/data', methods=['GET'])
def send_data():
    if storage:
        return jsonify(storage)
    return jsonify({"message": "Belum ada data"}), 404

@app.route('/sendToTB', methods=['GET'])
def send_send_to_tb():
    if send_to_tb_data:
        return jsonify(send_to_tb_data)
    return jsonify({"message": "Belum ada data sendToTB"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)

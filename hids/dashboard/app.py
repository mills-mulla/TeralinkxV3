from flask import Flask, render_template, jsonify
import psycopg2
import os

app = Flask(__name__)

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'hids_db')

@app.route('/')
def index():
    return jsonify({'message': 'HIDS Dashboard', 'status': 'running'}), 200

@app.route('/alerts')
def alerts():
    # Fetch alerts from PostgreSQL
    return jsonify({'alerts': []}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)

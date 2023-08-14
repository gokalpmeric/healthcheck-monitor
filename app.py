from flask import Flask, jsonify, request, render_template
import requests
from threading import Thread
from time import sleep
import os
import json

app = Flask(__name__)

# List to hold monitors
monitors = []

# File path for storing URLs
DATA_DIR = './data'  # Change this path as needed
DATA_FILE = os.path.join(DATA_DIR, 'monitors.json')

# Ensure the directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Function to perform health checks
def check_health():
    while True:
        for monitor in monitors:
            try:
                response = requests.get(monitor['url'], timeout=5)
                monitor['status'] = 'up' if response.status_code == 200 else 'down'
            except Exception as e:
                monitor['status'] = 'down'
        save_monitors(monitors)
        sleep(60)

def load_monitors():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            pass
    return []

def save_monitors(monitors):
    with open(DATA_FILE, 'w') as file:
        json.dump(monitors, file)

# Starting the background thread
monitors = load_monitors()
health_check_thread = Thread(target=check_health)
health_check_thread.start()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/monitors', methods=['GET'])
def get_monitors():
    return jsonify(monitors)

@app.route('/monitors', methods=['POST'])
def add_monitor():
    monitor = request.json
    url = monitor['url']
    try:
        response = requests.get(url, timeout=5)
        monitor['status'] = 'up' if response.status_code == 200 else 'down'
    except Exception as e:
        monitor['status'] = 'down'
    monitors.append(monitor)
    save_monitors(monitors)
    return jsonify(monitor), 201

@app.route('/monitors/<int:monitor_id>', methods=['DELETE'])
def delete_monitor(monitor_id):
    monitor = monitors[monitor_id]
    monitors.pop(monitor_id)
    save_monitors(monitors)
    return jsonify(monitor), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
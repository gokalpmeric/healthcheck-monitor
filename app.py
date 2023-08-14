from flask import Flask, jsonify, request, render_template
import requests
from threading import Thread
from time import sleep
from collections import defaultdict
from datetime import datetime
import json
import os

DATA_FILE = '/data/monitors.json'

app = Flask(__name__)

def save_monitors(monitors):
    with open(DATA_FILE, 'w') as file:
        json.dump(monitors, file)

def load_monitors():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return []

monitors = load_monitors()

def check_health():
    while True:
        for monitor in monitors:
            previous_status = monitor.get('status', 'unknown')
            try:
                response = requests.get(monitor['url'], timeout=5)
                monitor['status'] = 'up' if response.status_code == 200 else 'down'
            except Exception as e:
                monitor['status'] = 'down'
            
            current_date = datetime.now().date().isoformat()
            if 'daily_data' not in monitor:
                monitor['daily_data'] = defaultdict(lambda: {'uptime': 0, 'downtime': 0})
            
            if monitor['status'] == 'up':
                monitor['daily_data'][current_date]['uptime'] += 60  # 60 seconds as we sleep for 60 seconds
            else:
                monitor['daily_data'][current_date]['downtime'] += 60
        
        save_monitors(monitors)
        sleep(60)

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

@app.route('/monitors/<url>/daily_data', methods=['GET'])
def get_daily_data(url):
    for monitor in monitors:
        if monitor['url'] == url:
            return jsonify(monitor.get('daily_data', {}))
    return jsonify({'error': 'URL not found'}), 404

@app.route('/details')
def details():
    url = request.args.get('url')
    daily_data = {}
    print("Monitors:", monitors)
    for monitor in monitors:
        if monitor['url'] == url:
            daily_data = monitor.get('daily_data', {})
            break
    print("Daily data:", daily_data)
    return render_template('details.html', url=url, daily_data=daily_data)


@app.route('/monitors/<int:monitor_id>', methods=['DELETE'])
def delete_monitor(monitor_id):
    monitor = monitors[monitor_id]
    monitors.pop(monitor_id)
    save_monitors(monitors)
    return jsonify(monitor), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
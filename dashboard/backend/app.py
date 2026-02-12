from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import json
from datetime import datetime


app = Flask(__name__)
CORS(app)  # Enable frontend access

# Load data
brent_data = pd.read_csv('data/BrentOilPrices.csv')
events_data = pd.read_csv('data/events.csv', parse_dates=['date'])

# Load Task 2 results (if available)
try:
    with open('data/change_point_results.json', 'r') as f:
        change_points = json.load(f)
except:
    change_points = []

@app.route('/api/prices', methods=['GET'])
def get_prices():
    """Endpoint: Historical prices with optional date filtering"""
    start_date = request.args.get('start', '1987-01-01')
    end_date = request.args.get('end', '2023-12-31')
    
    filtered = brent_data[
        (brent_data['Date'] >= start_date) & 
        (brent_data['Date'] <= end_date)
    ]
    
    return jsonify({
        'dates': filtered['Date'].tolist(),
        'prices': filtered['Price'].round(2).tolist()
    })

@app.route('/api/events', methods=['GET'])
def get_events():
    """Endpoint: All geopolitical events"""
    event_type = request.args.get('type')
    
    filtered = events_data
    if event_type:
        filtered = filtered[filtered['event_type'] == event_type]
    
    return jsonify(filtered.to_dict('records'))

@app.route('/api/change-points', methods=['GET'])
def get_change_points():
    """Endpoint: Task 2 Bayesian change point results"""
    return jsonify(change_points)

@app.route('/api/event-impact/<event_date>', methods=['GET'])
def get_event_impact(event_date):
    """Endpoint: Price impact around specific event (±7 days)"""
    try:
        event_dt = pd.to_datetime(event_date)
        window_days = 7
        
        # Get prices around event
        start = event_dt - pd.Timedelta(days=window_days)
        end = event_dt + pd.Timedelta(days=window_days)
        
        window_data = brent_data[
            (pd.to_datetime(brent_data['Date']) >= start) &
            (pd.to_datetime(brent_data['Date']) <= end)
        ]
        
        if len(window_data) == 0:
            return jsonify({'error': 'No data found for this event'})
        
        # Calculate impact
        before_avg = window_data[window_data['Date'] < event_date]['Price'].mean()
        after_avg = window_data[window_data['Date'] >= event_date]['Price'].mean()
        
        return jsonify({
            'dates': window_data['Date'].tolist(),
            'prices': window_data['Price'].round(2).tolist(),
            'before_avg': round(before_avg, 2),
            'after_avg': round(after_avg, 2),
            'change_pct': round(((after_avg - before_avg) / before_avg) * 100, 2),
            'event_date': event_date
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print("🚀 Dashboard API running on http://localhost:5000")
    print("   Endpoints:")
    print("   - GET /api/prices?start=YYYY-MM-DD&end=YYYY-MM-DD")
    print("   - GET /api/events?type=sanctions")
    print("   - GET /api/change-points")
    print("   - GET /api/event-impact/YYYY-MM-DD")
    app.run(debug=True, port=5000)
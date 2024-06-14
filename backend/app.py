from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os
import logging
from logging.handlers import RotatingFileHandler
from geopy.distance import geodesic

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config.Config')
CORS(app)

USC_COORDINATES = (34.0224, -118.2851)

def is_within_radius(point, center, radius):
    distance = geodesic(point, center).miles
    return distance <= radius

def get_coordinates(address):
    return USC_COORDINATES

# Connect to PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(app.config['SQLALCHEMY_DATABASE_URI'])
    return conn

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/')
def landing_page():
    return "Hello World"

@app.route('/api/route', methods=['POST'])
def create_route():
    data = request.get_json()
    start_coords = data['start']
    end_coords = data['end']

    if not is_within_radius((start_coords['lat'], start_coords['lng']), USC_COORDINATES, 2):
        return jsonify({"error": "Start point is not within a 2-mile radius of USC"}), 400

    if not is_within_radius((end_coords['lat'], end_coords['lng']), USC_COORDINATES, 2):
        return jsonify({"error": "End point is not within a 2-mile radius of USC"}), 400

    # If both points are valid
    return jsonify({"message": "Route is within the 2-mile radius of USC"}), 200

# @app.route('/api/route', methods=['POST'])
# def create_route():
#     data = request.get_json()
#     start = data['start']
#     end = data['end']
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute('INSERT INTO routes (start, "end") VALUES (%s, %s) RETURNING id', (start, end))
#     route_id = cur.fetchone()[0]
#     conn.commit()
#     cur.close()
#     conn.close()
#     return jsonify({"start": start, "end": end, "route_id": route_id})

@app.route('/api/routes', methods=['GET'])
def get_routes():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, start, "end", safety_rating FROM routes')
    routes = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"route_id": route[0], "start": route[1], "end": route[2], "safety_rating": route[3]} for route in routes])

@app.route('/api/route/<int:route_id>', methods=['GET'])
def get_route_details(route_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT start, "end", safety_rating FROM routes WHERE id = %s', (route_id,))
    route = cur.fetchone()
    cur.execute('SELECT id, start, "end", safety_rating FROM routes WHERE id != %s AND start = %s AND "end" = %s', (route_id, route[0], route[1]))
    alternative_routes = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({
        "route_id": route_id,
        "start": route[0],
        "end": route[1],
        "safety_rating": route[2],
        "alternative_routes": [{"route_id": alt_route[0], "start": alt_route[1], "end": alt_route[2], "safety_rating": alt_route[3]} for alt_route in alternative_routes]
    })

# @app.route('/api/crime_data', methods=['GET'])
# def get_crime_data():
#     latitude = request.args.get('latitude')
#     longitude = request.args.get('longitude')
#     radius = request.args.get('radius')
#     # Example: Call to an external crime data API
#     # crime_data = fetch_crime_data(latitude, longitude, radius)
#     # For now, return dummy data
#     crime_data = [
#         {"type": "Robbery", "location": {"latitude": 34.0224, "longitude": -118.2851}, "timestamp": "2024-06-13T12:34:56Z"}
#     ]
#     return jsonify(crime_data)

# @app.route('/api/calculate_safety', methods=['POST'])
# def calculate_safety():
#     data = request.get_json()
#     start = data['start']
#     end = data['end']
#     # Example: Safety rating calculation based on crime data
#     safety_rating = 4.5
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute('INSERT INTO routes (start, "end", safety_rating) VALUES (%s, %s, %s) RETURNING id', (start, end, safety_rating))
#     route_id = cur.fetchone()[0]
#     conn.commit()
#     cur.close()
#     conn.close()
#     return jsonify({"route_id": route_id, "start": start, "end": end, "safety_rating": safety_rating})

# @app.route('/api/suggest_routes', methods=['POST'])
# def suggest_routes():
#     data = request.get_json()
#     start = data['start']
#     end = data['end']
#     # Example: Algorithm to suggest alternative routes
#     alternative_routes = [
#         {"route_id": 2, "start": start, "end": end, "safety_rating": 3.8}
#     ]
#     return jsonify({"start": start, "end": end, "alternative_routes": alternative_routes})

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/safety_map.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Safety Map startup')

def main():
    app.run()

main()
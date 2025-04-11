from flask import Flask, request, jsonify
import database
import phone_utils
import gps_utils
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/customers', methods=['POST'])
def create_customer():
    data = request.get_json()

    if not all(key in data for key in ('name', 'email', 'mobile', 'address')):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        is_valid, phone_message = phone_utils.validate_mobile_number(data['mobile'])
        if not is_valid:
            return jsonify({'error': f'Invalid phone number: {phone_message}'}), 400

        lat, lon, gps_message = gps_utils.get_coordinates(data['address'])
        if not lat:
            return jsonify({'error': f'Invalid address: {gps_message}'}), 400

        database.insert_customer(data['name'], data['email'], data['mobile'], lat, lon, data.get('application_usage'))

        logging.info(f"Customer created: {data['name']}, {data['email']}")
        return jsonify({'message': 'Customer created successfully'}), 201

    except ValueError as e:
        logging.error(f"Error creating customer: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.exception("An unexpected error occurred")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = database.retrieve_customer(customer_id)
    if customer:
        return jsonify(dict(customer)), 200
    else:
        return jsonify({'message': 'Customer not found'}), 404

if __name__ == '__main__':
    database.create_database()
    app.run(debug=True)

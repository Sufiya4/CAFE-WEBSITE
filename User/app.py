from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from pymongo import MongoClient
import os
from datetime import datetime, timedelta
import re
from calculate import get_consecutive_dates

app = Flask(__name__, static_folder='static',template_folder='templates')
app.secret_key = os.urandom(24)

client = MongoClient('mongodb+srv://GroupOfFour:webtect_lab@cluster0.jhpakil.mongodb.net/?retryWrites=true&w=majority', ssl=True)
db = client.get_database('WebTech')
bookings_collection = db['bookings']
availability_collection = db['avialability']


def populate_availability():
    try:
        availability_collection.delete_many({})

        # Populate availability data
        availability_data = [
            {
                'date': date,
                'morning': 10,
                'brunch': 10,
                'lunch': 10,
                'evening': 10,
                'night': 10
            } for date in get_consecutive_dates()
        ]

        # Insert data into the availability collection
        availability_collection.insert_many(availability_data)

        print('Availability collection populated successfully.')
    except Exception as e:
        print(f"Error populating availability collection: {e}")

# Run the function to populate availability
# populate_availability

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/book')
def book():
    return render_template('book.html')

@app.route('/aboutus2')
def aboutus2():
    return render_template('aboutus2.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/available_tables', methods=['POST'])
def available_tables():
    try:
        # Assume the user has submitted a form with date and time_slot data
        data = request.get_json()  # Use get_json to parse JSON data
        user_selected_date = data.get('date')
        user_selected_time_slot = data.get('time_slot')

        # Fetch availability data for the selected date from MongoDB
        availability_data = availability_collection.find_one({'date': user_selected_date})

        if availability_data and user_selected_time_slot in availability_data:
            # Send available tables count for the selected time slot to the frontend
            return jsonify({'available_tables': availability_data[user_selected_time_slot]})
        else:
            return jsonify({'error': f'Availability data not found for the selected date or time slot: {user_selected_time_slot}'})

    except Exception as e:
        return jsonify({'error': f'Error fetching availability data: {str(e)}'})


def adjust_tables(booking_id, requested_tables):
    try:
        # Update booking with the new table count
        bookings_collection.update_one({'_id': booking_id}, {'$set': {'tables': requested_tables}})

        # Decrement availability based on the number of tables booked
        booking = bookings_collection.find_one({'_id': booking_id})
        if booking:
            booking_date = booking['date']
            booking_time_slot = booking['time_slot'].lower()  # Convert to lowercase
            availability_collection.update_one(
                {'date': booking_date},
                {'$inc': {booking_time_slot: -requested_tables}}
            )

            return {'success': 'Tables updated successfully'}
        else:
            return {'error': 'Booking not found'}

    except Exception as e:
        return {'error': f'Error adjusting tables: {str(e)}'}

@app.route('/available_dates', methods = ['GET', 'POST'])
def get_dates():
    available_dates = get_consecutive_dates()  # Use the same function as in populate_plots
    return jsonify({'available_dates': available_dates})

@app.route('/store_bookings', methods=['POST'])
def store_bookings():
    try:
        # Get booking details from the request
        booking_details = request.get_json()
        print(booking_details)

        # Increment reservation number
        last_reservation = bookings_collection.find_one(sort=[("reservation_number", -1)])
        if last_reservation:
            reservation_number = last_reservation["reservation_number"] + 1
        else:
            reservation_number = 1

        # Store booking details in the MongoDB collection
        booking_details["reservation_number"] = reservation_number
        booking_id = bookings_collection.insert_one(booking_details).inserted_id

        # Reduce availability based on the number of tables booked
        booking_date = booking_details["date"]
        booking_time_slot = booking_details["time_slot"].lower()
        requested_tables = booking_details["tables"]

        result = adjust_tables(booking_id, requested_tables)

        if 'error' in result:
            # Log the error and return an error response
            print(f'Error adjusting tables: {result["error"]}')
            return jsonify({'error': f'Error adjusting tables: {result["error"]}'})
        else:
            return jsonify({'success': 'Booking details stored successfully', 'booking_id': str(booking_id),'reservation_number': reservation_number})

    except Exception as e:
        # Log the exception and return an error response
        print(f'Error storing booking details: {str(e)}')
        return jsonify({'error': f'Error storing booking details: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
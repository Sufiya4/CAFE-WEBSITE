from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from calculate import get_consecutive_dates

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB connection
client = MongoClient('mongodb+srv://GroupOfFour:webtect_lab@cluster0.jhpakil.mongodb.net/?retryWrites=true&w=majority', ssl=True)
db = client.get_database('WebTech')
admin_collection = db['admins']
bookings_collection = db['bookings']

# Insert a default admin record if not exists
default_admin = {
    'username': 'admin',
    'password': 'admin123',
}

existing_admin = admin_collection.find_one({'username': 'admin'})

if not existing_admin:
    admin_collection.insert_one(default_admin)

@app.route('/')
def home():
    return render_template('admin_login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Check admin credentials in MongoDB
    admin = admin_collection.find_one({'username': username, 'password': password})

    if admin:
        # Successful login
        flash('Login successful', 'success')
        return redirect(url_for('admin_dashboard'))
    else:
        # Failed login
        flash('Invalid credentials. Please try again.', 'error')
        return redirect(url_for('home'))

@app.route('/get_available_dates', methods=['GET'])
def get_available_dates():
    available_dates = get_consecutive_dates()

    return jsonify({'available_dates': available_dates})

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    # Fetch bookings and available dates from your database or provide dummy data
    bookings = []  # Replace with actual data
    available_dates = []  # Replace with actual data

    return render_template('admin_dashboard.html', bookings=bookings, available_dates=available_dates)

@app.route('/admin_bookings', methods=['GET'])
def admin_bookings():
    search_date = request.args.get('date')

    try:
        search_datetime = datetime.strptime(search_date, '%Y-%m-%d')
    except ValueError:
        return jsonify([])

    # Fetch booking history data based on the selected date
    booking_history = list(bookings_collection.find({'bookingDate': search_datetime}))

    return jsonify(booking_history)

if __name__ == "__main__":
    app.run(debug=True)
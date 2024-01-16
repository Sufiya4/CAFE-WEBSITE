from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from pymongo import MongoClient
from flask_mail import Mail, Message
import os
from app import generate_validation_code, get_consecutive_dates
from datetime import datetime, timedelta
import re
from flask import Flask, redirect, request

app = Flask(__name__, static_folder='static')
app.secret_key = os.urandom(24)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'supriyar334@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'supriyar334@123'  # Replace with your email password

mail = Mail(app)

# Replace 'YOUR_CONNECTION_STRING' with your actual MongoDB Atlas connection string
client = MongoClient('mongodb+srv://supriyar334:Supriyar334123@cluster0.emggwsx.mongodb.net/?retryWrites=true&w=majority')
db = client.get_database('online_parking')
users_collection = db['users']
plots_collection = db['plots']
bookings_collection = db['bookings']
parking_availability = db['parking_availability']
admin_collection = db['admin_data']
price_collection = db['prices']

def populate_plots():
    plots_collection.delete_many({})
    plot_data = [
        {'plot_id': 'A1', 'name': 'A1', 'occupied_slots': {date: {f"{minute:}-{minute+30}": True for minute in range(0, 1410, 30)} for date in get_consecutive_dates()}},
        {'plot_id': 'A2', 'name': 'A2', 'occupied_slots': {date: {f"{minute}-{minute+30}": True for minute in range(0, 1410, 30)} for date in get_consecutive_dates()}},
        {'plot_id': 'A3', 'name': 'A3', 'occupied_slots': {date: {f"{minute}-{minute+30}": True for minute in range(0, 1410, 30)} for date in get_consecutive_dates()}},
        {'plot_id': 'A4', 'name': 'A4', 'occupied_slots': {date: {f"{minute}-{minute+30}": True for minute in range(0, 1410, 30)} for date in get_consecutive_dates()}},
        {'plot_id': 'B1', 'name': 'B1', 'occupied_slots': {date: {f"{minute}-{minute+30}": True for minute in range(0, 1410, 30)} for date in get_consecutive_dates()}},
        {'plot_id': 'B2', 'name': 'B2', 'occupied_slots': {date: {f"{minute}-{minute+30}": True for minute in range(0, 1410, 30)} for date in get_consecutive_dates()}},
        {'plot_id': 'B3', 'name': 'B3', 'occupied_slots': {date: {f"{minute}-{minute+30}": True for minute in range(0, 1410, 30)} for date in get_consecutive_dates()}},
        {'plot_id': 'B4', 'name': 'B4', 'occupied_slots': {date: {f"{minute}-{minute+30}": True for minute in range(0, 1410, 30)} for date in get_consecutive_dates()}},
        {'plot_id': 'C1', 'name': 'C1', 'occupied_slots': {date: {f"{minute}-{minute+30}": True for minute in range(0, 1410, 30)} for date in get_consecutive_dates()}},
        {'plot_id': 'C2', 'name': 'C2', 'occupied_slots': {date: {f"{minute}-{minute+30}": True for minute in range(0, 1410, 30)} for date in get_consecutive_dates()}},
        {'plot_id': 'C3', 'name': 'C3', 'occupied_slots': {date: {f"{minute}-{minute+30}": True for minute in range(0, 1410, 30)} for date in get_consecutive_dates()}},
        {'plot_id': 'C4', 'name': 'C4', 'occupied_slots': {date: {f"{minute}-{minute+30}": True for minute in range(0, 1410, 30)} for date in get_consecutive_dates()}},
    ]
    plots_collection.insert_many(plot_data)


#Uncomment the following line and run the app once to populate plots
#populate_plots()

plots = [{'plot_id': 'A1', 'name': 'Plot A1'},
        {'plot_id': 'A2', 'name': 'Plot A2'},
        {'plot_id': 'A3', 'name': 'Plot A3'},
        {'plot_id': 'A4', 'name': 'Plot A4'},
        {'plot_id': 'B1', 'name': 'Plot B1'},
        {'plot_id': 'B2', 'name': 'Plot B2'},
        {'plot_id': 'B3', 'name': 'Plot B3'},
        {'plot_id': 'B4', 'name': 'Plot B4'},
        {'plot_id': 'C1', 'name': 'Plot C1'},
        {'plot_id': 'C2', 'name': 'Plot C2'},
        {'plot_id': 'C3', 'name': 'Plot C3'},
        {'plot_id': 'C4', 'name': 'Plot C4'}]

@app.route('/')
def index():
    return render_template('index.html')

# Accessing user registration
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        vehicle_number = request.form.get('vehicle_number')
        password = request.form.get('password')

        # Store the user data in the database
        users_collection.insert_one({
            'fullname': fullname,
            'email': email,
            'phone': phone,
            'vehicle_number': vehicle_number,
            'password': password})
        flash('Account created successfully. You can now sign in.', 'success')
        return redirect(url_for('signin'))

    return render_template('signup.html')

@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Search for a user with the provided username (email or full name)
        user = users_collection.find_one({'$or': [{'email': username}, {'fullname': username}]})

        if user and user['password'] == password:
            # Store user's email (or other identifier) in the session
            session['user_email'] = user['email']

            return redirect(url_for('home'))  # Redirect to the homepage or any other desired page
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('signin.html')

@app.route('/profile',methods = ['Post', 'GET'])
def profile():
    user_email = session.get('user_email')
    if user_email:
        # Retrieve user data using the stored email
        user = users_collection.find_one({'email': user_email})
        if user:
            return render_template('profile.html', user=user)
        else:
            flash('User data not found.', 'error')
            return redirect(url_for('signin'))  # Redirect to sign-in if user data is not found
    else:
        flash('Please sign in to access the profile.', 'error')
        return redirect(url_for('signin'))  # Redirect to sign-in if user email is not stored in session


validation_codes = {}
bufferdata = {}

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = users_collection.find_one({'email': email})

        if user:
            validation_code_value = generate_validation_code()  # Use a different variable name
            validation_codes[email] = validation_code_value

            msg = Message('Password Reset Request', sender='your_email@gmail.com', recipients=[email])
            msg.body = f'Your validation code: {validation_code_value}'
            mail.send(msg)

            session['user_email'] = email  # Store email in session for later use
            return redirect(url_for('reset_password'))

        flash('Invalid email. Please try again.', 'error')

    return render_template('forgot_password.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        validation_code = request.form.get('validation_code')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if validation_code == session.get('validation_code', None):
            if new_password == confirm_password:
                email = session.get('user_email')
                users_collection.update_one({'email': email}, {'$set': {'password': new_password}})

                flash('Password has been reset successfully. You can now sign in with your new password.', 'success')
                session.pop('validation_code', None)
                session.pop('email', None)
                return redirect(url_for('signin'))
            else:
                flash('Passwords do not match. Please try again.', 'error')
        else:
            flash('Invalid validation code. Please try again.', 'error')

    return render_template('reset_password.html')

@app.route('/home')
def home():
    return render_template('home.html',plots = plots)

@app.route('/available_dates')
def get_available_dates():
    available_dates = get_consecutive_dates()  # Use the same function as in populate_plots
    return jsonify({'available_dates': available_dates})

@app.route('/available_time_intervals', methods=['POST', 'GET'])
def available_time_intervals():
    data = request.json
    selected_date_str = data['selectedDate']

    # Convert the selected date string to a datetime object
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

    current_datetime = datetime.now()
    today = current_datetime.date()

    # Define start and end times for generating time intervals
    start_time = datetime.strptime("00:00", '%H:%M')
    end_time = datetime.strptime("23:30", '%H:%M')

    # If the selected date is today, adjust start time based on the current time
    if selected_date == today:
        current_time = current_datetime.time()
        current_hour, current_minute = current_time.hour, current_time.minute

        # Calculate the next 30-minute interval
        if current_minute >= 30:
            current_hour += 1
            current_minute = 0
        else:
            current_minute = 30

        start_time = start_time.replace(hour=current_hour, minute=current_minute)

    # Generate time intervals at 30-minute increments with "00" or "30" in the minutes part
    time_intervals = []
    while start_time <= end_time:
        # Format the time to display only the hour and minute with "00" or "30" minutes
        if start_time.minute == 0 or start_time.minute == 30:
            time_intervals.append(start_time.strftime('%H:%M'))
        start_time += timedelta(minutes=30)

    print(selected_date)
    print(time_intervals)
    response_data = {
        'time_intervals': time_intervals
    }

    return jsonify(response_data), 200

'''@app.route('/available_time_intervals', methods=['POST','GET'])
def available_time_intervals():
    data = request.json
    selected_date_str = data['selectedDate']

    # Convert the selected date string to a datetime object
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

    current_datetime = datetime.now()
    today = current_datetime.date()
    print("Selected Date:", selected_date)
    print("Today's Date:", today)

    # Define start and end times for generating time intervals
    start_time = datetime.strptime("00:00", '%H:%M')
    end_time = datetime.strptime("23:30", '%H:%M')

    # If the selected date is today, adjust start time
    if selected_date == today:
        current_time = current_datetime.time()
        start_hour, start_minute = start_time.hour, start_time.minute
        current_hour, current_minute = current_time.hour, current_time.minute

        new_hour = start_hour + current_hour
        new_minute = start_minute + current_minute + 30  # Add 30 minutes

        # Check for overflow in minutes
        if new_minute >= 60:
            new_hour += 1
            new_minute -= 60

        # Ensure the time remains within bounds
        new_hour = min(23, new_hour)
        new_minute = min(30, new_minute)

        start_time = start_time.replace(hour=new_hour, minute=new_minute)

    # Generate time intervals at 30-minute increments with "00" and "30" in the minutes part
    time_intervals = []
    while start_time <= end_time:  # Change '<' to '<=' here
        # Format the time to display only the hour and minute with "00" or "30" minutes
        if start_time.minute == 0 or start_time.minute == 30:
            time_intervals.append(start_time.strftime('%H:%M'))
        start_time += timedelta(minutes=30)

    print(selected_date)
    print(time_intervals)

    print("Today's Date:", today)
    response_data = {
        'time_intervals': time_intervals
    }

    return jsonify(response_data), 200'''


'''@app.route('/available_time_intervals', methods=['POST','GET'])
def available_time_intervals():
    data = request.json
    selected_date_str = data['selectedDate']

    # Convert the selected date string to a datetime object
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

    current_datetime = datetime.now()
    today = current_datetime.date()

    # Define start and end times for generating time intervals
    start_time = datetime.strptime("00:00", '%H:%M')
    end_time = datetime.strptime("23:30", '%H:%M')

    # If the selected date is today, adjust start time
    if selected_date == today:
        current_time = current_datetime.time()
        start_hour, start_minute = start_time.hour, start_time.minute
        current_hour, current_minute = current_time.hour, current_time.minute

        new_hour = start_hour + current_hour
        new_minute = start_minute + current_minute + 30  # Add 30 minutes

        # Check for overflow in minutes
        if new_minute >= 60:
            new_hour += 1
            new_minute -= 60

        # Ensure the time remains within bounds
        new_hour = min(23, new_hour)
        new_minute = min(30, new_minute)

        start_time = start_time.replace(hour=new_hour, minute=new_minute)

    # Generate time intervals at 30-minute increments with "00" and "30" in the minutes part
    time_intervals = []
    while start_time < end_time:
        # Format the time to display only the hour and minute with "00" or "30" minutes
        if start_time.minute == 0 or start_time.minute == 30:
            time_intervals.append(start_time.strftime('%H:%M'))
        start_time += timedelta(minutes=30)

    print(selected_date)
    print(time_intervals)
    response_data = {
        'time_intervals': time_intervals
    }

    return jsonify(response_data), 200'''


'''@app.route('/available_time_intervals', methods=['POST'])
def available_time_intervals():
    data = request.json
    selected_date_str = data['selectedDate']

    # Convert the selected date string to a datetime object
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

    current_datetime = datetime.now()
    today = current_datetime.date()

    # Define start and end times for generating time intervals
    start_time = datetime.strptime("00:00", '%H:%M')
    end_time = datetime.strptime("23:30", '%H:%M')

    # If the selected date is today, adjust start time
    if selected_date == today:
        current_time = current_datetime.time()
        start_hour, start_minute = start_time.hour, start_time.minute
        current_hour, current_minute = current_time.hour, current_time.minute

        new_hour = start_hour + current_hour
        new_minute = start_minute + current_minute + 30  # Add 30 minutes

        # Check for overflow in minutes
        if new_minute >= 60:
            new_hour += 1
            new_minute -= 60

        # Ensure the time remains within bounds
        new_hour = min(23, new_hour)
        new_minute = min(30, new_minute)

        start_time = start_time.replace(hour=new_hour, minute=new_minute)

    # Generate time intervals at 30-minute increments
    time_intervals = []
    while start_time < end_time:
        # Format the time to display only the hour and minute
        time_intervals.append(start_time.strftime('%H:%M'))
        start_time += timedelta(minutes=30)

    print(selected_date)
    print(time_intervals)
    response_data = {
        'time_intervals': time_intervals
    }

    return jsonify(response_data), 200'''


@app.route('/get_plot_availability', methods=['GET', 'POST'])
def get_plot_availability():
    data = request.json
    booking_date = data['bookingDate']
    booking_time = data['bookingTime']
    booking_hours = int(data['bookingHours'])
    bufferdata['date'] = booking_date
    bufferdata['time'] = booking_time
    bufferdata['hours'] = booking_hours
    try:

        # Calculate the start time and end time of the booking
        start_time = datetime.strptime(booking_time, '%H:%M')
        end_time = start_time + timedelta(hours=booking_hours)

        booking_start_minute = start_time.hour * 60 + start_time.minute
        booking_end_minute = end_time.hour * 60 + end_time.minute

        # Get all plots
        all_plots = plots_collection.find()

        # Create a dictionary to store plot availability
        plot_availability = {}

        # Iterate over each plot
        for plot in all_plots:
            plot_id = plot['plot_id']
            occupied_slots = plot['occupied_slots'].get(booking_date, {})

            # Initialize availability status for the plot
            is_plot_available = True

            # Iterate over each minute interval in the start time and booking hours range
            for minute in range(booking_start_minute, booking_end_minute,30):
                # Determine the time slot using total minutes
                time_slot = f"{minute}-{minute+30}"
                is_available = occupied_slots.get(time_slot, False)
                if not is_available:
                    is_plot_available = False
                    break  # Exit loop if any slot is not available

            # Set the availability status for the plot
            plot_availability[plot_id] = is_plot_available
        response = {
            'plotAvailability': plot_availability
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def populateprice():
    prices = [{'principal_amount' : 50, 'additional_amount_per_hour' : 20}]
    price_collection.insert_many(prices)
#populateprice()

@app.route('/payment', methods = ['GET','POST'])
def payment():
    plot_id = request.args.get('plot_id')
    # Calculate the total amount based on the fetched data
    prices_document = price_collection.find_one({})
    if prices_document:
        principal_amount= int(prices_document.get('principal_amount'))
        additional_amount_per_hour =int( prices_document.get('additional_amount_per_hour'))
    total_hours = bufferdata['hours']
    total_amount = principal_amount + ((total_hours-1) * additional_amount_per_hour)

    # Apply discount for more than 5 hours
    if total_hours > 5:
        discount_percent = 1.5
        discount_amount = (total_amount * discount_percent) / 100
        total_amount -= discount_amount

    user_email = session.get('user_email')  # Replace with the actual key used in your session
    return render_template('payment.html', user_email=user_email,plotId = plot_id, booking_date=bufferdata['date'],booking_time=bufferdata['time'],hours=total_hours,total_amount=total_amount,additional = additional_amount_per_hour,principal = principal_amount )

@app.route('/update_availability', methods=['POST', 'GET'])
def update_availability():
    booking_data = request.json  # Get data from the request body
    plot_id = booking_data['plotId']
    booking_hours = int(booking_data['hours'])
    booking_date = booking_data['bookingDate']
    booking_time = booking_data['bookingTime']  # Assuming this field is provided in the JSON

    start_time = datetime.strptime(booking_time, '%H:%M')
    end_time = start_time + timedelta(hours=booking_hours)


    # Calculate booking start and end minutes since midnight
    booking_start_minute = start_time.hour * 60 + start_time.minute
    booking_end_minute = end_time.hour * 60 + end_time.minute

    # Get the plot entry from the collection
    plot = plots_collection.find_one({'plot_id': plot_id})

    if plot:
        # Get the occupied_slots for the specific booking date
        occupied_slots = plot['occupied_slots'].get(booking_date, {})

        # Update the occupied_slots based on the booking start and end minutes
        for minute in range(booking_start_minute, booking_end_minute, 30):
            time_slot = f"{minute}-{minute+30}"
            occupied_slots[time_slot] = False

        # Update the occupied_slots for the specific booking date in the plot entry
        plot['occupied_slots'][booking_date] = occupied_slots
        plots_collection.replace_one({'plot_id': plot_id}, plot)

        # Store booking details in booking history collection
        bookings_collection.insert_one(booking_data)

        return jsonify({'message': 'Availability updated and booking details stored'})
    else:
        return jsonify({'error': 'Plot not found'})

@app.route('/booking_history')
def booking_history():
    return render_template('booking_history.html')

@app.route('/get_user_booking_history', methods=['POST', 'GET'])
def get_user_booking_history():
    user_email = session.get('user_email')

    # Retrieve booking history for the user
    booking_history = list(bookings_collection.find({'userEmail': user_email}, {'_id': 0}))

    return jsonify(booking_history)

# Replace this with your MongoDB setup and actual data retrieval logic
def get_user_current_bookings_data(user_email):
    current_time = datetime.now()
    current_date = current_time.date()
    user_bookings = list(bookings_collection.find({'user_email': user_email},
                            {'bookingDate': current_date.strftime('%Y-%m-%d')}
                        ))
    current_and_upcoming_bookings = []
    for booking in user_bookings:
        booking_start_time_str = booking['bookingTime']  # Replace with your field name
        booking_duration_hours = int(booking['hours'])  # Replace with your field name
        booking_start_time = datetime.strptime(booking_start_time_str, '%H:%M')

        # Calculate the booking end time
        booking_end_time = booking_start_time + timedelta(hours=booking_duration_hours)
        current_and_upcoming_bookings = []

        # Filter bookings based on start time and duration
        if  booking_end_time >= current_time:
            current_and_upcoming_bookings.append({
                'plot': booking['plotId'],  # Replace with your field name
                'booking_start_time': booking_start_time,
                'booking_end_time': booking_end_time,
                'TotalAmount' : booking['totalAmount']
            })

    return current_and_upcoming_bookings

@app.route('/get_user_current_bookings', methods=['GET'])
def get_user_current_bookings():
    user_email = session.get('user_email')
    print(user_email)
    if user_email:
        current_bookings_data = get_user_current_bookings_data(user_email)
        print(current_bookings_data)
        return jsonify(current_bookings_data)
    return jsonify([])  # Return an empty array if user is not logged in


@app.route('/update-profile', methods=['POST','GET'])
def update_profile():
    try:
        user_email = session.get('user_email')
          # Assuming you send user_id from the frontend
        profile = request.json
        fullName = profile['fullName']
        vehicleNumber = profile['vehicleNumber']
        contactNumber = profile['contactNumber']

        users_collection.update_one(
            {'email': user_email},
            {
                '$set': {
                    'fullname': fullName,
                    'vehicle_number': vehicleNumber,
                    'phone': contactNumber
                }
            }
        )

        return jsonify({'message': 'Profile updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)})

#Admin Backend
def populateadmin():
    admin_data = [{"parkinglot_id":"Mantri-Square","password":"123456@MantriSquare"}]
    admin_collection.insert_many(admin_data)
#populateadmin()

@app.route('/adminsignin',methods = ['GET', 'POST'])
def adminsignin():
    if request.method == 'POST':
        parkinglot_id = request.form.get('parkinglot_id')
        password = request.form.get('password')

        # Search for a user with the provided username (email or full name)
        admin = admin_collection.find_one({'$or': [{'parkinglot_id': parkinglot_id}]})

        if admin and admin['password'] == password:
            # Store user's email (or other identifier) in the session
            session['parkinglot_id'] = admin['parkinglot_id']

            return redirect(url_for('admininterface'))  # Redirect to the homepage or any other desired page
        else:
            flash('Invalid parkinglot_id or password. Please try again.', 'error')

    return render_template('adminsignin.html')

@app.route('/admininterface',methods = ['GET','POST'])
def admininterface():
    prices_document = price_collection.find_one({})
    if prices_document:
        principal= prices_document.get('principal_amount')
        additional = prices_document.get('additional_amount_per_hour')
    return render_template('admininterface.html',plots = plots, principal_amount = principal, additional_amount = additional)

@app.route('/admin_bookings_page',methods = ['GET', 'POST'])
def admin_booking_page():
    return render_template('admin_bookings.html')

# Route to handle admin booking history request
@app.route('/admin_bookings', methods=['GET', 'POST'])
def get_admin_booking_history():
    search_date = request.args.get('date')

    # Retrieve booking history from the database based on the selected date
    booking_history = bookings_collection.find({'bookingDate': search_date})

    # Initialize an empty list to hold the final results
    results = []

    # Iterate through the booking history and retrieve user data for each booking
    for booking in booking_history:
        user_email = booking['userEmail']
        user_data = users_collection.find_one({'email': user_email})
        if user_data:
            booking_data = {
                'bookingDate': booking['bookingDate'],
                'bookingTime': booking['bookingTime'],
                'plotId': booking['plotId'],
                'hours': booking['hours'],
                'totalAmount': booking['totalAmount'],
                'paymentMethod': booking['paymentMethod'],
                'userEmail': booking['userEmail'],
                'vehicleNumber': user_data['vehicle_number']
            }
            results.append(booking_data)

    return jsonify(results)

'''@app.route('/get_current_bookings')
def get_current_bookings():
    current_date = datetime.now().date()
    current_time = datetime.now().time()

    current_bookings = list(bookings_collection.find({
        'bookingDate': current_date,
    }))

    for booking in current_bookings:
        booking_start_datetime = datetime.combine(booking['booking_date'], booking['booking_time'])
        booking_end_datetime = booking_start_datetime + timedelta(hours=booking['hours'])
        current_datetime = datetime.combine(current_date, current_time)

        if booking_start_datetime <= current_datetime <= booking_end_datetime:
            booking['end_time'] = booking_end_datetime.time()
        else:
            current_bookings.remove(booking)

    return jsonify({'current_bookings': current_bookings})'''

@app.route('/update_prices', methods=['POST'])
def update_prices():
    new_principal_amount = request.form.get('principal_amount')
    new_additional_amount = request.form.get('additional_amount_per_hour')

    # Update the document in the collection
    price_collection.update_one({}, {'$set': {
        'principal_amount': new_principal_amount,
        'additional_amount_per_hour': new_additional_amount
    }})

    flash('Prices updated successfully.', 'success')
    return redirect(url_for('admininterface'))

@app.route('/cancel_booking', methods=['POST','GET'])
def cancel_booking():
    return render_template('cancel.html')

@app.route('/cancel_data', methods=['POST','GET'])
def cancel_data():
    try:
        data = request.json
        booking_date = data.get('bookingDate')
        start_time = data.get('startTime')
        plot_id = data.get('plotId')

        # Find and delete the booking based on provided details
        result = bookings_collection.delete_one({
            'bookingDate': booking_date,
            'bookingTime': start_time,
            'plotId': plot_id
        })

        if result.deleted_count == 1:
            response = {'message': 'Booking canceled successfully.'}
        else:
            response = {'message': 'Booking not found or could not be canceled.'}
        return jsonify(response), 200
    except Exception as e:
        print('Error:', str(e))
        return jsonify({'message': 'An error occurred while canceling the booking.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
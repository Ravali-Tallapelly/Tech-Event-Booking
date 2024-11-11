from flask import Blueprint, render_template, flash, request, redirect, url_for, session
from app.models import Event, User, Booking
from werkzeug.security import generate_password_hash
from app import db
from datetime import datetime
from sqlalchemy import extract
from flask_login import current_user
routes = Blueprint('main_routes', __name__)

def valid_credentials(username, password):
    user = User.query.filter_by(username=username).first()
    print("Queried User:", user)
    if user and user.check_password(password):
        return user  # Return the user object if credentials are valid
    return None  # Return None if invalid credentials

@routes.route('/')
def index():
    events = Event.query.all()  # Fetch all events from the database
    return render_template('index.html', events=events)

@routes.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        account_type = request.form.get('account_type')
        
        # Validation and user creation logic
        if not username or not email or not password:
            flash('All fields are required!')
            return redirect(url_for('main_routes.signup'))
        
        password_hash = generate_password_hash(password)
        if User.query.filter_by(username=username).first():
            flash("Username already taken. Please choose a different username.")
            return redirect(url_for('main_routes.signup'))
        
        user = User(username=username, email=email, password_hash=password_hash, account_type=account_type)
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully!")
        return redirect(url_for('main_routes.signin'))
    return render_template("signup.html")

@routes.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = valid_credentials(username, password)
        if user:
            session['user_id'] = user.id  # Store the user_id in the session
            return redirect(url_for('main_routes.dashboard'))
        else:
            flash("Invalid credentials.")
    return render_template('signin.html')

@routes.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to access the dashboard.")
        return redirect(url_for('main_routes.signin'))
    
    user = User.query.get(session['user_id'])
    if user:
        bookings = Booking.query.filter_by(user_id=user.id).all()
        month = request.args.get('month', type=int)
        
        if month:
            events = Event.query.filter(db.extract('month', Event.date) == month).all()
        else:
            events = Event.query.all()
        
        return render_template('dashboard.html', user=user, bookings=bookings, events=events, selected_month=month)
    else:
        flash("User not found.")
        return redirect(url_for('main_routes.signin'))


@routes.route('/add_event', methods=['GET', 'POST'])
def add_event():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash("Please log in to add an event.")
        return redirect(url_for('main_routes.signin'))
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        date = request.form.get('date')
        location = request.form.get('location')
        description = request.form.get('description')
        tickets = request.form.get('tickets', 0)  # Default to 0 if tickets field is not provided
        
        # Validate that all required fields are filled
        if not name or not date or not location or not description:
            flash("All fields are required.")
            return redirect(url_for('main_routes.add_event'))
        
        # Convert date to datetime object
        try:
            event_date = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.")
            return redirect(url_for('main_routes.add_event'))
        
        # Create a new event instance
        event = Event(name=name, date=event_date, location=location, description=description, tickets=int(tickets))
        
        # Add the event to the database
        db.session.add(event)
        db.session.commit()
        
        flash("Event added successfully!")
        return redirect(url_for('main_routes.dashboard'))
    
    return render_template('add_event.html')

@routes.route('/book_event/<int:event_id>', methods=['GET', 'POST'])
def book_event(event_id):
    # Check if the user is logged in
    if 'user_id' not in session:
        flash("Please log in to book an event.")
        return redirect(url_for('main_routes.signin'))
    
    # Fetch the event by its ID
    event = Event.query.get(event_id)
    
    # Check if event exists
    if not event:
        flash("Event not found.")
        return redirect(url_for('main_routes.dashboard'))
    
    # Check if there are tickets available
    if event.tickets <= 0:
        flash("Sorry, no tickets are available for this event.")
        return redirect(url_for('main_routes.dashboard'))
    
    if request.method == 'POST':
        # Update the event ticket count
        event.tickets -= 1  # Decrease available tickets by 1
        
        # Create a new booking entry with status set to "Confirmed"
        booking = Booking(user_id=session['user_id'], event_id=event.id, date=datetime.now(), status='Confirmed')
        db.session.add(booking)
        db.session.commit()

        # Commit the changes to the event ticket count
        db.session.commit()

        flash("You have successfully booked a ticket for the event!")
        return redirect(url_for('main_routes.dashboard'))

    # If the method is GET, just render the event booking page
    return render_template('book_event.html', event=event)

@routes.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully.")
    return redirect(url_for('main_routes.signin'))
@routes.route('/dashboard/bookings')
def upcoming_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('upcoming_bookings.html', bookings=bookings)

@routes.route('/manage_bookings', methods=['GET', 'POST'])
def manage_bookings():
    # Get the current user's bookings
    bookings = Booking.query.filter_by(user_id=session['user_id']).all()

    if request.method == 'POST':
        # Check if the user wants to unregister from an event
        booking_id = request.form.get('booking_id')
        booking_to_remove = Booking.query.get(booking_id)

        if booking_to_remove:
            # Update the event's ticket count (increase by 1)
            event = Event.query.get(booking_to_remove.event_id)
            event.tickets += 1
            db.session.commit()

            # Remove the booking
            db.session.delete(booking_to_remove)
            db.session.commit()

            flash("You have successfully unregistered from the event.")
            return redirect(url_for('main_routes.manage_bookings'))

    return render_template('manage_bookings.html', bookings=bookings)
@routes.route('/unregister_booking/<int:booking_id>', methods=['POST'])
def unregister_booking(booking_id):
    booking = Booking.query.get(booking_id)
    
    if not booking or booking.user_id != current_user.id:
        flash("Booking not found.")
        return redirect(url_for('main_routes.manage_bookings'))
    
    # Increase the ticket count of the event
    event = booking.event
    event.tickets += 1
    
    # Delete the booking
    db.session.delete(booking)
    db.session.commit()
    
    flash("You have successfully unregistered from the event.")
    return redirect(url_for('main_routes.manage_bookings'))

@routes.route('/my_bookings')
def my_bookings():
    user_id = session.get('user_id')  # Ensure you are tracking logged-in users with a session or authentication
    if user_id:
        # Fetch bookings for the logged-in user
        bookings = Booking.query.filter_by(user_id=user_id).all()
        return render_template('my_bookings.html', bookings=bookings)
    else:
        # Redirect to login if the user is not logged in
        return redirect(url_for('main_routes.login'))
@routes.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')
@routes.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("Please log in to view your profile.")
        return redirect(url_for('main_routes.signin'))
    
    user = User.query.get(session['user_id'])  # Fetch user info from DB
    if not user:
        flash("User not found.")
        return redirect(url_for('main_routes.dashboard'))
    
    return render_template('profile.html', user=user)
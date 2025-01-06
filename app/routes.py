from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm, SessionForm, SaveForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app.models import User, Session
from flask import request
from urllib.parse import urlsplit
from app.report import query_api, create_df

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
#If i try to access the index page without being logged in, I will be redirected to the login page.
@login_required
def index():
    form = SessionForm()

    if form.validate_on_submit():
        lat = form.lat.data
        lng = form.lng.data
        date = form.date.data

        return redirect( url_for('report', lat=lat, lng=lng, date=date) )

    return render_template('index.html', form=form, title='Home')


@app.route('/report/<lat>/<lng>/<date>', methods=['POST', 'GET'])
def report(lat, lng, date):
    reply = query_api(lat, lng, date)
    hours = reply["hours"]
    df = create_df(hours)

    # Convert DataFrame to list of dictionaries
    table_data = df.to_dict(orient='records')
    form = SaveForm()

    return render_template('report.html', tables=table_data, form=form)

@app.route('/save_row', methods=['POST'])
def save_row():
    form = SaveForm()
    # Validate the form to ensure the CSRF token and other requirements are correct
    if form.validate_on_submit():
        # Extract the data from the form submission
        row_data = request.form.to_dict()

        # Extract individual values from the row_data dictionary
        row_session_at = row_data.get('Session time')
        row_waveHeight = row_data.get('Wave Height')
        row_primarySwellHeight = row_data.get('Primary Swell Height')
        row_primarySwellDirection = row_data.get('Primary Swell Direction')
        row_primarySwellPeriod = row_data.get('Primary Swell Period')
        row_secondarySwellHeight = row_data.get('Secondary Swell Height')
        row_secondarySwellDirection = row_data.get('Secondary Swell Direction')
        row_secondarySwellPeriod = row_data.get('Secondary Swell Period')
        row_windSpeed = row_data.get('Wind Speed')
        row_windDirection = row_data.get('Wind Direction')
        row_temperature = row_data.get('Temperature')
        row_pressure = row_data.get('Pressure')

        # Create a new instance of YourModel with the extracted data
        new_session = Session(session_at=row_session_at, waveHeight=row_waveHeight, primarySwellHeight=row_primarySwellHeight, primarySwellDirection=row_primarySwellDirection,
                              primarySwellPeriod=row_primarySwellPeriod, secondarySwellHeight=row_secondarySwellHeight, secondarySwellDirection=row_secondarySwellDirection,
                              secondarySwellPeriod=row_secondarySwellPeriod, windSpeed=row_windSpeed, windDirection=row_windDirection, temperature=row_temperature, pressure=row_pressure,
                              user = current_user
                            )
        
        # Add the new record to the database session and commit it
        db.session.add(new_session)
        db.session.commit()
        flash('Your post is now live!')
        
        return redirect(url_for('index'))
    else:
        return redirect(url_for('report'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    sessions = db.session.scalars(current_user.sessions_user()).all()

    return render_template('user.html', user=user, posts=posts, sessions=sessions)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

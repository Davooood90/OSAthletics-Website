# Import library for os functions
import os

# Import libraries for time
import calendar
from datetime import datetime, date, timedelta

# Import library for generating universally unique identifiers
import uuid

# Import libraries for dealing with mysql
import mysql.connector
from mysql.connector import Error
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import libraries for building/managing web applications
from flask import Flask, redirect, render_template, request, session, url_for, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer

# Custom functions scored in another directory
from funcs.drive_helper import build_drive_service, upload_file, get_file
from funcs.calendar_helper import build_cal_service, build_event, create_event, get_events, update_event, delete_event
from funcs.sql_helper import sql_connect, sql_close, sql_get, sql_rmv, sql_insert, sql_update
from funcs.email_helper import email_create, email_send, email_verify
from funcs.teams import Roster, Achievements
from funcs.accounts import Student, Parent, Coach

# Create environmental variables
os.environ['ENCRYPTED_SALT'] = 'my_precious_two'
os.environ['GMAIL_APP'] = 'vqsxfcrjymeqgquw'
os.environ['SQL_SERVER'] = 'AnotherR@ndomAcc0unt'

# Global dictionary that contains classes
TABLE = {"student": Student, "parent": Parent, "coach": Coach}

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = os.urandom(36)
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('ENCRYPTED_SALT')
app.config['GMAIL_KEY'] = os.environ.get('GMAIL_APP')
app.config['SQL_KEY'] = os.environ.get('SQL_SERVER')
Session(app)

# Register
@app.route("/register", methods=["GET", "POST"])
def register(page=""):
    if request.method == "POST":
        try:
            # Connect To Server
            connection = sql_connect(app.config['SQL_KEY'])
            cursor = connection.cursor()

            # Get Information
            test_case = (str(request.form.get("email")),)
            used = sql_get("confirmed", "accounts", "email = %s", test_case, cursor)

            # Is the email already registered
            if used != []:
                if used[0][0] == int(0):
                    sql_rmv(connection, "accounts", "email = %s", test_case, cursor)
                else:
                    flash("error This account already exists.")
                    return redirect("/register")

            # Create Account
            test_case = (uuid.uuid4().hex, request.form.get('email'), generate_password_hash(request.form.get('password')), request.form.get('select'), False)
            sql_insert(connection, "accounts", "(accountId, email, password, type, confirmed)", "(%s, %s, %s, %s, %s)", test_case, cursor)
        except mysql.connector.Error as error:
            flash("error An error occured.")
            return redirect("/register")
        finally:
            sql_close(connection, cursor)

        # Send Verification Email
        try:
            # Generate JSON Web Token
            serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            token =  serializer.dumps((request.form.get("email")), salt=app.config['SECURITY_PASSWORD_SALT'])
            confirm_url = url_for('confirm', token=token, _external=True)

            # Contact Information
            email_receive = ""

            # Determine Where to Send Email by Account Type
            if request.form.get('select') == "student":
                email_receive = request.form.get("email")
            elif request.form.get('select') == "parent":
                token =  serializer.dumps((request.form.get("email"), request.form.get("conf-email")), salt=app.config['SECURITY_PASSWORD_SALT'])
                confirm_url = url_for('confirm', token=token, _external=True)
                email_receive = request.form.get("conf-email")
            elif request.form.get('select') == "coach":
                if "@epsb.ca" in request.form.get("email"):
                    email_receive = request.form.get("email")
                else:
                    email_receive = "oldsconathletics@gmail.com"

            # Email Structure
            message = MIMEMultipart("alternative")
            message["Subject"] = "OSAthletics Account Confirmation"
            message["From"] = "oldsconathletics@gmail.com"
            message["To"] = email_receive
           
            # Email Content
            mail = email_create(confirm_url)
            email_send(mail, message, "oldsconathletics@gmail.com", app.config['GMAIL_KEY'], email_receive)

            # Popup Message
            flash("success Verification email was successfully sent.")
            return redirect(f"/login")
        except:
            # Popup Message
            flash("error Verification email was unsuccessfully sent.")
            return redirect("/register")
    else:
        # Render Template for Flask Web App
        return render_template("register.html", page=page)


# Email Verification
@app.route('/confirm/<token>')
def confirm(token):  # Accept a JSON Web Token
    try:
        # Decode the Token
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            # Checks if the Token is still Valid
            confirm_token = serializer.loads(
                token,
                salt=app.config['SECURITY_PASSWORD_SALT'],
                max_age=600
            )
        except:
            confirm_token = False
        # Retrieve Email From Token
        email = confirm_token

        # Verify Email Address
        email_verify(email)
    except:
        flash('error The confirmation link is invalid or has expired.')
    return redirect("/")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("email"):
            flash("error Must provide email")
            return redirect("/login")
        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("error Must provide password")
            return redirect("/login")

        # Query Database for Account
        try:
            # Connect to MySQL Server
            connection = sql_connect(app.config['SQL_KEY'])
            cursor = connection.cursor()

            # Search For Account
            test_case = (str(request.form.get("email")),)
            used = sql_get("*", "accounts", "email = %s", test_case, cursor)

            # If An Empty Array is Returned
            if used == [] or not check_password_hash(used[0][2], request.form.get("password")) or used[0][-1] == 0:
                flash("error Invalid email or password")
                return redirect("/login")
           
            # Store Session Information
            session["user_id"] = used[0][0]
            session["type"] = used[0][3]

            # Retrieve User's First Name
            if used[0][3] != "admin":  # Admin Account Does Not Have A Name
                if used[0][3] == "student":
                    name = sql_get("fname", "students", "accountId = %s", (str(used[0][0]),), cursor)
                elif used[0][3] == "parent":
                    name = sql_get("fname", "parents", "accountId = %s", (str(used[0][0]),), cursor)
                elif used[0][3] == "coach":
                    name = sql_get("fname", "coaches", "accountId = %s", (str(used[0][0]),), cursor)
               
                # If No Name Was Retrieved
                if name[0][0] == '':
                    flash("success Login Successful. Please finish setting up your account")
                    return redirect("/settings")

                # If A Name Was Successfully Retrieved
                session["name"] = name[0][0]
           
            flash("success Login Successful")
        finally:
            sql_close(connection, cursor)

        # Redirect user to home page
        return redirect('/')
    else:
        # Render Template for Flask Web App
        return render_template("login.html")


# Logout
@app.route("/logout")
def logout():
    # Forget any session information
    session.clear()

    # Redirect user to login form
    return redirect("/")


# News & Events
@app.route("/news")
def schedule():
    try:
        # Connect to MySQL Server
        connection = sql_connect(app.config['SQL_KEY'])    
        cursor = connection.cursor(dictionary=True)

        # Retrieve Data (By Newest First)
        sql_select_Query = "SELECT * FROM information ORDER BY dateposted DESC"
        cursor.execute(sql_select_Query)
        info = cursor.fetchall()
        sql_select_Query = "SELECT * FROM highlights ORDER BY dateposted DESC"
        cursor.execute(sql_select_Query)
        highlights = cursor.fetchall()
    finally:
        sql_close(connection, cursor)

    # Render Template for Flask Web App
    return render_template("news.html", info=info, highlights=highlights)


# Team Page
@app.route("/team/<sport>")
def team(sport):
    # Dictionary of Google Calendar Links
    SCHEDULE = {
        "badminton": "j9hgch35kc37qq7ks0op09ido3eetjub%40import.calendar.google.com&ctz=America%2FEdmonton",
        "mens-basketball": "9o1ku4sjemfep0k7l624f9qcousd2v2h%40import.calendar.google.com&ctz=America%2FEdmonton",
        "womens-basketball": "i9ca2m1o9ftuc8im8ihqtffmm999n593%40import.calendar.google.com&ctz=America%2FEdmonton",
        "cross-country": "b2d581e81cc498578c98fc4adc0a83ff9cc2d326f98b0c2b2d1269e4b8359fbf%40group.calendar.google.com&ctz=America%2FEdmonton",
        "mens-handball": "gqhmdr8ek9jtnckrt6jvsb6vsgat1l69%40import.calendar.google.com&ctz=America%2FEdmonton",
        "womens-handball": "2k2re2k55sbiv14hug53ta4if5d2it3i%40import.calendar.google.com&ctz=America%2FEdmonton",
        "mens-soccer": "bnghmiflg1661u6jd0ue07eqes0ukdnh%40import.calendar.google.com&ctz=America%2FEdmonton",
        "womens-soccer": "mpgljgnqu4hc9ibrl5qqvtek36l88lki%40import.calendar.google.com&ctz=America%2FEdmonton",
        "swimming": "3727c7d34210a8b2e2c8065531b5b14caec91d0b922b35190f307ae6c47df88a%40group.calendar.google.com&ctz=America%2FEdmonton",
        "test_case-&-field": "2e7a89bd75e990e974d3a538079d710fb16df3995e0f6da1cdb3d6ba7ea88257%40group.calendar.google.com&ctz=America%2FEdmonton",
        "mens-volleyball": "v92vtglrqhpg6g2gmmh9nle07v2htt7t%40import.calendar.google.com&ctz=America%2FEdmonton",
        "womens-volleyball": "737vpvt38vnv5vn4hqbb3s6aepokc540%40import.calendar.google.com&ctz=America%2FEdmonton"
    }

    try:
        # Connect to MySQL Server
        connection = sql_connect(app.config['SQL_KEY'])
        cursor = cursor = connection.cursor (dictionary=True)  # Set Mode to Dictionary

        # Create Team Object
        team = Roster(sport, cursor)

        # Create Achievements Object
        achievements = Achievements(sport, cursor)

        # Display Team Information
        return render_template("teams.html", team_name=sport, players=team.sortedplayers(),
                               coaches=team.sortedcoaches(), achievements=achievements.getachievements(), schedule=SCHEDULE[sport])
    except mysql.connector.Error as error:
        flash("error An error occured")
        return redirect('/')
    finally:
        sql_close(connection, cursor)


# Contact
@app.route("/contact")
def contact():
    # Render Template for Flask Web App
    return render_template("contact.html")


# OSAthletic Manager
@app.route("/manager/<tag>")
@app.route("/manager/<tag>/<action>", methods=['POST', 'GET'])
def manage(tag = None, action = None):
    # Check if account has admin permisions
    if session.get("type") == "admin":
        if request.method == "POST":  # If form submission
            try:
                # Connect to MySQL Server
                connection = sql_connect(app.config['SQL_KEY'])
                cursor = connection.cursor()
                if tag == "users":  # If User Management
                    if request.form.get("title") == "" or request.form.get("date") == "" or request.form.get("file") == "":  # Check if all fields are filled
                        flash("error Please fill in all the fields.")
                        return redirect(f"/manager/{tag}")

                    else:
                        # Upload File to Google Drive
                        file = request.files['file']
                        filename = file.filename
                        folder_id = '128bzBNtS0X_f536Xt6m77p3mgjc8h4do'

                        # Connect to Drive API
                        service = build_drive_service()
                        file_id = upload_file(service, file, filename, folder_id)
                        link = get_file(service, file_id)

                        # Upload File Link to SQL Database
                        account = sql_get("accountId", "accounts", "email = %s", (action,), cursor)

                        test_case = (file_id, request.form.get("title"), request.form.get("date"), link, account[0][0])

                        sql_insert(connection, "forms", "(formId, title, date, link, accountId)", "(%s, %s, %s, %s, %s)", test_case, cursor)

                elif tag == "sports":  # If Sports Management
                    if action == "add":  # Adding Information
                        if request.form.get("name") == "" or request.form.get("sport") == "":  # Check if all fields are filled
                            flash("error Please fill in all the fields.")
                            return redirect(f"/manager/{tag}")

                        elif request.form.get("role") == "achievements":  # Achievement Related
                            if request.form.get("year") == "":  # Check if all fields are filled
                                flash("error Please fill in all the fields.")
                                return redirect(f"/manager/{tag}")
                            else:
                                # Try to retrieve information
                                test_case = (uuid.uuid4().hex, int(request.form.get("year")), request.form.get("name"), request.form.get("sport"))
                                used = sql_get("*", "achievements", "yachieved = %s AND achievement = %s AND sport = %s", test_case[1::], cursor)

                                # Achievement Already Has Been Posted
                                if used != []:
                                    flash("error Achievement has already been added.")
                                    return redirect(f"/manager/{tag}")
                                else:
                                    # Add To Database
                                    sql_insert(connection, "achievements", "(achievementId, yachieved, achievement, sport)", "(%s, %s, %s, %s)", test_case, cursor)
                        else:  # Roster Related
                            if request.form.get("role") == "":  # Check if all fields are filled
                                flash("error Please fill in all the fields.")
                                return redirect(f"/manager/{tag}")
                            else:
                                # Try to retrieve Information
                                test_case = (request.form.get("name"), request.form.get("sport"))
                                used = sql_get("*", "roster", "name = %s AND sport = %s", test_case, cursor)

                                # This Player Has Already Been Added
                                if used != []:
                                    flash(f"error This {request.form.get('role')} has already been added.")
                                else:
                                    # Add To Database
                                    test_case = (uuid.uuid4().hex, request.form.get("name"), request.form.get("sport"), request.form.get("role"))
                                    sql_insert(connection, "roster", "(rosterId, name, sport, role)", "(%s, %s, %s, %s)", test_case, cursor)
                    else:  # Edit Information
                        if request.form.get("name") == "" or request.form.get("sport") == "":  # Check if all fields are filled
                            flash("error Please fill in all the fields.")
                            return redirect(f"/manager/{tag}")
                        elif request.form.get("role") == "achievements":  # Achievement Related
                            if request.form.get("year") == "":  # Check if all fields are filled
                                flash("error Please fill in all the fields.")
                                return redirect(f"/manager/{tag}")
                            else:
                                sql_update(connection, "achievements", "yachieved = %s, achievement = %s, sport = %s", "achievementId = %s", (int(request.form.get("year")), request.form.get("name"), request.form.get("sport"), action), cursor)
                        else:  # Roster Related
                            if request.form.get("role") == "":  # Check if all fields are filled
                                flash("error Please fill in all the fields.")
                                return redirect(f"/manager/{tag}")
                            else:
                                sql_update(connection, "roster", "name = %s, sport = %s, role = %s", "rosterId = %s", (str(request.form.get("name")), request.form.get("sport"), request.form.get("role"), action), cursor)
                elif tag == "news":  # If Editing News and Events Information
                    if action == "add":  # Adding Information
                        if request.form.get("title") == "" or request.form.get("desc") == "":  # Check if all fields are filled
                            flash("error Please fill in all the fields.")
                            return redirect(f"/manager/{tag}")
                        elif request.form.get("message") == "event":  # Events Related
                            if request.form.get("sdate") == "" or request.form.get("edate") == "":  # Check if all fields are filled
                                flash("error Please fill in all the fields.")
                                return redirect(f"/manager/{tag}")
                            elif datetime.strptime(request.form.get("sdate"), "%Y-%m-%dT%H:%M") > datetime.strptime(request.form.get("edate"), "%Y-%m-%dT%H:%M"):
                                flash("error Please make sure that the end date is after the start date.")
                                return redirect(f"/manager/{tag}")
                            else:
                                # Connect to Calendar API
                                service = build_cal_service()

                                # Insert Event
                                event = build_event(request.form.get("title"), request.form.get("desc"), request.form.get("sdate"), request.form.get("edate"))
                                create_event(service, event)
                        elif request.form.get("message") == "info":  # General Info Related
                            # Try to retrieve information
                            test_case = (uuid.uuid4().hex, request.form.get("title"), request.form.get("desc"))
                            used = sql_get("*", "information", "title = %s AND description = %s", test_case[1::], cursor)

                            # Information Has Already Been Posted
                            if used != []:
                                flash("error Information has already been added.")    
                                return redirect(f"/manager/{tag}")

                            # Add To Database
                            sql_insert(connection, "information", "(infoId, title, description)", "(%s, %s, %s)", test_case, cursor)
                        elif request.form.get("message") == "high":  # Highlight Related
                            if request.form.get("link") == "":
                                flash("error Please fill in all the fields.")
                                return redirect(f"/manager/{tag}")
                            else:
                                # Try to retrieve information
                                test_case = (uuid.uuid4().hex, request.form.get("title"), request.form.get("desc"), request.form.get("link"))
                                used = sql_get("*", "highlights", "title = %s AND description = %s AND link = %s", test_case[1::], cursor)

                                # Highlight Has Already Been Posted
                                if used != []:
                                    flash("error Highlight has already been added.")    
                                    return redirect(f"/manager/{tag}")  

                                # Add To Database
                                sql_insert(connection, "highlights", "(highlightId, title, description, link)", "(%s, %s, %s, %s)", test_case, cursor)
                    else:  # Edit Information
                        if request.form.get("title") == "" or request.form.get("desc") == "":  # Check if all fields are filled
                            flash("error Please fill in all the fields.")
                            return redirect(f"/manager/{tag}")
                        elif request.form.get("message") == "event":  # Event Related
                            if request.form.get("sdate") == "" or request.form.get("edate") == "":  # Check if all fields are filled
                                flash("error Please fill in all the fields.")
                                return redirect(f"/manager/{tag}")
                            else:
                                # Connect to Calendar API
                                service = build_cal_service()
                                # Update Event
                                update_event(service, action, [request.form.get("title"), request.form.get("desc"), request.form.get("sdate"), request.form.get("edate")])
                        elif request.form.get("message") == "info":  # General Info Related
                            sql_update(connection, "information", "title = %s, description = %s", "infoId = %s", (request.form.get("title"), request.form.get("desc"), action), cursor)
                        elif request.form.get("message") == "high":  # Highlight Related
                            if request.form.get("link") == "":  # Check if all fields are filled
                                flash("error Please fill in all the fields.")
                                return redirect(f"/manager/{tag}")
                            else:
                                sql_update(connection, "highlights", "title = %s, description = %s, link = %s", "highlightId = %s", (request.form.get("title"), request.form.get("desc"), request.form.get("link"), action), cursor)
                flash("success Your request was successful")
            except:
                flash("error An error occured while making the change")
            finally:
                sql_close(connection, cursor)
            return redirect(f"/manager/{tag}")
        else:
            # Connect to MySQL Server
            connection = sql_connect(app.config['SQL_KEY'])
            cursor = connection.cursor(dictionary=True)
            if tag == "users":  # Users Related
                if request.args.get("email") != None:  # Specific User
                    user = TABLE[request.args.get("type")](request.args.get("email"), cursor)
                    forms = sql_get("*", "forms", "accountId = %s", (user.getId(),), cursor)              
                    return render_template("manager.html", user=user, forms=forms)
                else:
                    # All Users
                    accounts = sql_get("*", "accounts", "confirmed = %s and type != %s", ("1", "admin"), cursor)

                    accounts = sorted(accounts, key=lambda x: x["type"])

                    students = []
                    coaches = []
                    parents = []

                    for account in accounts:
                        if account['type'] == 'student':
                            students.append(account)
                        elif account['type'] == 'coach':
                            coaches.append(account)
                        elif account['type'] == 'parent':
                            parents.append(account)

                    return render_template("manager.html", accounts=accounts, students=students, parents=parents, coaches=coaches)
            elif tag == "sports":
                # Roster/Sport Related
                players = sql_get("*", "roster", "role = %s", ("player",), cursor)
                players = sorted(players, key=lambda x: x["sport"])

                coaches = sql_get("*", "roster", "role = %s", ("coach",), cursor)
                coaches = sorted(coaches, key=lambda x: x["sport"])

                sql_select_Query = "SELECT * FROM achievements ORDER BY yachieved DESC"

                cursor.execute(sql_select_Query)
                achievements = cursor.fetchall()
                return render_template("manager.html", players=players, coaches=coaches, achievements=achievements)
            elif tag == "news":
                # News and Events Related
                service = build_cal_service()
                events = get_events(service, datetime(2023, 8, 31, 0, 0, 0))

                sql_select_Query = "SELECT * FROM information ORDER BY dateposted DESC"
                cursor.execute(sql_select_Query)
                info = cursor.fetchall()

                sql_select_Query = "SELECT * FROM highlights ORDER BY dateposted DESC"
                cursor.execute(sql_select_Query)
                highlights = cursor.fetchall()                  

                return render_template("manager.html", events=events, info=info, highlights=highlights)
    else:
        flash("error You do not have access to that webpage.")
        return redirect("/")


# Home Page
@app.route('/', methods=['POST', 'GET'])
def index():
    # Get Current Date
    current = datetime.now()
    month = calendar.month_name[current.month]
    try:
        # Connect to Database
        connection = sql_connect(app.config['SQL_KEY'])
        cursor = connection.cursor(dictionary=True)  # Set to Dictionary Mode

        # Get Highlights
        sql_select_Query = "SELECT * FROM highlights ORDER BY dateposted DESC"
        cursor.execute(sql_select_Query)
        highlights = cursor.fetchall()

        # Connect to Calendar API
        service = build_cal_service()
        events = get_events(service, datetime.combine(date.today()  + timedelta(days=1), datetime.min.time()))

        # Display Most Recent Four
        if len(highlights) > 4:
            highlights = highlights[:4]

        return render_template('index.html', month=month, day=current.day, year=current.year, highlights=highlights, events=events)
    finally:
        sql_close(connection, cursor)


# Delete Data From Database
@app.route('/delete/<page>/<id>/<db>/')
def delete(page, id, db):
    if session.get("type") == "admin":  # Must Have Admin Permissions
        try:
            # Connect to Database
            connection = sql_connect(app.config['SQL_KEY'])
            cursor = connection.cursor()

            # Managing Users
            if page == "users":
                sql_rmv(connection, "forms", "formId = %s", (id,), cursor)

                # Connect to Drive API
                service = build_drive_service()
                service.files().delete(fileId=id).execute()
            # Managing Teams
            elif page == "sports":
                if db == "roster":
                    sql_rmv(connection, "roster", "rosterId = %s", (id,), cursor)
                elif db == "achievements":
                    sql_rmv(connection, "achievements", "achievementId = %s", (id,), cursor)

            # Managing News
            elif page == "news":
                if db == "events":
                    service = build_cal_service()
                    delete_event(service, id)
                elif db == "information":
                    sql_rmv(connection, "information", "infoId = %s", (id,), cursor)
                elif db == "highlights":
                    sql_rmv(connection, "highlights", "highlightId = %s", (id,), cursor)
            flash("success Your request was successful")
            return redirect(f"/manager/{page}")
        except:
            flash("error An error occured while carrying out your request")
            return redirect(f"/manager/{page}")
        finally:
            sql_close(connection, cursor)
    else:
        return redirect('/')


# Access Personal Profile
@app.route('/profile')
def profile():
    if session.get("type") != "admin" and session.get("type") != None:  # Must Be Signed In and Can't Be In Admin Account
        try:
            # Connect to Database
            connection = sql_connect(app.config['SQL_KEY'])
            cursor = connection.cursor(dictionary=True)
            forms = sql_get("*", "forms", "accountId = %s", (session["user_id"],), cursor)              
        finally:
            sql_close(connection, cursor)
        return render_template('profile.html', header="Profile", forms=forms)
    else:
        flash("error Please signin to access that webpage")
        return redirect("/")


# Account Settings
@app.route("/settings", methods=['POST', 'GET'])
def settings():
    if session.get("type") != None:  # Must Be Signed In
        return render_template('settings.html')
    else:
        flash("error Please signin to access that webpage")
        return redirect("/")


# Edit Settings    
@app.route("/settings/edit/<area>", methods=['POST', 'GET'])
def edit_settings(area):
    # Dictionary that relates account type to database
    key = {"student": "students", "parent": "parents", "coach":"coaches", "admin": "accounts"}

    if session.get("type") != None:  # Must Be Signed In
        try:
            # Connect to Database
            connection = sql_connect(app.config['SQL_KEY'])
            cursor = connection.cursor(dictionary=True)  # Set to Dictionary Mode
            email = sql_get("email", "accounts", "accountId = %s", (session.get("user_id"),), cursor)

            if request.method == "POST":  # Form submitted
                if area == "name":  # Manage Name
                    sql_update(connection, key[session.get("type")], "fname = %s, mname = %s, lname = %s ", "accountId = %s", (request.form.get("fname"), request.form.get("mname"), request.form.get("lname"), session.get("user_id")), cursor)
                    name = sql_get("fname", key[session.get("type")], "accountId = %s", (session.get("user_id"),), cursor)
                    session["name"] = name[0]["fname"]
                elif area == "password":  # Manage Password
                    password = sql_get("password", "accounts", "accountId = %s", (session.get("user_id"),), cursor)
                    if not check_password_hash(password[0]["password"], request.form.get("oldpass")):
                        flash("error Password incorrect")
                    elif not (request.form.get("newpass") == request.form.get("confpass")):
                        flash("error Passwords do not match")
                    else:
                        sql_update(connection, "accounts", "password = %s", "accountId = %s", (generate_password_hash(request.form.get('newpass')), session.get("user_id")), cursor)
                else:  # Manage Any Other Fields
                    sql_update(connection, key[session.get("type")], f"{area}= %s", "accountId = %s", (request.form.get(f"{area}"), session.get("user_id")), cursor)
                return redirect(f"/settings/edit/{area}")
            else:
                # Retrieve Data to Display
                info = sql_get("*", key[session.get("type")], "accountId = %s", (session.get("user_id"),), cursor)
                flash("success Your request was successful")
                return render_template('edit_settings.html', area=area, info=info[0], email=email[0]["email"])
        except:
            flash("error An error occured during the process")
            return redirect(f"/settings/edit/{area}")
        finally:
            sql_close(connection, cursor)
    else:
        flash("error Please signin to access that webpage")
        return redirect("/")

# Catch All (If none of the other functions are called this one gets everything)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    flash("error The page you are looking for does not exist")
    return redirect("/")

# Run App
if __name__ == "__main__":
    app.run(port=5000, debug=True)

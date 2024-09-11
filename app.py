from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from database import engine
from sqlalchemy import text
from database import fetch_software_data_by_id, fetch_all_requests, move_to_notapproved, fetch_request_by_id, insert_software, fetch_all_notapproved
from flaskmail import init_mail, mail
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'KAjgZ8y73u'

#initialize flaskmail.py app 
init_mail(app)

def load_software_from_db(filter_status=None):
    with engine.connect() as connection:
        if filter_status == 'approved':
            query = text("SELECT * FROM software WHERE Approved = 'Yes';")
        elif filter_status == 'not_approved':
            query = text("SELECT * FROM software WHERE Approved = 'No';")
        else:
            query = text("SELECT * FROM software;")
        
        result = connection.execute(query).mappings()
        rows = [dict(row) for row in result]
        return rows

@app.route("/")
def index():
    software = load_software_from_db()
    recent_software = sorted(software, key=lambda x: x['id'], reverse=True)[:5]
    return render_template('index.html', software_list=recent_software)

@app.route("/adminrejected")
def adminrejected():
    rejected = fetch_all_notapproved()
    return render_template ('adminrejected.html', rejected=rejected)

@app.route("/search")
def search():
    query = request.args.get('query', '')
    software_list = []
    if query:
        all_software = load_software_from_db()
        software_list = [s for s in all_software if query.lower() in s['Software_Name'].lower()]
    return render_template('searchresults.html', software_list=software_list, query=query)

@app.route("/allsoftware")
def all_software():
    filter_status = request.args.get('filter', None)  # Get filter parameter
    software_list = load_software_from_db(filter_status)
    return render_template('allsoftware.html', software_list=software_list)

@app.route("/adminrequests")
def userreq_page():
    return render_template('adminrequests.html')

@app.route("/request")
def request_page():
    return render_template('request.html')

@app.route("/admin")
def admin_page():
    return render_template('admin.html')

@app.route("/application/<id>")
def show_appinfo(id):
    appinfo = fetch_software_data_by_id(id)
    if not appinfo:
        return "Not Found", 404
    return render_template('application.html', appinfo=appinfo[0])

# Route for submitting software request
@app.route("/submit", methods=["POST"])
def submit_form():
    # Get form data
    software_name = request.form.get('softwareName')
    license_type = request.form.get('licenseType')
    price = request.form.get('price')
    comments = request.form.get('comments')
    approved = 'Yes' if request.form.get('approved') else 'No'  # Set to 'Yes' if checkbox is checked, otherwise 'No'

    # Insert data into database
    try:
        with engine.connect() as connection:
            query = text("""
                INSERT INTO software (Software_Name, License_Type, Price, Approved, Comments)
                VALUES (:software_name, :license_type, :price, :approved, :comments)
            """)
            connection.execute(query, {
                "software_name": software_name,
                "license_type": license_type,
                "price": float(price),
                "approved": approved,
                "comments": comments
            })
            connection.commit()  # Explicit commit
        
        return render_template('submit.html', message="Submission successful!")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template('submit.html', message="An error occurred during submission.")

# Combined GET and POST route for user request
@app.route('/submit-request', methods=['GET', 'POST'])
def submit_request():
    if request.method == 'POST':
        username = request.form['username']
        application = request.form['application']
        price = request.form['price']
        license_type = request.form['license_type']
        approved_by_manager = request.form['approved_by_manager']
        link = request.form['link']
        comments = request.form['comments']

        # Insert data into the request table
        try:
            with engine.connect() as connection:
                query = text("""
                    INSERT INTO requests (username, application, price, license_type, approved_by_manager, link, comments)
                    VALUES (:username, :application, :price, :license_type, :approved_by_manager, :link, :comments)
                """)
                connection.execute(query, {
                    "username": username,
                    "application": application,
                    "price": float(price),
                    "license_type": license_type,
                    "approved_by_manager": approved_by_manager,  # 'yes' or 'no'
                    "link": link,
                    "comments": comments
                })
                connection.commit()  # Explicit commit

            # Send an email with the request details
            msg = Message(
                "New Software Request Submitted",
                recipients=["softwareregister999@gmail.com"]  # Update to actual recipient email
            )
            # Email content
            msg.body = f"""
            A new software request has been submitted:

            Username: {username}
            Application: {application}
            Price: {price}
            License Type: {license_type}
            Approved by Manager: {approved_by_manager}
            Link: {link}
            Comments: {comments}
            """
            msg.html = f"""
            <h3>New Software Request Submitted</h3>
            <p><strong>Username:</strong> {username}</p>
            <p><strong>Application:</strong> {application}</p>
            <p><strong>Price:</strong> {price}</p>
            <p><strong>License Type:</strong> {license_type}</p>
            <p><strong>Approved by Manager:</strong> {approved_by_manager}</p>
            <p><strong>Link:</strong> <a href="http://{link}">{link}</a></p>
            <p><strong>Comments:</strong> {comments}</p>
            """
            
            # Send the email
            mail.send(msg)

            # Render a success message
            return render_template('submit-request.html', message="Submission successful! An email has been sent.")
        
        except Exception as e:
            # Handle any database or email errors here
            return render_template('submit-request.html', message=f"An error occurred: {str(e)}")

    # GET request to show the form
    return render_template('submit-request.html')


#this is to get requests table data for user requests 

@app.route('/admin/requests')
def adminrequests():
    try:
        with engine.connect() as connection:
            query = text("SELECT * FROM requests;")
            result = connection.execute(query).mappings()
            requests = [dict(row) for row in result]
            print("Requests data type:", type(requests))  # Debug statement
            print("Requests data:", requests)  # Debug statement
        return render_template('adminrequests.html', requests=requests)
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while fetching requests.", 500




@app.route('/approve_request/<int:id>', methods=['POST'])
def approve_request(id):
    try:
        # You need to fetch request details first
        request_data = fetch_request_by_id(id)
        if request_data:
            request_data = request_data[0]
            # Move the request to the software table
            insert_software(
                software_name=request_data['application'],
                license_type=request_data['license_type'],
                price=request_data['price'],
                approved='Yes',
                comments=request_data['comments']
            )
            # Delete from requests
            with engine.connect() as connection:
                delete_query = text("DELETE FROM requests WHERE id = :id")
                connection.execute(delete_query, {"id": id})
                connection.commit()

                # Send approval email
            msg = Message(
                subject="Request Approved",
                recipients=["stanwisniew@gmail.com"]
            )
            msg.body = f"""
            A request has been approved:

            Username: {request_data['username']}
            Application: {request_data['application']}
            Price: {request_data['price']}
            License Type: {request_data['license_type']}
            Comments: {request_data['comments']}
            """
            msg.html = f"""
            <h3>Request Approved</h3>
            <p><strong>Username:</strong> {request_data['username']}</p>
            <p><strong>Application:</strong> {request_data['application']}</p>
            <p><strong>Price:</strong> {request_data['price']}</p>
            <p><strong>License Type:</strong> {request_data['license_type']}</p>
            <p><strong>Comments:</strong> {request_data['comments']}</p>
            """

            mail.send(msg)

            print("Disapproval email sent successfully!")
        else:
            print("No request found for disapproval.")

        flash('Request has been approved successfully!', 'success')
        return redirect(url_for('adminrequests'))
    except Exception as e:
        print(f"An error occurred: {e}")
        flash('An error occurred while processing the request.', 'danger')
        return "An error occurred while processing the request.", 500

@app.route('/disapprove_request/<int:id>', methods=['POST'])
def disapprove_request(id):
    reason = request.form['reason']
    application = request.form['application']
    try:
        move_to_notapproved(id, reason)

  # Send disapproval email
        msg = Message(
            subject="Request Disapproved",
            recipients=["stanwisniew@gmail.com"]
        )
        msg.body = f"""
        A request has been disapproved:

        Application: {application}
        Reason for Disapproval: {reason}
        """
        msg.html = f"""
        <h3>Request Disapproved</h3>
        <p><strong>Application:</strong> {application}</p>
        <p><strong>Reason for Disapproval:</strong> {reason}</p>
        """

        mail.send(msg)
        flash('Request has been rejected successfully!', 'success')
        return redirect(url_for('adminrequests'))
    except Exception as e:
        print(f"An error occurred: {e}")
        flash('An error occurred while processing the request.', 'danger')
        return "An error occurred while processing the request.", 500

#route for flask mail 


# Route to send an email

@app.route('/send_email')
def send_email():
    try:
        # Create a Message object
        msg = Message("Hello from Software Register",
                      recipients=["recipient@example.com"])  # Change recipient's email

        msg.body = "This is a test email sent from Flask-Mail in a Flask app."
        msg.html = "<b>This is a test email</b> sent from Flask-Mail in a Flask app."

        # Send the email
        mail.send(msg)
        return "Email sent successfully!"
    except Exception as e:
        return str(e)  # In case something goes wrong



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

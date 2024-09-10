from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from database import engine
from sqlalchemy import text
from database import fetch_software_data_by_id, fetch_all_requests, move_to_notapproved, fetch_request_by_id, insert_software

app = Flask(__name__)
app.secret_key = 'KAjgZ8y73u'
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

            # Render a success message
            return render_template('submit-request.html', message="Submission successful!")
        
        except Exception as e:
            # Handle any database errors here
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
        request = fetch_request_by_id(id)
        if request:
            request = request[0]
            # Move the request to the software table
            insert_software(
                software_name=request['application'],
                license_type=request['license_type'],
                price=request['price'],
                approved='Yes',
                comments=request['comments']
            )
            # Delete from requests
            with engine.connect() as connection:
                delete_query = text("DELETE FROM requests WHERE id = :id")
                connection.execute(delete_query, {"id": id})
                connection.commit()
        flash('Request has been approved successfully!', 'success')
        return redirect(url_for('adminrequests'))
    except Exception as e:
        print(f"An error occurred: {e}")
        flash('An error occurred while processing the request.', 'danger')
        return "An error occurred while processing the request.", 500

@app.route('/disapprove_request/<int:id>', methods=['POST'])
def disapprove_request(id):
    reason = request.form['reason']
    try:
        move_to_notapproved(id, reason)
        return redirect(url_for('adminrequests'))
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while processing the request.", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

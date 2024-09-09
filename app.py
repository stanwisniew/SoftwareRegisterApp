from flask import Flask, render_template, jsonify, request, redirect, url_for
from database import engine
from sqlalchemy import text
from database import fetch_software_data_by_id

app = Flask(__name__)

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
        return render_template('submit_page', message="An error occurred during submission.")


print(__name__)
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
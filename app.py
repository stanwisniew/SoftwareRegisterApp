from flask import Flask, render_template, jsonify, request, redirect, url_for
from database import engine
from sqlalchemy import text
from database import fetch_software_data_by_id

app = Flask(__name__)

def load_software_from_db():
    with engine.connect() as connection:
            # Define and execute the query
            query = text("SELECT * FROM software;")
            result = connection.execute(query).mappings()  # Use .mappings() to return as dictionaries
            rows = [dict(row) for row in result]  # Each row is already a dictionary-like object
            return rows


@app.route("/")
def hello_world():
    software = load_software_from_db()
    return render_template('index.html', software=software)

@app.route("/request")
def request_page():
    return render_template('request.html')

@app.route("/admin")
def admin_page():
    return render_template('admin.html')

@app.route("/submit")
def submit_page():
    return render_template('submit.html')

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
        
        return render_template('submit.html', message="Submission successful!")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template('submit_page', message="An error occurred during submission.")


print(__name__)
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
from flask import Flask, render_template, jsonify
from database import engine
from sqlalchemy import text

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

print(__name__)
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
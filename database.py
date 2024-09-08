import sqlalchemy
from sqlalchemy import create_engine, text

# Define the connection string to your MySQL database
connection_string = "mysql+pymysql://sql7730122:idnTnhBtif@sql7.freesqldatabase.com:3306/sql7730122"

# Create the SQLAlchemy engine
engine = create_engine(connection_string)

# Connect to the database and execute a query

def fetch_software_data():
    try:
        with engine.connect() as connection:
            # Define and execute the query
            query = text("SELECT * FROM software;")
            result = connection.execute(query).mappings()  # Use .mappings() to return as dictionaries

            # Convert the result into a list of dictionaries
            rows = [dict(row) for row in result]  # Each row is already a dictionary-like object

            return rows

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Example usage
software_data = fetch_software_data()
print(software_data)
import sqlalchemy
from sqlalchemy import create_engine, text

# Define the connection string to your MySQL database
connection_string = "mysql+pymysql://sql7730122:idnTnhBtif@sql7.freesqldatabase.com:3306/sql7730122"

# Create the SQLAlchemy engine
engine = create_engine(connection_string)

def fetch_all_software_data():
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

def fetch_software_data_by_id(id):
    try:
        with engine.connect() as connection:
            # Define and execute the query with parameter binding
            query = text("SELECT * FROM software WHERE id = :val")
            result = connection.execute(query, {"val": id}).mappings()  # Use parameter binding correctly

            # Convert result to a list of dictionaries
            rows = [dict(row) for row in result]
            return rows
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Example usage
all_software_data = fetch_all_software_data()
print("All software data:", all_software_data)

software_data = fetch_software_data_by_id(1)  # Replace 1 with the desired ID
print("Software data by ID:", software_data)

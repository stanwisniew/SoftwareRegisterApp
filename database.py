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


#new stuff for other databases

def fetch_all_requests():
    try:
        with engine.connect() as connection:
            query = text("SELECT * FROM requests;")
            result = connection.execute(query).mappings()
            rows = [dict(row) for row in result]
            return rows
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def fetch_request_by_id(request_id):
    try:
        with engine.connect() as connection:
            query = text("SELECT * FROM requests WHERE id = :val")
            result = connection.execute(query, {"val": request_id}).mappings()
            rows = [dict(row) for row in result]
            return rows
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def insert_software(software_name, license_type, price, approved, comments):
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
            connection.commit()
    except Exception as e:
        print(f"An error occurred: {e}")

def move_to_notapproved(request_id, reason):
    try:
        with engine.connect() as connection:
            # Fetch the request data
            query = text("SELECT * FROM requests WHERE id = :val")
            result = connection.execute(query, {"val": request_id}).mappings()
            request_data = [dict(row) for row in result]
            if request_data:
                request_data = request_data[0]
                # Insert into notapproved
                insert_query = text("""
                    INSERT INTO notapproved (application, comment)
                    VALUES (:application, :comment)
                """)
                connection.execute(insert_query, {
                    "application": request_data["application"],
                    "comment": reason
                })
                # Delete from request
                delete_query = text("DELETE FROM requests WHERE id = :val")
                connection.execute(delete_query, {"val": request_id})
                connection.commit()
    except Exception as e:
        print(f"An error occurred: {e}")

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

connection_string = "mysql+pymysql://sql7730122:idnTnhBtif@sql7.freesqldatabase.com:3306/sql7730122"
engine = create_engine(connection_string, echo=True)
try:
    with engine.connect() as connection:
        # Execute the SQL command to create a table
        connection.execute(text("INSERT INTO software (Software_Name, License_Type, Price, Approved, Comments) VALUES ('Google Earth Pro', 'free', 40, 'Yes', 'free license')"))
        connection.commit()  # Explicit commit

    print("Table created successfully.")
except SQLAlchemyError as e:
    print(f"An error occurred: {e}")

# Import the Database class from the pony.orm library to create a database connection object.
from pony.orm import Database
# Import the db_session decorator from the pony.orm library to manage database sessions.
from pony.orm import db_session

# Database singleton
db = Database()

# Create an alias for the db_session decorator to provide a convenient way to manage database sessions.
session = db_session
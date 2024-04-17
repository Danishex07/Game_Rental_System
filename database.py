import random
import sqlite3
from datetime import datetime
import re


# Null value check
def has_none_values(parameter):
    return len(parameter) == 0

# Customer Id length check
def in_valid_customer_id(parameter):
    return len(str(parameter)) != 4


# Checking the rental data is greater than return date or not, if true its invalid and vice versa of it.
def is_Invalid_dates(rental_date, return_date):
    if has_none_values(return_date):
        return False
    rental_date_obj = datetime.strptime(rental_date, '%d-%m-%Y')
    return_date_obj = datetime.strptime(return_date, '%d-%m-%Y')
    return rental_date_obj > return_date_obj

# Checking the dates and throwing exception of valueerror if given format is incorrect.
def check_date_format(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
        date_str = date_obj.strftime('%d-%m-%Y')
        return date_str
    except ValueError:
        return None


def correct_date_format(actual_date):
    date_valid = True
    correction = False

    result = check_date_format(actual_date)

    if result is None:
        # Regular expression to remove all the non digit values and replacing with the - character
        actual_date = re.sub(r'\D', '-', actual_date)
        result = check_date_format(actual_date)
        if result is None:
            date_valid = False
            return date_valid, actual_date, correction
        else:
            correction = True
            return date_valid, actual_date, correction
    return date_valid, actual_date, correction


def data_cleaning(record, index):
    '''
    Data cleaning function get the individual records from the text file and their index to do multiple function check upon them.
    '''
    record = record.split(',')
    game_id, rental_date, return_date, customer_id = record
    message = ''
    status = False

    # Checking the null value of the given paramter
    if (has_none_values(game_id)):
        message = f"Row={index} has Game Id as Null"
        status = True
        return message, status, record

    if (has_none_values(rental_date)):
        message = f"Row={index} has Rental Date as Null"
        status = True
        return message, status, record

    if (has_none_values(customer_id)):
        message = f"Row={index} has Customer Id as Null"
        status = True
        return message, status, record
    
    # Checking the customer id value in the range of 1000-9999
    if (in_valid_customer_id(customer_id)):
        message = f"Row={index} has invalid Customer Id of {customer_id} not in range (1000-9999)"
        status = True
        return message, status, record

    # Checking the rental date and trying to format the dates correctly if the given date format is not in d-m-y.
    isValid_rental, date_rental, correction = correct_date_format(rental_date)

    if (not isValid_rental):
        message = f"Row={index} has Rental Date is invalid, and could not be corrected"
        status = True
        return message, status, record
    else:
        if (correction):
            message = f"Row={index} has Rental Date:  {rental_date}  invalid, but formated correctly to {date_rental}"
        rental_date = date_rental
        record[1] = date_rental

    # Checking the return date and trying to format the dates correctly if the given date format is not in d-m-y.
    isValid_return, date_return, correction = correct_date_format(return_date)

    if (not has_none_values(return_date) and not isValid_return):
        message = f"Row={index} has Return Date is invalid, and could not be corrected"
        status = True
        return message, status, record
    else:
        if (correction):
            if (len(message) > 0):
                message = message + '\n'
            message = message + f"Row={index} has Return Date:  {return_date}  invalid, but formated correctly to  {date_return}"
        return_date = date_return
        record[2] = date_return

    if (is_Invalid_dates(rental_date, return_date)):
        message = f"Row={index} has invalid dates, Rental Date is more than Return Date"
        status = True
        return message, status, record
    
    if (has_none_values(return_date)):
        record[2] = None

    return message, status, record



def get_data_from_txt_files():
    games_tuple_list = []
    rental_tuple_list = []
    suggestion_tuple_list = []
    error_list = []
    
    # Reading the game text file and getting the data to add them into a tuple list to proceed further.
    try:
        with open('./data/txt/game.txt', 'r') as file:
            next(file)
            lines = file.read().splitlines()
            for line in lines:
                games_tuple_list.append(tuple(line.split(',')))
    except FileNotFoundError:
        print("Game File not found. Please check the file path or name.")
     
    # Data cleaning before giving the data for the database initialization.
    try:
        with open('./data/txt/rental.txt', 'r') as file:
            next(file)
            lines = file.read().splitlines()
            index = 1
            for line in lines:
                # code is message , status is current operation status and data contains the formated record.
                code, status, data = data_cleaning(line,index)
                if (status):
                    code = code.split('\n')
                    error_list = error_list + code
                else:
                    if (len(code) > 0):
                        code = code.split('\n')
                        error_list = error_list + code
                    rental_tuple_list.append(tuple((data) + [random.randint(0, 15)]))
                index = index + 1
    except FileNotFoundError:
        print("Rental File not found. Please check the file path or name.")
    
    try:
        with open('./data/txt/suggestions.txt', 'r') as file:
            next(file)
            lines = file.read().splitlines()
            for line in lines:
                suggestion_tuple_list.append(tuple(line.split(',')))
    except FileNotFoundError:
        print("Suggestion File not found. Please check the file path or name.")
     
    return games_tuple_list, rental_tuple_list, suggestion_tuple_list, error_list
     


def database_creation(games_tuple,rental_tuple, suggestion_tuple):
    '''
    This function is called at the start of the program and populate the rental, game and suggestion files to table with the same name.
    
    Keyword Arguments:
    games_tuple : This will contains the list of the games txt file data as a list of tuples.
    rental_tuple: This will contains the list of the rental txt file data as a list of tuples.
    suggestion_tuple: This will contains the list of the suggestion txt file data as a list of tuples.
    '''
    
    try:
        connection = sqlite3.connect('GameRental.db')
        cursor = connection.cursor()

        cursor.execute("DROP TABLE IF EXISTS games")

        cursor.execute("CREATE TABLE games \
                        (id INTEGER NOT NULL, title Text, platform Text, genre Text, purchase_price Real, purchase_date Text)")

        cursor.executemany("INSERT INTO games (id, title, platform, genre, purchase_price, purchase_date) \
                                VALUES (?,?,?,?,?,?)", games_tuple)
        connection.commit()

        cursor.execute("DROP TABLE IF EXISTS games_suggestion")

        cursor.execute("CREATE TABLE games_suggestion \
                       (id INTEGER NOT NULL, title Text, platform Text, genre Text, purchase_price Real, purchase_date Text)")

        cursor.executemany("INSERT INTO games_suggestion (id, title, platform, genre, purchase_price, purchase_date) \
                                VALUES (?,?,?,?,?,?)",suggestion_tuple)
        connection.commit()


        cursor.execute("DROP TABLE IF EXISTS rental")

        cursor.execute("CREATE TABLE rental \
                       (game_id INTEGER NOT NULL, rental_date Text NOT NULL, return_date Text, customer_id CHARACTER(4), \
                        unavailability INTEGER DEFAULT 0, FOREIGN KEY (game_id) REFERENCES games (id))")

        cursor.executemany("INSERT INTO rental (game_id, rental_date, return_date, customer_id,unavailability)\
                                 VALUES (?,?,?,?,?)",rental_tuple)
        connection.commit()
    except sqlite3.Error as e:
        # Handle SQLite errors
        print(f"SQLite error: {e}")
        record = None
    finally:
        # Closing Connection
        if connection:
            connection.close()

# Below function are the basic operation done to the databases like inserting, updating, or fetching the data from the database.

def update_db(query, parameter):
    try:
        connection = sqlite3.connect('GameRental.db')
        cursor = connection.cursor()
        cursor.execute(query, (parameter,))
        records = cursor.fetchall()
        connection.commit()
    except sqlite3.Error as e:
        # Handle SQLite errors
        print(f"SQLite error: {e}")
        record = None
    finally:
        # Closing Connection
        if connection:
            connection.close()
            


def insert_tuple_into_db(query, parameter):
    try:
        connection = sqlite3.connect('GameRental.db')
        cursor = connection.cursor()
        cursor.execute(query, parameter)
        records = cursor.fetchall()
        connection.commit()
    except sqlite3.Error as e:
        # Handle SQLite errors
        print(f"SQLite error: {e}")
        record = None
    finally:
        # Closing Connection
        if connection:
            connection.close()


def read_from_db_fetch_all(query, parameter):
    try:
        connection = sqlite3.connect('GameRental.db')
        cursor = connection.cursor()
        cursor.execute(query, (parameter,))
        records = cursor.fetchall()
        connection.commit()
    except sqlite3.Error as e:
        # Handle SQLite errors
        print(f"SQLite error: {e}")
        record = None
    finally:
        # Closing Connection
        if connection:
            connection.close()

    return records


def select_from_db_fetch_all(query):
    try:
        connection = sqlite3.connect('GameRental.db')
        cursor = connection.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        connection.commit()
    except sqlite3.Error as e:
        # Handle SQLite errors
        print(f"SQLite error: {e}")
        record = None
    finally:
        # Closing Connection
        if connection:
            connection.close()

    return records


def read_from_db_fetch_one(query, parameter):
    
    # I've found the select statement with count() to be slow on a very large DB.
    # Moreover, using fetch all() can be very memory-intensive.
    try:
        connection = sqlite3.connect('GameRental.db')
        cursor = connection.cursor()
        cursor.execute(query, (parameter,))

        record = cursor.fetchone()[0]

        connection.commit()
    except sqlite3.Error as e:
        # Handle SQLite errors
        print(f"SQLite error: {e}")
        record = None
    finally:
        # Closing Connection
        if connection:
            connection.close()

    return record

# Testing Environment

def test_get_data_from_txt_files():
    status = True
    try:
        # Test if data loading functions work correctly
        games_tuple, rental_tuple, suggestion_tuple,error_list = get_data_from_txt_files()

        # Add assertions to check if the tables and data are returned as expected
        assert len(games_tuple) > 0
        assert len(rental_tuple) > 0
        assert len(suggestion_tuple) > 0

        print("Data loading from text files test passed!")
    except AssertionError as e:
        status = False
        print(f"Data loading from text files  test failed: {e}")
    return status


def test_database_creation():
    status = True
    try:
        # Test if the database creation functions work correctly
        games_tuple, rental_tuple, suggestion_tuple,error_list = get_data_from_txt_files()

        database_creation(games_tuple, rental_tuple, suggestion_tuple)

        # Add assertions to check if the tables and data are created as expected

        games_data = select_from_db_fetch_all("SELECT * FROM games")
        games_rental = select_from_db_fetch_all("SELECT * FROM rental")
        assert len(games_data) > 0
        assert len(games_rental) > 0

        print("Database creation test passed!")
    except AssertionError as e:
        status = False
        print(f"Database creation test failed: {e}")
    return status


def test_read_from_db_fetch_one():
    status = True
    try:
        # Insert test data
        insert_tuple_into_db("INSERT INTO games (id, title, platform, genre, purchase_price, purchase_date) VALUES (?,?,?,?,?,?)",
                             (1001, "Test Game number 1", "Xbox", "Action", 39.99, "2023-11-11"))

        # Fetch the inserted record
        result = read_from_db_fetch_one("SELECT title FROM games WHERE id=?", 1001)

        # Add assertions to check if the data is fetched correctly
        assert result == "Test Game number 1"
        print("read_from_db_fetch_one test passed!")
        return status
    except AssertionError as e:
        status = False
        print(f"read_from_db_fetch_one test failed: {e}")
        return status
    except Exception as e:
        status = False
        print(f"An unexpected error occurred during testing: {e}")
        return status

def test_update_and_insert_db():
    status = True
    try:
        # Insert test data
        insert_tuple_into_db("INSERT INTO games (id, title, platform, genre, purchase_price, purchase_date) VALUES (?,?,?,?,?,?)",
                             (1002, "Test Game number 1", "PC", "Action", 59.99, "2023-09-10"))

        # Update the inserted record
        update_db("UPDATE games SET purchase_price = purchase_price + 10  WHERE id=?", 1002)

        # Fetch the updated record
        result = read_from_db_fetch_one("SELECT purchase_price FROM games WHERE id=?", 1002)

        # Rounding the price due to float value
        result = round(result, 2)

        # Add assertions to check if the data is updated correctly
        assert result == 69.99

        print("update_db test passed!")
        return status
    except AssertionError as e:
        status = False
        print(f"update_db test failed: {e}")
        return status
    except Exception as e:
        status = False
        print(f"An unexpected error occurred during testing: {e}")
        return status

def database_initialization():
    games_tuple_list, rental_tuple_list, suggestion_tuple_list, error_list  = get_data_from_txt_files()
    database_creation(games_tuple_list, rental_tuple_list, suggestion_tuple_list)
    return error_list

if __name__ == '__main__':
    if(test_get_data_from_txt_files()):
        if(test_database_creation()):
            if(test_read_from_db_fetch_one()):
                if(test_update_and_insert_db()):
                    print('All Test Passed')






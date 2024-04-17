from database import read_from_db_fetch_one, insert_tuple_into_db
from datetime import datetime

def returning_game_standalone(game_id):
    '''
    Returning  the games based upon game id
    '''
    
    # Checking whether the game is rented out initially or not for return and whether its available in the database or not.
    query = "SELECT COUNT(*) FROM games WHERE id = ?"
    records_count = read_from_db_fetch_one(query,game_id)

    if (records_count > 0):
        query = "SELECT COUNT(*) FROM rental WHERE game_id = ? and return_date is NULL"
        records_count = read_from_db_fetch_one(query, game_id)

        # Getting the record count for the game id, so to return it and giving the return date as of today.
        if (records_count > 0):
            current_datetime = datetime.now()
            current_date = current_datetime.strftime('%d-%m-%Y')

            query = "UPDATE rental SET return_date = ? WHERE game_id = ?"
            parameter = (current_date, game_id,);
            insert_tuple_into_db(query, parameter)

            return(f'Successfully returned the game of id number {game_id}', 'success')
        else:
            return('Game is already available in the database', 'error')

    else:
        return(f'Game Id number {game_id} not found in the db', 'error')



# Testing Environment

def test_returning_game_standalone():

    # Simulating the game_id input
    status = True
    try:
        game_id = 1     # Game Id is already available in the databse but checking the functionality
        # Call the function
        result, status = returning_game_standalone(game_id)

        # Check if the returned values match the expected values
        expected_result = 'Game is already available in the database'
        assert result == expected_result


        game_id = 100000    # Game Id is not in the databse but checking the functionality
        result, status = returning_game_standalone(game_id)
        expected_result = f'Game Id number {game_id} not found in the database'
        assert result == expected_result

        print("Returning Games with Id Tests are working properly!")
        return status
    except Exception as e:
        print(f"Test failed: {e}")
        status = False
        return status

# Run the test
if __name__ == '__main__':
    if(test_returning_game_standalone()):
        print('All Test Passed')
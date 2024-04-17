from subscriptionManager import *
from database import read_from_db_fetch_one, update_db,insert_tuple_into_db
from datetime import datetime
import random

def rent_game_and_update_db(game_id, customer_id):
    # Get the current date and time
    current_datetime = datetime.now()
    # Format the date as DD-MM-YYYY
    current_date = current_datetime.strftime('%d-%m-%Y')
    rental_record = (game_id, current_date, None, customer_id)
    query = "INSERT INTO rental (game_id, rental_date, return_date, customer_id) VALUES (?,?,?,?)"
    insert_tuple_into_db(query, rental_record)


def check_game_availability(game_id):
    # Checking whether the game is avilable or it is rented out earlier.
    query = "SELECT COUNT(*) FROM rental WHERE game_id = ? and return_date is NULL"

    record = read_from_db_fetch_one(query, game_id)

    return True if record == 0 else False


def get_customer_rental_count(customer_id):
    # Checking the customer rental count based upon the subscription type, the person have.
    
    query = "SELECT COUNT(*) FROM rental WHERE customer_id = ? and return_date is NULL"
    record = read_from_db_fetch_one(query, customer_id)
    return record


def update_rent_unavailability(game_id):
    # Updating the rent unavailability count when game is asked for rent but already rented out.
    query = f"UPDATE rental SET unavailability = unavailability + 1 WHERE game_id = ? and return_date is NULL"
    update_db(query, game_id)



def rent_game_standalone( customer_id, game_id):
    '''
    Renting the games based upon customer id and game id
    '''
    
    if(len(customer_id) != 4 ):
         return('InValid Customer Id,should be in the range 1000-9999', 'error')
    # Getting the subscription data using the subscription manager.
    subscription_data = load_subscriptions()

    # Checking the customer id in the subscription data.
    if customer_id in subscription_data:
        customer_subscription_detail = subscription_data[customer_id]
        subscription_type = customer_subscription_detail['SubscriptionType']

        subscription_limit = get_rental_limit(subscription_type)
        subscription_status = check_subscription(customer_id, subscription_data)

        customer_rental_count = get_customer_rental_count(customer_id)
        
        # Checking whether the given game is available or not.
        game_availability = check_game_availability(game_id)

        if (subscription_status):
            available_limit = subscription_limit - customer_rental_count

            if (game_availability):
                if (available_limit > 0):
                    rent_game_and_update_db(game_id, customer_id)
                    return(f'Successfully Rented, Available rent limit : {available_limit - 1}', 'success')
                else:
                    return('You cannot rent another game due to subscription limit', 'error')
            else:
                update_rent_unavailability(game_id)
                return(f'Game Id number {game_id} is not available at this moment', 'error')

        else:
            return('Customer Subscription has expired, Please Renew', 'error')
    else:
        return('Customer Id could not be found in the Subscription File', 'error')


# Testing Environment

def test_rent_game_standalone():
    status = True
    try:
        customer_id = '1111'     # Customer Id is not in the subscription so checking its functionality
        game_id = 3         # Simulating the game_id input
        message, type = rent_game_standalone(customer_id,game_id)
        assert message == 'Customer Id could not be found in the Subscription File'


        customer_id = '4444'    # Customer Id is in the subscription but subscription expired
        game_id = 3             # Simulating the game_id input
        message, type = rent_game_standalone(customer_id,game_id)
        assert message == 'Customer Subscription has expired, Please Renew'


        customer_id = '4321'                         # Customer Id is present in the subscription and renting the game
        game_id = random.randint(15, 50);            # Random selecting any game id for the game_id input
        message, type = rent_game_standalone(customer_id,game_id)
        assert type == 'success'

        print("Renting Games with Id's Tests are working properly!")
        return status
    except Exception as e:
        print(f"Test failed: {e}")
        status = False
        return status



# Run the test
if __name__ == '__main__':
    if(test_rent_game_standalone()):
        print('All Test Passed')
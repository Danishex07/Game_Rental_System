from subscriptionManager import *
from database import select_from_db_fetch_all, read_from_db_fetch_all
import numpy as np
import pandas as pd

def recommendation_games(category):
    '''
    This function creates recommend games based on the Unavailability and rental history based upon the user choice.
    
    Keyword arguments:
    category: Reference to the dropdown option.
    
    '''
        
    category = category['new']
    category = category.split()
    category = category[-1]
    order_by = 'rental_unavailability_sum' if category == 'Unavailability' else 'games_title_count'
    coloum_index = 6 if category == 'Unavailability' else 5

    # Joining games with rental and then with images to get most number of records based upon the category. 
    query = f"SELECT games.id, games.title, games.genre, games_images.image, games.purchase_price, \
             COUNT(games.title) as games_title_count, SUM(rental.unavailability) as rental_unavailability_sum \
             FROM games INNER JOIN rental ON  games.id = rental.game_id \
             INNER JOIN games_images ON games.title = games_images.title \
             GROUP BY games.title ORDER BY {order_by} DESC LIMIT 5"

    records = select_from_db_fetch_all(query)
    records.reverse()

    # Gettting availability or rental count to be plotted on the x axis.
    x_values = [record[coloum_index] for record in records]

    # Gettting title to be plotted on the y axis.
    y_titles = [record[1] for record in records]

    records.reverse()
    return x_values, y_titles, category, records


def recommend_copies(records, weightage_list,flip, game_suggestion_input_text):
    '''
    This function gives recommend copies of the games based on the Unavailability and rental history or genre wise, 
    its value depends upon the user choice.
    
    Keyword arguments:
    records: List of records on which the copies to be recommended.
    weightage_list: The count of unavailability or rental or genre to give weightage for the distribution of the budgets amongs copies.
    flip : Boolean value to flip the array or not.
    game_suggestion_input_text: The ouput value of the game budget box value.
    
    '''
    weightage_array = np.array(weightage_list)
    if flip:
        weightage_array = np.flip(weightage_list)
    
    # Getting into the dataframe and summing along the coloum to get the total weight
    df = pd.DataFrame(weightage_array, columns=['weights'])
    totalWeightage = df['weights'].sum()
    
    # Allocating weight to diffrent weight to get the percentage value.
    percantage_weights = weightage_array / totalWeightage

    tabular_result = []
    for index, row in enumerate(records):
        title = row[1]
        genre = row[2]
        cover_image = row[3]
        price = row[4]
        
        # Formatting the records value to label and button, thus appending to a tabular_result list

        weight = percantage_weights[index]
        copies = int((int(game_suggestion_input_text) / price) * weight)

        title = f"{index + 1}. {title.split(':')[0]} ({genre})"
        if (flip):
            rented = row[5]
            not_available = row[6]
            title = title + f', UnAvailable = {not_available} times, Rented = {rented} times'
        spacer_1 = '' if len(str(copies)) > 1 else '0'
        spacer_2 = '' if len(str(price)) > 4 else '0'
        price = f"{spacer_1}{copies} Copies * {spacer_2}{price}£ = {copies * price:.2f}£"
        tabular_result.append((title, price, cover_image))

    return tabular_result


def games_genre():
    '''
    Calculating the games genre count based upon the rental history, to get the top 5 genre which are most rented out.
    '''
    
    query = f"SELECT games.genre, COUNT(*) as genre_count \
             FROM games INNER JOIN rental ON  games.id = rental.game_id \
             GROUP BY games.genre ORDER BY genre_count DESC LIMIT 5"

    records = select_from_db_fetch_all(query)

    label = [record[0] for record in records]
    sizes = [record[1] for record in records]

    return sizes, label


def games_suggestion_based_on_genre(genre):
    '''
    Suggestion of the games based upon the genre, to give 5 new games suggestion.
    '''

    query = f"SELECT games_suggestion.id, games_suggestion.title, games_suggestion.genre, games_images.image,\
              games_suggestion.purchase_price FROM games_suggestion \
              INNER JOIN games_images ON games_suggestion.title = games_images.title \
              WHERE genre = ? ORDER BY games_suggestion.title DESC LIMIT 5"

    records = read_from_db_fetch_all(query,genre)

    return records






# Testing Environment

def test_games_genre():
    status = True
    try:
        query = f"SELECT games.genre, COUNT(*) as genre_count \
                 FROM games INNER JOIN rental ON  games.id = rental.game_id \
                 GROUP BY games.genre ORDER BY genre_count DESC LIMIT 5"

        records = select_from_db_fetch_all(query)

        label = [record[0] for record in records]
        sizes = [record[1] for record in records]
        # Add assertions to check if the tables and data are fetched as expected
        assert len(sizes) > 0
        assert len(label) > 0
        print("Data loading from test_games_genre function test passed!")
        return status
    except AssertionError as e:
        status = False
        print(f"Data loading from test_games_genre function test failed: {e}")
        return status

def test_games_suggestion_based_on_genre(genre):
    status = True
    try:
        query = f"SELECT games_suggestion.id, games_suggestion.title, games_suggestion.genre, games_images.image,\
                   games_suggestion.purchase_price FROM games_suggestion \
                   INNER JOIN games_images ON games_suggestion.title = games_images.title \
                   WHERE genre = ? ORDER BY games_suggestion.title DESC LIMIT 5"

        records = read_from_db_fetch_all(query,genre)
        # Add assertions to check if the tables and data are fetched as expected
        assert len(records) > 0

        print("Data loading from test_games_suggestion_based_on_genre function test passed!")
        return status
    except AssertionError as e:
        status = False
        print(f"Data loading from test_games_suggestion_based_on_genre function test failed: {e}")
        return status

def test_recommendation_games(category):
    status = True
    genre = 'Action-Adventure'
    category = category['new']
    category = category.split()
    category = category[-1]
    order_by = 'rental_unavailability_sum' if category == 'Unavailability' else 'games_title_count'
    coloum_index = 6 if category == 'Unavailability' else 5
    try:
        query = f"SELECT games.id, games.title, games.genre, games_images.image, games.purchase_price, \
                 COUNT(games.title) as games_title_count, SUM(rental.unavailability) as rental_unavailability_sum \
                 FROM games INNER JOIN rental ON  games.id = rental.game_id \
                 INNER JOIN games_images ON games.title = games_images.title \
                 GROUP BY games.title ORDER BY {order_by} DESC LIMIT 5"

        records = select_from_db_fetch_all(query)

        # Add assertions to check if the tables and data are fetched as expected
        assert len(records) > 0

        print("Data loading from test_recommendation_games function test passed!")
        return status
    except AssertionError as e:
        status = False
        print(f"Data loading from test_recommendation_games function test failed: {e}")
        return status



if __name__ == '__main__':
    if(test_games_genre()):
        genre = 'Action-Adventure' # Simulation of Selecting genre
        if(test_games_suggestion_based_on_genre(genre)):
            drop_down_selection = {} # Simulation of Dropdown Button
            drop_down_selection['new'] = 'Based on Unavailability'
            if(test_recommendation_games(drop_down_selection)):
                print('All Test Passed')
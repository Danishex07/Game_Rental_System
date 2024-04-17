import base64
from database import read_from_db_fetch_all
import random


def search_game_standalone(game_title):
    '''
    Searching the games based upon the given parameter and to query the database and fetching the result.
    '''
        
    query = f"SELECT games.*, games_icons.image \
                             FROM games INNER JOIN games_icons ON  games.title = games_icons.title \
                             WHERE games.title LIKE ?"

    parameter = f"%{game_title}%"

    records = read_from_db_fetch_all(query,parameter)
    search_result = []
    
    # Styling the fetched records and conversion of blob images to base64 image to show them in the tabular format.
    for row in records:
        id = row[0]
        title = row[1]
        platform = row[2]
        genre = row[3]
        purchase_price = row[4]
        purchase_date = row[5]
        icon = row[6]
        icon = base64.b64encode(icon).decode('utf-8')
        icon_html_code = f'<img style="height:70px; widht:70px" src="data:image/jpg;base64,{icon}" alt="{title}">'
        search_result.append((id,  title, platform, genre, purchase_price, purchase_date, icon_html_code))
    return search_result;

# Testing Environment

def test_search_game_standalone():
    status = True
    try:
        user_choices = ['Minecraft', 'Super Mario', 'ca', 'sp', 'c', 'a', 'Monster Hunter', 'Sekiro', 'Mortal Kombat',
                        'StarCraft', 'Gh', 'Te', 'Among', 'Fi', 'Rainbow', 'Terraria']
        game_title = random.choice(user_choices)     # Simulating the game_title input by giving random user_choices

        result = search_game_standalone(game_title)
        assert len(result) > 0
        print("Searching Games Tests is working properly!")
        return status
    except Exception as e:
        print(f"Test failed: {e}")
        status = False
        return status

# Run the test
if __name__ == '__main__':
    if(test_search_game_standalone()):
        print('All Test Passed')
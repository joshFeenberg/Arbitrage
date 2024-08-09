import time
import threading
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  
options = Options()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)

data_dict_mlb = {}
data_dict_nfl = {}

def everygameMLB():
    global data_dict_mlb
    while True:
        driver.get("https://sports.everygame.eu/en/Bets/Baseball/4")
        time.sleep(10)
        new_data_dict = {}
        uls = driver.find_elements(By.CSS_SELECTOR, 'ul.tab.nextbets.active')
        for ul in uls:
            list_items = ul.find_elements(By.XPATH, './/li')
            for game in list_items: 
                game_text = game.text.split("\n")
                try:
                    game_name = game_text[0]
                    away_odds = game_text[2]
                    home_odds = game_text[4]
                    game_time = game_text[5]
                    new_data_dict[game_name] = {
                        "odds": {
                            "awayOdds": away_odds,
                            "homeOdds": home_odds
                        },
                        "gameTime": game_time
                    }
                except:
                    pass
        data_dict_mlb = new_data_dict
        time.sleep(60)

def everygameNFL():
    global data_dict_nfl
    while True:
        driver.get("https://sports.everygame.eu/en/Bets/American-Football/NFL-Preseason-Lines/1017")
        time.sleep(5)
        new_data_dict = {}
        element = driver.find_element(By.CSS_SELECTOR, 'li.singlemarkettype.onemarket[data-mt-nm="Game Lines"]')
        games = element.find_elements(By.CSS_SELECTOR, 'div.onemarket.tr')
        for game in games:
            game_text = game.text.split("\n")
            try:
                if len(game_text) == 13:
                    game_name = game_text[1] + " @ " + game_text[2]
                    away_odds = game_text[-2]
                    home_odds = game_text[-1]
                    game_time = game_text[0]
                    new_data_dict[game_name] = {
                        "odds": {
                            "awayOdds": away_odds,
                            "homeOdds": home_odds
                        },
                        "gameTime": game_time
                    }
            except:
                pass
        data_dict_nfl = new_data_dict
        time.sleep(60)

@app.route('/everygameMLB', methods=['GET'])
def get_mlb_games():
    return jsonify(data_dict_mlb)

@app.route('/everygameNFL', methods=['GET'])
def get_nfl_games():
    return jsonify(data_dict_nfl)

if __name__ == '__main__':
    thread_mlb = threading.Thread(target=everygameMLB, daemon=True)
    thread_nfl = threading.Thread(target=everygameNFL, daemon=True)
    thread_mlb.start()
    thread_nfl.start()
    app.run(host='0.0.0.0', port=5001)

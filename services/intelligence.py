import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from utils.logger import logger
from utils import telegram
from services import account, monitoring
from config import Config as cfg
import requests
from datetime import datetime
import json

tlgm = telegram.Telegram()
acc = account.Account()
mnt = monitoring.Monitor()


class Intelligence:
    
    def __init__(self):
        return
    
    def get_player_scores(self, player_ids):
        scores = []
        for player_id in player_ids:
            player_details = acc.get_player_detail(player_id)
            name = player_details["data"]["firstname"] + " " + player_details["data"]["lastname"]
            previous_season = self.get_elite_procspect_details(name)

            rank = player_details["data"]["rank"]
            team_id = player_details["data"]["team"]["id"]
            team_name = player_details["data"]["team"]["name"]
            is_foreigner = player_details["data"]["is_foreigner"]
            market_value = player_details["data"]["marketvalue"]
            market_value_trend = player_details["data"]["marketvalue_trend"]
            points = player_details["data"]["points"]
            average_points = player_details["data"]["points_avg"]
            position = player_details["data"]["position_name"]
            if position != "Goalie":
                games = player_details["data"]["stats_summary"][0]["value"]
                goals = player_details["data"]["stats_summary"][1]["value"]
                assists = player_details["data"]["stats_summary"][2]["value"]
                plus_minus = player_details["data"]["stats_summary"][3]["value"]
                shots_on_goal = player_details["data"]["stats_summary"][4]["value"]
                shots_blocked = player_details["data"]["stats_summary"][5]["value"]
                faceoffs_won = player_details["data"]["stats_summary"][6]["value"]
                fouls = player_details["data"]["stats_summary"][7]["value"]

                pevious_games = previous_season[0]["games"]
                pevious_goals = previous_season[0]["goals"]
                pevious_assists = previous_season[0]["assists"]

            else:
                games = player_details["data"]["stats_summary"][0]["value"]
                goals_against = player_details["data"]["stats_summary"][1]["value"]
                shots_against = player_details["data"]["stats_summary"][2]["value"]
                saves = player_details["data"]["stats_summary"][3]["value"]
                games_won = player_details["data"]["stats_summary"][4]["value"]
                save_rate = player_details["data"]["stats_summary"][5]["value"]
                assists = player_details["data"]["stats_summary"][6]["value"]
                shoot_outs = player_details["data"]["stats_summary"][7]["value"]

                pevious_games = previous_season[0]["games"]
                previous_goals_against = previous_season[0]["goal_against"]
                previous_average_goals_against = previous_season[0]["average_goal_against"]        
                pevious_save_rate = previous_season[0]["save_rate"]
                previous_shoot_outs = previous_season[0]["shoot_outs"]          


        return games, pevious_games

    def get_elite_procspect_details(self, player_name, season_end_year=[datetime.now().year]):
    
        player_details = []

        url_search = f'https://autocomplete.eliteprospects.com/all?q={player_name.lower()}&hideNotActiveLeagues=1'
        search_response = requests.get(url_search, headers=cfg.ep.HEADERS).json()
        eliteprospect_id = search_response[0]["id"]
        url_details = f'https://gql.eliteprospects.com/?operationName=PlayerStatisticDefault&variables={{"player":"{eliteprospect_id}","leagueType":"league","sort":"season"}}&extensions={{"persistedQuery":{{"version":1,"sha256Hash":"922817a06790cfca6ead3f987d2da2a7d5213eca323f574bec51305d9582d602"}}}}'
        eliteprospect_details = requests.get(url_details, headers=cfg.ep.HEADERS).json()
        print(eliteprospect_details)

        excluded_leagues = ["International", "WC"]
        last_club_season = [edge for edge in eliteprospect_details["data"]["playerStats"]["edges"] if edge["season"]["endYear"] in season_end_year and edge["leagueName"] not in excluded_leagues]
        for i in range(0, len(last_club_season)):
            if last_club_season[i]["postseasonStats"] is not None:
                    player_details.append(
                                        {
                                        "season": last_club_season[i]["season"]["endYear"],
                                        "league_name": last_club_season[i]["leagueName"],
                                        "games": (last_club_season[i]["regularStats"]["GP"] or 0) + (last_club_season[i]["postseasonStats"]["GP"] or 0),
                                        "goals": (last_club_season[i]["regularStats"]["G"] or 0) + (last_club_season[i]["postseasonStats"]["G"] or 0),
                                        "assist": (last_club_season[i]["regularStats"]["A"] or 0) + (last_club_season[i]["postseasonStats"]["A"] or 0),
                                        "goal_against": (last_club_season[i]["regularStats"]["GA"] or 0) + (last_club_season[i]["postseasonStats"]["GA"] or 0),
                                        "average_goal_against": (last_club_season[i]["regularStats"]["GAA"] or 0) + (last_club_season[i]["postseasonStats"]["GAA"] or 0),
                                        "save_rate": (last_club_season[i]["regularStats"]["SVP"] or 0) + (last_club_season[i]["postseasonStats"]["SVP"] or 0),
                                        "shoot_outs": (last_club_season[i]["regularStats"]["SO"] or 0) + (last_club_season[i]["postseasonStats"]["SO"] or 0)                               
                                        }
                                        )
            else:
                    player_details.append(
                                        {
                                        "season": last_club_season[i]["season"]["endYear"],
                                        "league_name": last_club_season[i]["leagueName"],
                                        "games": (last_club_season[i]["regularStats"]["GP"] or 0),
                                        "goals": (last_club_season[i]["regularStats"]["G"] or 0),
                                        "assist": (last_club_season[i]["regularStats"]["A"] or 0),
                                        "goal_against": (last_club_season[i]["regularStats"]["GA"] or 0),
                                        "average_goal_against": (last_club_season[i]["regularStats"]["GAA"] or 0),
                                        "save_rate": (last_club_season[i]["regularStats"]["SVP"] or 0),
                                        "shoot_outs": (last_club_season[i]["regularStats"]["SO"] or 0)                              
                                        }
                                        )            

        return player_details
            
    def get_line_up_reccomendation(self):
        suggestions = {}
        return suggestions
    
    def get_next_opponent(self, player_id):
        return
    
    def get_biding_recommendation(self):
        biding_reccommendations = {}
        return biding_reccommendations
    
if __name__ == '__main__':

    intl = Intelligence()

    print(intl.get_elite_procspect_details("Nils Bächler", [2023, 2024]))
    # print(intl.get_player_scores([317063]))


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
    
    def get_player_scores(self, player_ids, mode="efficiency"):
        score_table = []
        for player_id in player_ids:
            player_details = acc.get_player_detail(player_id)
            # print(player_details)
            name = player_details["data"]["firstname"] + " " + player_details["data"]["lastname"]
            previous_season_ep = self._get_elite_procspect_details(name)

            # rank = player_details["data"]["rank"]
            # team_id = player_details["data"]["team"]["id"]
            # team_name = player_details["data"]["team"]["name"]
            # is_foreigner = player_details["data"]["is_foreigner"]
            market_value = player_details["data"]["marketvalue"]
            # market_value_trend = player_details["data"]["marketvalue_trend"]
            # points = player_details["data"]["points"]
            average_points = player_details["data"]["points_avg"]
            position = player_details["data"]["position_name"]
            if position != "Goalie":
                games = player_details["data"]["stats_summary"][0]["value"]
                # goals = player_details["data"]["stats_summary"][1]["value"]
                # assists = player_details["data"]["stats_summary"][2]["value"]
                # plus_minus = player_details["data"]["stats_summary"][3]["value"]
                # shots_on_goal = player_details["data"]["stats_summary"][4]["value"]
                # shots_blocked = player_details["data"]["stats_summary"][5]["value"]
                # faceoffs_won = player_details["data"]["stats_summary"][6]["value"]
                # fouls = player_details["data"]["stats_summary"][7]["value"]

                previous_games = previous_season_ep[0]["games"]
                if player_details["data"]["point_metrics"]:
                    # previous_points = player_details["data"]["point_metrics"][0]["points"]
                    previous_average_points = player_details["data"]["point_metrics"][0]["points_avg"]
                previous_goals = previous_season_ep[0]["goals"]
                previous_assists = previous_season_ep[0]["assist"]

            else:
                games = player_details["data"]["stats_summary"][0]["value"]
                # goals_against = player_details["data"]["stats_summary"][1]["value"]
                # shots_against = player_details["data"]["stats_summary"][2]["value"]
                # saves = player_details["data"]["stats_summary"][3]["value"]
                # games_won = player_details["data"]["stats_summary"][4]["value"]
                # save_rate = player_details["data"]["stats_summary"][5]["value"]
                # assists = player_details["data"]["stats_summary"][6]["value"]
                # shoot_outs = player_details["data"]["stats_summary"][7]["value"]

                previous_games = previous_season_ep[0]["games"]
                previous_wins = previous_season_ep[0]["wins"]
                if player_details["data"]["point_metrics"]:
                    # previous_points = player_details["data"]["point_metrics"][0]["points"]
                    previous_average_points = player_details["data"]["point_metrics"][0]["points_avg"]
                # previous_goals_against = previous_season_ep[0]["goal_against"]
                pevious_save_rate = previous_season_ep[0]["save_rate"]
                # previous_shoot_outs = previous_season_ep[0]["shoot_outs"] 
                
            weight = cfg.intl.CURRENT_SEASON_SOCRING_WEIGHT*(games/50)

            if mode == "performance":

                if player_details["data"]["point_metrics"]:
                    score = (previous_average_points +  weight*(average_points)) / (1+weight)
                
                elif position != "Goalie":
                    score = ((previous_goals * 60 + previous_assists * 40) / previous_games) + weight*(average_points) / (1+weight)

                else:
                    score = ((((pevious_save_rate * 7000) / previous_games) + weight*(average_points)) / (1+weight))
            
            else:

                if player_details["data"]["point_metrics"]:
                    score = (((max(previous_average_points - 20, 0) +  weight*(max(average_points - 20, 0))) * 10000) / (1+weight)) / market_value 
                
                elif position != "Goalie":
                    score = (((max(((previous_goals * 60 + previous_assists * 40) / previous_games) - 20, 0) + weight*(max(average_points - 20, 0))) * 10000) / (1+weight)) / market_value

                else:
                    score = (((max(((pevious_save_rate * 7000) / previous_games) - 20, 0) + weight*(max(average_points - 20, 0))) * 10000) / (1+weight)) / market_value


            scoring_details = {
                    "id": player_id,
                    "name": name,
                    "position": position,
                    "score": score
            }
            score_table.append(scoring_details)


        return score_table

    def _get_elite_procspect_details(self, player_name, season_end_year=[datetime.now().year]):
    
        player_details = []

        url_search = f'https://autocomplete.eliteprospects.com/all?q={player_name.lower()}&hideNotActiveLeagues=1'
        search_response = requests.get(url_search, headers=cfg.ep.HEADERS).json()
        eliteprospect_id = search_response[0]["id"]
        url_details = f'https://gql.eliteprospects.com/?operationName=PlayerStatisticDefault&variables={{"player":"{eliteprospect_id}","leagueType":"league","sort":"season"}}&extensions={{"persistedQuery":{{"version":1,"sha256Hash":"922817a06790cfca6ead3f987d2da2a7d5213eca323f574bec51305d9582d602"}}}}'
        eliteprospect_details = requests.get(url_details, headers=cfg.ep.HEADERS).json()
        # print(eliteprospect_details)
        excluded_leagues = ["International", "WC", "WJC-20", "International-Jr"]
        print(player_name)
        for s in range(0, len(season_end_year)):
            last_club_season = [edge for edge in eliteprospect_details["data"]["playerStats"]["edges"] if edge["season"]["endYear"] == season_end_year[s] and edge["leagueName"] not in excluded_leagues]
            for i in range(0, len(last_club_season)):
                if last_club_season[i]["postseasonStats"] is not None:
                    # print(last_club_season[i]["leagueName"])
                    # print(last_club_season[i]["postseasonStats"])
                    # print((last_club_season[i]["regularStats"]["GAA"] or 0))
                    # print(type(last_club_season[i]["regularStats"]["GAA"] or 0))
                    # print((last_club_season[i]["postseasonStats"]["GAA"] or 0))
                    # print(type(last_club_season[i]["postseasonStats"]["GAA"] or 0))

                    if i == 0:
                        player_details.append(
                                            {
                                            "season": last_club_season[i]["season"]["endYear"],
                                            "leagues": last_club_season[i]["leagueName"],
                                            "games": float(last_club_season[i]["regularStats"]["GP"] or 0) + float(last_club_season[i]["postseasonStats"]["GP"] or 0),
                                            "wins": float(last_club_season[i]["regularStats"]["W"] or 0) + float(last_club_season[i]["postseasonStats"]["W"] or 0),
                                            "goals": float(last_club_season[i]["regularStats"]["G"] or 0) + float(last_club_season[i]["postseasonStats"]["G"] or 0),
                                            "assist": float(last_club_season[i]["regularStats"]["A"] or 0) + float(last_club_season[i]["postseasonStats"]["A"] or 0),
                                            "goal_against": float(last_club_season[i]["regularStats"]["GA"] or 0) + float(last_club_season[i]["postseasonStats"]["GA"] or 0),
                                            "shots_on_goalie": (float(last_club_season[i]["regularStats"]["GA"] or 0) + float(last_club_season[i]["postseasonStats"]["GA"] or 0)) / (1-(float(last_club_season[i]["regularStats"]["SVP"] or 0))),
                                            "shoot_outs": float(last_club_season[i]["regularStats"]["SO"] or 0) + float(last_club_season[i]["postseasonStats"]["SO"] or 0)                               
                                            }
                                            )
                    else:
                        player_details[s]["leagues"] = player_details[s]["leagues"] + ", " + last_club_season[i]["leagueName"]
                        player_details[s]["games"] = player_details[s]["games"] + (float(last_club_season[i]["regularStats"]["GP"] or 0) + float(last_club_season[i]["postseasonStats"]["GP"] or 0))
                        player_details[s]["wins"] = player_details[s]["wins"] + (float(last_club_season[i]["regularStats"]["W"] or 0) + float(last_club_season[i]["postseasonStats"]["W"] or 0))
                        player_details[s]["goals"] = player_details[s]["goals"] + (float(last_club_season[i]["regularStats"]["G"] or 0) + float(last_club_season[i]["postseasonStats"]["G"] or 0))
                        player_details[s]["assist"] = player_details[s]["assist"] + (float(last_club_season[i]["regularStats"]["A"] or 0) + float(last_club_season[i]["postseasonStats"]["A"] or 0))
                        player_details[s]["goal_against"] = player_details[s]["goal_against"] + (float(last_club_season[i]["regularStats"]["GA"] or 0) + float(last_club_season[i]["postseasonStats"]["GA"] or 0))
                        player_details[s]["shots_on_goalie"] = player_details[s]["shots_on_goalie"] + (float(last_club_season[i]["regularStats"]["GA"] or 0) + float(last_club_season[i]["postseasonStats"]["GA"] or 0)) / (1-(float(last_club_season[i]["regularStats"]["SVP"] or 0)))
                        player_details[s]["shoot_outs"] = player_details[s]["shoot_outs"] + (float(last_club_season[i]["regularStats"]["SO"] or 0) + float(last_club_season[i]["postseasonStats"]["SO"] or 0) )
                
                else:            
                    if i == 0:
                        player_details.append(
                                            {
                                            "season": last_club_season[i]["season"]["endYear"],
                                            "leagues": last_club_season[i]["leagueName"],
                                            "games": float(last_club_season[i]["regularStats"]["GP"] or 0),
                                            "wins": float(last_club_season[i]["regularStats"]["W"] or 0),
                                            "goals": float(last_club_season[i]["regularStats"]["G"] or 0),
                                            "assist": float(last_club_season[i]["regularStats"]["A"] or 0),
                                            "goal_against": float(last_club_season[i]["regularStats"]["GA"] or 0),
                                            "shots_on_goalie": float(last_club_season[i]["regularStats"]["GA"] or 0)/(1-float(last_club_season[i]["regularStats"]["SVP"] or 0)),
                                            "shoot_outs": float(last_club_season[i]["regularStats"]["SO"] or 0)                               
                                            }
                                            )
                    else:
                        player_details[s]["leagues"] = player_details[s]["leagues"] + ", " + last_club_season[i]["leagueName"]
                        player_details[s]["games"] = player_details[s]["games"] + (float(last_club_season[i]["regularStats"]["GP"] or 0))
                        player_details[s]["wins"] = player_details[s]["wins"] + (float(last_club_season[i]["regularStats"]["W"] or 0))
                        player_details[s]["goals"] = player_details[s]["goals"] + (float(last_club_season[i]["regularStats"]["G"] or 0))
                        player_details[s]["assist"] = player_details[s]["assist"] + (float(last_club_season[i]["regularStats"]["A"] or 0))
                        player_details[s]["goal_against"] = player_details[s]["goal_against"] + (float(last_club_season[i]["regularStats"]["GA"] or 0))
                        player_details[s]["shots_on_goalie"] = player_details[s]["shots_on_goalie"] + float(last_club_season[i]["regularStats"]["GA"] or 0)/(1-float(last_club_season[i]["regularStats"]["SVP"] or 0))
                        player_details[s]["shoot_outs"] = player_details[s]["shoot_outs"] + (float(last_club_season[i]["regularStats"]["SO"] or 0))        
            if player_details[s]["shots_on_goalie"] != 0: 
                player_details[s]["save_rate"] = 1 - (player_details[s]["goal_against"] / player_details[s]["shots_on_goalie"])
            else:
                player_details[s]["save_rate"] = 0


        return player_details
            
    def get_line_up_reccomendation(self):
        mode="performance"
        suggestion_ids = {"players":{}}
        suggestion_names = {"players":{}}
        score_table = self.get_player_scores(acc.get_roster(mode="player_ids"), mode=mode)

        goalies = [player for player in score_table if player["position"] == "Goalie"]
        defencemen = [player for player in score_table if player["position"] == "Defenceman"]
        forwards = [player for player in score_table if player["position"] == "Forward"]

        goalies_sorted = sorted(goalies, key=lambda x: x["score"], reverse=True)
        defencemen_sorted = sorted(defencemen, key=lambda x: x["score"], reverse=True)
        forwards_sorted = sorted(forwards, key=lambda x: x["score"], reverse=True)

        best_goalie_id = [goalies_sorted[0]["id"]] if goalies_sorted else []
        best_defencemen_ids = [player["id"] for player in defencemen_sorted[:6]]
        best_forwards_ids = [player["id"] for player in forwards_sorted[:9]]

        suggestion_ids['players']['1'] = best_goalie_id[0]

        defencemen_keys = ['2', '3', '7', '8', '12', '13']
        for i, key in enumerate(defencemen_keys):
            suggestion_ids['players'][key] = best_defencemen_ids[i]

        forward_keys = ['4', '5', '6', '9', '10', '11', '14', '15', '16']
        for i, key in enumerate(forward_keys):
            suggestion_ids['players'][key] = best_forwards_ids[i]

        best_goalie_name = [goalies_sorted[0]["name"]] if goalies_sorted else []
        best_defencemen_name = [player["name"] for player in defencemen_sorted[:6]]
        best_forwards_name = [player["name"] for player in forwards_sorted[:9]]

        suggestion_names['players']['1'] = best_goalie_name[0]

        defencemen_keys = ['2', '3', '7', '8', '12', '13']
        for i, key in enumerate(defencemen_keys):
            suggestion_names['players'][key] = best_defencemen_name[i]

        forward_keys = ['4', '5', '6', '9', '10', '11', '14', '15', '16']
        for i, key in enumerate(forward_keys):
            suggestion_names['players'][key] = best_forwards_name[i]

        return suggestion_ids, suggestion_names
    
    def get_next_opponent(self, player_id):
        return
    
    def get_biding_recommendation(self):
        biding_reccommendations = {}
        return biding_reccommendations
    
if __name__ == '__main__':

    intl = Intelligence()
    acc = account.Account()

    print(intl._get_elite_procspect_details("noah patenaude", [2023, 2024]))
    
    # print(intl.get_player_scores([149071]))

    # print(intl.get_player_scores(acc.get_roster(mode="player_ids"), mode="efficiency"))
    # print(intl.get_player_scores(acc.get_roster(mode="player_ids"), mode="performance"))
    
    # print(intl.get_line_up_reccomendation())


from RL.util import Init_throw_range, add_action_to_play_dict, eliminate_and_update_board, calculate_normal_probability, get_symbol_by_location
from RL.action import get_all_valid_action
from RL.action_evaluation import action_evaluation
from RL.state import State
from copy import copy, deepcopy
from RL.random_algorithms import refined_random_throw, random_throw, random_action, get_current_player_nodes_count
import random
import csv
from RL.learning import temporal_difference_learning
import os
import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
import collections
from collections import defaultdict as dd
from RL.prediction import getScoredActionList, select_enemy_next_index, update_next_enemy_action, draw_avoid_best_action, update_accuracy_of_prediction, record_enemy_action_index


class Player:
    
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.
        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        self.TEMPORAL_DIFF_LEARNING = True
        self.USE_TOTAL_SCORE_PREDICTION = True
        self.GREEDY_PREDICT = False
        self.EXCLUDE_THROW_DIST = True
        self.ANALYSIS_MODE = True
        self.AVOID_DRAW = True   # if algorithm break tie automatically
        self.REFINED_THROW = True   # if using advanced random throw strategy
        self.CONFIDENCE_LEVEL = 0.05   #confidence level to exclude outliers into distribution
        self.IGNORE_ROUND = 5  # ignore first 5 rounds when doing probability predicting
        self.beta = 0.2         
        self.episilon = 0.1

        self.game_round = 1
        self.throws_left = 9   # reduced by 1 after each throw in util/add_action_board function
        self.enemy_throws_left = 9
        self.side = player
        if self.side == "upper":
            self.enemy_side = "lower"
        else:
            self.enemy_side = "upper"

        # Determine throw range according to different locations
        self.throw_range = tuple()
        self.enemy_throws_range = tuple()
        Init_throw_range(self)

        # play_dict is used to store symbols for each player
        self.play_dict = {"player":{"r":[], "p":[], "s":[]},
                        "opponent":{"r":[], "p":[], "s":[]},
                        "block":[]}                     
                        # "R":[(1,3),(3,4)]   saying Rock1 at position (1,3) and Rock2 at (3,4)
        
        # target_dict is used to store relationship between 2 symbols
        self.target_dict = {"r":"s", "s":"p", "p":"r"}

        # Store Opponent's Action List
        self.score_names = ["Total_Score_Index", "Aggresive_Index", "Defense_Index", "Punishment_Index", "State_Score_Index"]
        self.opponent_score_array = np.array(0)
        self.enemy_action_dist_dict = {}
        self.predicted_enemy_action = ()
        self.corrected_predict = 0
        self.total_predict = 0
        self.predict_accuracy = 0.0
        
        

        # Store history to Check Draw Game
        self.history = collections.Counter({self._snap(): 1})
        self.cur_snap_used_action_index = dd(int)  # a dictionary that stores used action for every snap to avoid those steps in the future
            # {state1: 0,1,2}   at state1 used action at index 0, 1 and 2, so next time starting from 3
        self.states_list = []   # used to store states happen in the past turn, a list of State object



    def action(self):
        
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        next_enemy_action = None
        # hard code the first three rounds to lay out my defensive 
        if self.game_round <= 3:
            return open_game_stragety(self)
        else:
            # ---------------Prediction---------------
            # After certain rounds, get enough data of opponent and start to predict opponent's next action
            if (self.game_round > self.IGNORE_ROUND):

                # Get sorted Action Evaluation List for Enemy's choice
                opponent_action_score_list = getScoredActionList(self, "opponent")
                #in the format of [(Score,  Action,  Probability,  Reward Explanation), (.......)]
                
                predict_index = select_enemy_next_index(self)
                self.predicted_enemy_action = update_next_enemy_action(self, predict_index)   
                assert(self.predicted_enemy_action != None)

            ### ----------------Choose Best Step For Our Player
            # Get sorted Scored Action Evaluation List for us to choose
            player_total_score_list = getScoredActionList(self, "player", self.predicted_enemy_action)
            
            
            # Check Repeated State
            # Avoid Draw Situation, take another action without using already used indexes checked by default dict
            cur_snap = self._snap()
            if (self.history[cur_snap] >= 2 and self.AVOID_DRAW):
                return draw_avoid_best_action(self, player_total_score_list, cur_snap)
            else:
                return player_total_score_list[0][1]
            
            # return best action, if no action, do evaluation without enemy's action
            if len(player_total_score_list) < 1:
                player_total_score_list = getScoredActionList(self, "player", next_enemy_action)
            else:
                die_num = random.uniform(0, 1)
                if die_num <= self.episilon:
                    return random.choice(get_all_valid_action("player", self.states_list[-1]))
                else:
                    return player_total_score_list[0][1]

    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        # count enemy's choices index based on our function into array
        if (self.game_round > self.IGNORE_ROUND):
            update_accuracy_of_prediction(self,opponent_action)
            record_enemy_action_index(self, opponent_action)

        # do not calculate elimination now, just update symbols to play_dict
        # add each player's action to board for the reason of synchronising play.
        # if throw, also reduce throws left by 1
        add_action_to_play_dict(self, "opponent", opponent_action)
        add_action_to_play_dict(self, "player", player_action)
        # update self representation of the game
        # Calculate eliminations and update
        # after token actions, check if eliminate other tokens by following function
        eliminate_and_update_board(self,self.target_dict)


        if ((self.TEMPORAL_DIFF_LEARNING==True)):
            # store state into a file 
            new_state = State(copy(self.play_dict), copy(self.throws_left),
                                    copy(self.enemy_throws_left), copy(self.side))
            self.states_list.append(new_state)

            if (self.game_round >= 4):
                if os.stat("RL/weights.csv").st_size == 0:
                    pre_w = [10, 5, -5]
                else:
                    with open("RL/weights.csv") as csv_file:
                        csv_reader = csv.reader(csv_file, delimiter=',')
                        row = next(csv_reader)
                        pre_w = []
                        for num in row:
                            pre_w.append(float(num))
                    #print("Previous weight: ", pre_w)
                    update_w = temporal_difference_learning(self.states_list, pre_w, self.beta) 
                    #print("Weights after update: ", update_w)                       
                    with open('RL/weights.csv', 'w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(update_w)
        

        # Take a snap of current game state and store it
        cur_snap = self._snap()
        self.history[cur_snap] += 1
        self.game_round += 1


        #Analyse Enemy's choice based on our evaluation list 
        if (self.ANALYSIS_MODE):
            if (self.game_round>self.IGNORE_ROUND):
                array = self.opponent_score_array
                # dist.agg(['min', 'max', 'mean', 'std']).round(decimals=2)
                print("\n Enemy Index Mean:")
                print(np.mean(array))
                print("\n Enemy Index STD:")
                print(np.std(array))
                print("\nAccuracy of Prediction:")
                if self.total_predict:
                    print(round(self.corrected_predict/self.total_predict,3))
                print("\nMake Prediction Percentage:")
                print(round(self.total_predict/self.game_round,3))
                # fig, ax = plt.subplots()
                # dist.plot.hist(density=True, ax=ax)
                # ax.set_ylabel('Probability')
                # ax.grid(axis='y')
                # ax.set_facecolor('#d8dcd6')
                # plt.savefig("output.png")

    
    def _snap(self):
        """
        Capture the current play state in a hashable way
        (for repeated-state checking)
        reference: referee/game.py from Melbourne Uni AI Tutor's code
        """
        play_history = []
        for i in "rps":
            play_history.append(tuple(sorted(self.play_dict["player"][i])))
            play_history.append(tuple(sorted(self.play_dict["opponent"][i])))
        return (tuple(play_history),
            # with the same number of throws remaining for each player
            self.throws_left,
            self.enemy_throws_left,
        )


def open_game_stragety(self):
    if self.game_round == 1: 
        if self.side == "upper":
            return ('THROW', 'r', (4, -4))
        if self.side == "lower":
            return ("THROW", "r", (-4, 2))
    if self.game_round == 2: 
        if self.side == "upper":
            return ("THROW", "p", (3, -2))
        if self.side == "lower":
            return ("THROW", "p", (-3, 2))
    if self.game_round == 3: 
        if self.side == "upper":
            return ("THROW", "s", (4, -1))
        if self.side == "lower":
            return ("THROW", "s", (-3, 1))




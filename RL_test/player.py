from RL_test.util import Init_throw_range, add_action_to_play_dict, eliminate_and_update_board, calculate_normal_probability, get_symbol_by_location
from RL_test.action import get_all_valid_action
from RL_test.action_evaluation import action_evaluation
from RL_test.state import State
from copy import copy
from copy import deepcopy
import random
from RL_test.random_algorithms import refined_random_throw, random_throw, random_action, get_current_player_nodes_count
import csv
from RL_test.learning import temporal_difference_learning
import os
import numpy as np


import math
import pandas as pd
import matplotlib.pyplot as plt
import collections
from collections import defaultdict as dd

class Player:
    
    
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.
        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        self.TEMPORAL_DIFF_LEARNING = False
        self.USE_TOTAL_SCORE_PREDICTION = True
        self.GREEDY_PREDICT = False
        self.EXCLUDE_THROW_DIST = True
        self.ANALYSIS_MODE = True
        self.AVOID_DRAW = True   # if algorithm break tie automatically
        self.REFINED_THROW = True   # if using advanced random throw strategy
        self.CONFIDENCE_LEVEL = 0.05   #confidence level to exclude outliers into distribution
        self.IGNORE_ROUND = 5  # ignore first 5 rounds when doing probability predicting
        self.beta = 0.01
        self.episilon = 0.3

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
        self.opponent_action_score_list = []
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
        # Get Enemy Action's Probability and return the mean index using "Total Score"
        selected_score = 0
        selected_index = 0
        next_enemy_action = None
        # hard code the first three rounds to lay out my defensive 
        if self.game_round <= 3:
            player_best_action = open_game_stragety(self)
        else:
            ### ---------------Prediction

            
            #after certain rounds, start to predict
            if (self.game_round>self.IGNORE_ROUND):
            # Get sorted Action Evaluation List for Enemy's choice
                self.opponent_action_score_list = self.getScoredActionList("opponent")
            #if (self.opponent_action_score_list):
                predict_index = self.select_enemy_next_index()
                self.predicted_enemy_action = self.update_next_enemy_action(predict_index)   
                assert(self.predicted_enemy_action!=None)
            ### ----------------Choose Best Step For Our Player
            # Get sorted Scored Action Evaluation List for us to choose
            player_total_score_list = self.getScoredActionList("player", self.predicted_enemy_action)
            
            
            # Check Repeated State
            # Avoid Draw Situation, take another action without using already used indexes checked by default dict
            cur_snap = self._snap()
            if (self.history[cur_snap] >= 2 and self.AVOID_DRAW):
                player_best_action = self.draw_avoid_best_action(player_total_score_list, cur_snap)
            else:
                player_best_action = player_total_score_list[0][1]
            
            # if not player_best_action:
            #     # if no action, redo evaluation without enemy's action
            #     player_total_score_list = self.getScoredActionList("player", next_enemy_action)
        
        #input("asd")
        return player_best_action
            

        
    
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
            self.update_accuracy_of_prediction(opponent_action)
            self.record_enemy_action_index(opponent_action)

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


    def update_accuracy_of_prediction(self, opponent_action):
        """ Get the accuracy of our prediction"""
        if self.predicted_enemy_action:
            self.total_predict += 1
            if (self.predicted_enemy_action == opponent_action):
                self.corrected_predict += 1
                # Keep Track of prediction accuracy
        if (self.total_predict):
            self.predict_accuracy = round(self.corrected_predict/self.total_predict,3)

    def update_next_enemy_action(self, predict_index):
        """update enemy's next action into player class"""
        # always greedy predict enemy
        if (self.GREEDY_PREDICT):
            self.predicted_enemy_action = self.opponent_action_score_list[0][1]  
        else:
            # hard coding, get Next Enemy Action without using probability
            if (len(self.opponent_action_score_list) > predict_index):
                predicted_enemy_action = self.opponent_action_score_list[predict_index][1]
            else:
                predicted_enemy_action = self.opponent_action_score_list[0][1]
        return predicted_enemy_action

    def draw_avoid_best_action(self, player_total_score_list, cur_snap):
        """Avoid Draw Situation, take another action without using already used indexes checked by default dict"""
        self.cur_snap_used_action_index[cur_snap] += 1
        next_index = self.cur_snap_used_action_index[cur_snap]
        if next_index<len(player_total_score_list):
            return player_total_score_list[next_index][1]
        return player_total_score_list[random.randint(0,12)][1]
        

    def getScoredActionList(self, whichPlayer, Enemy_Next_Action=None):
        """
        Get Sorted List Based on Scoring Function,
        Can Use to get Opponent's score list,
        return 4 score list:

        Total_score_list;
        Aggresive_Score_list;
        Defense_Score_list;
        Punishment_Score_list;
        State_Score_list

        """

        # Check if using on ourside or predicting enemy
        if (whichPlayer == "player"):
            side = self.side
            prev_state = State(copy(self.play_dict), copy(self.throws_left),
                                copy(self.enemy_throws_left), copy(side))
        else:
            if self.side == "upper":
                #Reverse throws_left and enemy_throws_left for enemy evaluation
                prev_state = State(copy(self.play_dict), copy(self.enemy_throws_left),
                                copy(self.throws_left), "lower")
            else:
                #Reverse throws_left and enemy_throws_left for enemy evaluation
                prev_state = State(copy(self.play_dict), copy(self.enemy_throws_left),
                                copy(self.throws_left), "upper")
            

        action_list = get_all_valid_action(whichPlayer, prev_state)
        next_state = prev_state
        # add enemy next action into state, but do not calculate elimination
        if Enemy_Next_Action:
            next_state = add_next_action_to_play_dict(prev_state, "opponent", Enemy_Next_Action)
            #eliminate_and_update_board(next_state, prev_state.target_dict)
            
        if ((self.ANALYSIS_MODE) and (whichPlayer == "player")):
            print("````````````````````````````````Enemy_Next_Action````````````````````````````````")
            print(Enemy_Next_Action)
        # Get Score List
        Total_score_list = []
        for action in action_list:
            scoring_dict = action_evaluation(whichPlayer, next_state, action)
            total_score = scoring_dict["total_score"]
            reward = scoring_dict["reward_list"]#reWard_list
            Total_score_list.append( (total_score, action, reward) )
        # Sort to choose highest score
        Total_score_list = sorted(Total_score_list, reverse=True)

        Total_score_list_with_prob = []
        for i in range(0,len(Total_score_list)):
            prob = calculate_normal_probability(i, self.opponent_score_array)
            Total_score_list_with_prob.append(tuple((Total_score_list[i][0], Total_score_list[i][1], prob, Total_score_list[i][2]))) 
            

        #print(whichPlayer+" Best Score List:")
        #print(Reward_list[0])
        return Total_score_list_with_prob


    def select_enemy_next_index(self):
        """select most likely enemy's action"""
        selected_index = 0
        array = self.opponent_score_array
        # Select The Score we want to use to evaluate enemy's action
        # Selecting Least Standard Deviation one
        if np.size(array)==1:
            selected_index = 0
        else:
            selected_mean = np.mean(array)
            selected_index = int(round(selected_mean))
        if (self.ANALYSIS_MODE):
            print("``````````````````````````````````````````")
            print("selected_enemy_index")
            print(selected_index)
            print("``````````````````````````````````````````")
        return selected_index


   
    
    # count enemy's choices index based on our function into dataframe
    def record_enemy_action_index(self, opponent_action):
        #iterate through all types of score
        score_array = self.opponent_score_array
        index_to_add = 0
        score_list = self.opponent_action_score_list
        
        for index in range(0, len(score_list)):
            cur_pair = self.opponent_action_score_list[index]
            if cur_pair[1] == opponent_action:
                # exclude potation random throw outlier, using mean value
                if self.EXCLUDE_THROW_DIST == True:
                    if cur_pair[1][0] in "THROW":
                        index = self.opponent_score_array.mean()
                        break
                break
        # not enough data, add mean value
        if (np.size(score_array)<30):
            index_to_add = index
        else:
            #Excluding Potential Outlier and add mean value
            if calculate_normal_probability(index, score_array) > (1-self.CONFIDENCE_LEVEL*5):
                index_to_add = index
            else:
                index_to_add = score_array.mean()
        # add to action array
        self.opponent_score_array = np.append(score_array, index)



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


def add_next_action_to_play_dict(state, player, action):
    """
    This function copy the previous state and add action on the new board and return the new
    state 
    """
    # copy the previous state
    new_state = deepcopy(state)

    if action[0] in "THROW":
        #If throw, add a symbol onto board
        symbol_type = action[1]
        location = action[2]
        new_state.play_dict[player][symbol_type].append(location)
        #reduce available throw times by 1
        if player == "opponent":
            new_state.enemy_throws_left -= 1
        else:
            new_state.throws_left -= 1
    else:
        move_from = action[1]
        symbol_type = get_symbol_by_location(player, new_state.play_dict, move_from)
        move_to = action[2]
        # move token from start to end, simply update play_dict

        # move the token by adding new position and remove old one
        new_state.play_dict[player][symbol_type].remove(move_from)
        new_state.play_dict[player][symbol_type].append(move_to)
    return new_state

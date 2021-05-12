from RL_base.util import Init_throw_range, add_action_to_play_dict, eliminate_and_update_board, calculate_normal_probability, get_symbol_by_location
from RL_base.action import get_all_valid_action
from RL_base.action_evaluation import action_evaluation
from RL_base.state import State
from RL_base.prediction import *
from copy import copy
from copy import deepcopy
import random
from RL_base.random_algorithms import refined_random_throw, random_throw, random_action, get_current_player_nodes_count
import csv
from RL_base.learning import temporal_difference_learning
import os
import numpy as np

import math
import pandas as pd
import matplotlib.pyplot as plt
import collections
from collections import defaultdict as dd



def predict_next_enemy_action(self, player_next_action = None):
    """after certain rounds, start to predict enemy's action based on our action"""
    if (self.game_round>self.IGNORE_ROUND):
    # Get sorted Action Evaluation List for Enemy's choice
        self.opponent_action_score_list = getScoredActionList(self, "opponent", player_next_action)
        self.predicted_enemy_action = update_next_enemy_action(self, self.opponent_action_score_list)   
        assert(self.predicted_enemy_action!=None)
        
    
def LearnEnemyStrategy(self, opponent_action):
    """Learn Enemy's Strategy by comparing the arresive/defensive score and get their suitable evaluation function"""
    # count enemy's choices index based on our function into array
    if (self.game_round > self.IGNORE_ROUND):
        #update accuracy
        update_accuracy_of_prediction(self, opponent_action)
        #iterative learning 
        i = 0
        while i < self.ITERATION:
            break_condition = False
            new_score_list = getScoredActionList(self, "opponent")
            predicted_enemy_action = update_next_enemy_action(self, new_score_list)  
            
            # Adjust enemy evaluation weight according to prediction, reduce the weight if less
            aggresive_diff = self.enemy_aggresive_action_score[opponent_action] - self.enemy_aggresive_action_score[predicted_enemy_action]
            defensive_diff = self.enemy_defensive_action_score[opponent_action] - self.enemy_defensive_action_score[predicted_enemy_action]
            # If actual action more aggresive-biased or defensive-biased, adjust their weights
            if aggresive_diff > 0:
                self.Enemy_Eval_Weight["aggresive"] += self.STEP_ATK_SCALE
                # Upper Limit Setup
                # if self.Enemy_Eval_Weight["aggresive"] > 100:
                #     self.Enemy_Eval_Weight["aggresive"] = 100
            # if enemy is less aggresive
            elif aggresive_diff < 0:
                self.Enemy_Eval_Weight["aggresive"] -= self.STEP_ATK_SCALE
            else:
                break_condition = True
            # if enemy is more defensive
            if defensive_diff > 0:
                self.Enemy_Eval_Weight["defensive"] += self.STEP_DEF_SCALE
                if self.Enemy_Eval_Weight["defensive"] < 0:
                    self.Enemy_Eval_Weight["defensive"] = 0.02
            elif defensive_diff < 0:
                # Lower Limit Setup
                self.Enemy_Eval_Weight["defensive"] -= self.STEP_DEF_SCALE
            else:
                # if cannot adjust defensive score or aggresive score, break the loop
                if break_condition:
                    break
            # Check if enemy prefers slides rather than throw 
            if predicted_enemy_action[0] in "THROW":
                # predict throw and enemy not throw
                if opponent_action[0] not in "THROW":
                    self.Enemy_Eval_Weight["prefer_throw"] -= self.STEP_THROW_RATE
                else:
                    self.Enemy_Eval_Weight["prefer_throw"] += self.STEP_THROW_RATE
            i+=1
                

def update_accuracy_of_prediction(self, opponent_action):
    """ Get the accuracy of our prediction"""
    if self.predicted_enemy_action:
        self.total_predict += 1
        if (self.predicted_enemy_action == opponent_action):
            self.corrected_predict += 1
            # Keep Track of prediction accuracy
    if (self.total_predict):
        self.predict_accuracy = round(self.corrected_predict/self.total_predict,3)

def update_next_enemy_action(self, score_list):
    """update enemy's next action into player class"""
    # always greedy predict enemy
    if (self.GREEDY_PREDICT):
        predicted_enemy_action = score_list[0][1]  
    else:
        # hard coding, get Next Enemy Action without using probability
        predicted_enemy_action = score_list[0][1]
    return predicted_enemy_action

def draw_avoid_best_action(self, player_total_score_list, cur_snap):
    """Avoid Draw Situation, take another action without Reaching previous state"""
    index = 0
    # Iterate through every action can take
    while(index < len(player_total_score_list)):
        next_action = player_total_score_list[index][1]
        # get next state if doing this action
        for symbol in ("rps"):
            player_cp = deepcopy(self)
            add_action_to_play_dict(player_cp, "player", next_action)
            nex_snap = player_cp._snap()
        #check if next state is already exists in our history, otherwise change to another action
        if (self.history[nex_snap]<2):
            return next_action
        index += 1
    return player_total_score_list[0][1]
    

def getScoredActionList(self, whichPlayer, Enemy_Next_Action=None):
    """
    Get Sorted List Based on Scoring Function,
    Can Use to get Opponent's score list,
    return 
    Total_score_list;
    """

    # Check if using on ourside or predicting enemy
    if (whichPlayer == "player"):
        opponent = "opponent"
        prev_state = State(copy(self.play_dict), copy(self.throws_left), copy(self.enemy_throws_left), copy(self.side))
    # if using on opponent, set state at enemy's view
    else:
        opponent = "player"
        if self.side == "upper":
            prev_state = State(copy(self.play_dict), copy(self.enemy_throws_left),copy(self.throws_left), "lower")
        else:
            prev_state = State(copy(self.play_dict), copy(self.enemy_throws_left),copy(self.throws_left), "upper")
        

    action_list = get_all_valid_action(whichPlayer, prev_state)
    random.shuffle(action_list)
    next_state = prev_state
    # add enemy next action into state, but do not calculate elimination
    if Enemy_Next_Action:
        next_state = add_next_action_to_play_dict(prev_state, opponent, Enemy_Next_Action)
        #eliminate_and_update_board(next_state, prev_state.target_dict)
        
    # Get Score List
    Total_score_list = []
    for action in action_list:
        scoring_dict = action_evaluation(self, whichPlayer, next_state, action)
        total_score = scoring_dict["total_score"]
        reward = scoring_dict["reward_list"]#reWard_list
        Total_score_list.append( (total_score, action, reward) )
        # Aggresive Score dictionary
        agg_score = scoring_dict["aggresive_score"]
        self.enemy_aggresive_action_score[action] = agg_score
        # Defensive Score dictionary
        def_score = scoring_dict["defense_score"]
        self.enemy_defensive_action_score[action] = def_score
        
    # Sort to choose highest score
    Total_score_list = sorted(Total_score_list, reverse=True)
    return Total_score_list




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

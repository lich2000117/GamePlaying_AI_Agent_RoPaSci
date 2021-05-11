from RL.util import Init_throw_range, add_action_to_play_dict, eliminate_and_update_board, calculate_normal_probability, get_symbol_by_location
from RL.action import get_all_valid_action
from RL.action_evaluation import action_evaluation
from RL.state import State
from copy import copy
from copy import deepcopy
import random
from RL.random_algorithms import refined_random_throw, random_throw, random_action, get_current_player_nodes_count
import csv
from RL.learning import temporal_difference_learning
import os
import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
import collections
from collections import defaultdict as dd

def getScoredActionList(playerClass, whichPlayer, Enemy_Next_Action=None):
    """
    Get Sorted List Based on Scoring Function,
    Can Use to get Opponent's score list,
    return one list: Total_score_list
    """
    # Get Enemy Action's Probability and return the mean index using "Total Score"
    # Check if using on ourside or predicting enemy
    if (whichPlayer == "player"):
        side = playerClass.side
        prev_state = State(copy(playerClass.play_dict), copy(playerClass.throws_left),
                            copy(playerClass.enemy_throws_left), copy(side))
    else:
        if playerClass.side == "upper":
            #Reverse throws_left and enemy_throws_left for enemy evaluation
            prev_state = State(copy(playerClass.play_dict), copy(playerClass.enemy_throws_left),
                            copy(playerClass.throws_left), "lower")
        else:
            #Reverse throws_left and enemy_throws_left for enemy evaluation
            prev_state = State(copy(playerClass.play_dict), copy(playerClass.enemy_throws_left),
                            copy(playerClass.throws_left), "upper")
        

    action_list = get_all_valid_action(whichPlayer, prev_state)
    next_state = prev_state
    # add enemy next action into state, but do not calculate elimination
    if Enemy_Next_Action:
        next_state = add_next_action_to_play_dict(prev_state, "opponent", Enemy_Next_Action)
        #eliminate_and_update_board(next_state, prev_state.target_dict)
        
    if ((playerClass.ANALYSIS_MODE) and (whichPlayer == "player")):
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
        prob = calculate_normal_probability(i, playerClass.opponent_score_array)
        Total_score_list_with_prob.append(tuple((Total_score_list[i][0], Total_score_list[i][1], prob, Total_score_list[i][2]))) 
        
    return Total_score_list_with_prob


def update_accuracy_of_prediction(playerClass, opponent_action):
    """ Get the accuracy of our prediction"""
    if playerClass.predicted_enemy_action:
        playerClass.total_predict += 1
        if (playerClass.predicted_enemy_action == opponent_action):
            playerClass.corrected_predict += 1
            # Keep Track of prediction accuracy
    if (playerClass.total_predict):
        playerClass.predict_accuracy = round(playerClass.corrected_predict/playerClass.total_predict,3)


def update_next_enemy_action(playerClass, predict_index):
    """update enemy's next action into player class"""
    # always greedy predict enemy
    if (playerClass.GREEDY_PREDICT):
        playerClass.predicted_enemy_action = playerClass.opponent_action_score_list[0][1]  
    else:
        # hard coding, get Next Enemy Action without using probability
        if (len(playerClass.opponent_action_score_list) > predict_index):
            predicted_enemy_action = playerClass.opponent_action_score_list[predict_index][1]
        else:
            predicted_enemy_action = playerClass.opponent_action_score_list[0][1]
    return predicted_enemy_action


def draw_avoid_best_action(playerClass, player_total_score_list, cur_snap):
    """Avoid Draw Situation, take another action without using already used indexes checked by default dict"""
    playerClass.cur_snap_used_action_index[cur_snap] += 1
    next_index = playerClass.cur_snap_used_action_index[cur_snap]
    if next_index<len(player_total_score_list):
        return player_total_score_list[next_index][1]
    return player_total_score_list[random.randint(0,12)][1]
    

def select_enemy_next_index(playerClass):
    """select most likely enemy's action"""
    selected_index = 0
    array = playerClass.opponent_score_array
    # Select The Score we want to use to evaluate enemy's action
    # Selecting Least Standard Deviation one
    if np.size(array)==1:
        selected_index = 0
    else:
        selected_mean = np.mean(array)
        selected_index = int(round(selected_mean))
    if (playerClass.ANALYSIS_MODE):
        print("``````````````````````````````````````````")
        print("selected_enemy_index")
        print(selected_index)
        print("``````````````````````````````````````````")
    return selected_index



# count enemy's choices index based on our function into dataframe
def record_enemy_action_index(playerClass, opponent_action):
    #iterate through all types of score
    score_array = playerClass.opponent_score_array
    index_to_add = 0
    score_list = playerClass.opponent_action_score_list
    
    for index in range(0, len(score_list)):
        cur_pair = playerClass.opponent_action_score_list[index]
        if cur_pair[1] == opponent_action:
            # exclude potation random throw outlier, using mean value
            if playerClass.EXCLUDE_THROW_DIST == True:
                if cur_pair[1][0] in "THROW":
                    index = playerClass.opponent_score_array.mean()
                    break
            break
    # not enough data, add mean value
    if (np.size(score_array)<30):
        index_to_add = index
    else:
        #Excluding Potential Outlier and add mean value
        if calculate_normal_probability(index, score_array) > (1-playerClass.CONFIDENCE_LEVEL*5):
            index_to_add = index
        else:
            index_to_add = score_array.mean()
    # add to action array
    playerClass.opponent_score_array = np.append(score_array, index)


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
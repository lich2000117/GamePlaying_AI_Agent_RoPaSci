import numpy as np
from RL_train.state import State, isGameEnded
from RL_train.util import get_symbol_by_location, closest_one, least_distance
from RL_train.action import get_all_valid_action
from math import tanh

import os
import csv

def state_evaluation(state, txt = False):

    WINNING_REWARD = 300
    DRAW_REWARD = -100
    w = []
    # state is in the form of (play_dict, player's throw left, opponnet's throw left, player's side)
    # isGameEnded(state) returns (True, "Winner") or (True, "Loser") or (False, "Unknown")
    if isGameEnded(state)[0]:
        # if true, return the utility of the state, 1 for victory, 0 for lose
        if isGameEnded(state)[1] == "Winner":
            return WINNING_REWARD
        elif isGameEnded(state)[1] == "Draw":
            return DRAW_REWARD
        else:
            return -WINNING_REWARD
    else:
        # if false, do evaluation of the state, and return the state_score
        # if the file is empty, use the initial parameter
        if os.stat("RL_train/weights.csv").st_size == 0:
                w = [10, 5, -5, 1, -1, 2, 3, -2, -3, 5, -2]
        else:
            with open("RL_train/weights.csv") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                row = next(csv_reader)
                # print("csv: ", row)
                for num in row:
                    w.append(float(num))

        feature_array = []                                   # initial parameter
        feature_array.append(board_count(state))                    #1 10
        feature_array.append(enemy_token_in_danger(state))          #2 5
        feature_array.append(token_in_danger(state))                #3 -5
        feature_array.append(token_on_board(state))                 #4 1
        feature_array.append(enemy_token_on_board(state))           #5 -1
        feature_array.append(mean_distance_to_attack(state))        #6 -2
        feature_array.append(min_distance_to_attack(state))         #7 3
        feature_array.append(mean_distance_to_defense(state))       #8 5  
        feature_array.append(min_distance_to_defense(state))        #9 -3
        feature_array.append(num_throw(state))                      #10 5
        feature_array.append(support_distance(state))               #11 -2

        state_value = 0
        if txt == True:
            print("w:", w)
            print("feature array: ", feature_array)
        for i in range(0, len(w)):
            state_value += feature_array[i] * w[i]
        
        if txt == True:
            print(state_value)
        return state_value
    

def board_count(state):
    """this function is used to count how many more tokens we have than our opponent"""

    count = state.throws_left - state.enemy_throws_left
    # with respect to num of token 'r'
    count += len(state.play_dict['player']['r']) - len(state.play_dict['opponent']['r'])

    # with respect to num of token 'p'
    count += len(state.play_dict['player']['p']) - len(state.play_dict['opponent']['p'])

    # with respect to num of token 's'
    count += len(state.play_dict['player']['s']) - len(state.play_dict['opponent']['s'])
    return count


def token_on_board(state):
    count = 0

    # add number of 'r' on the board
    count += len(state.play_dict["player"]['r'])
    # add number of 'p' on the board
    count += len(state.play_dict["player"]['p'])
    # add number of 's' on the board
    count += len(state.play_dict["player"]['s'])

    return count


def enemy_token_on_board(state):
    count = 0

    # add number of 'r' on the board
    count += len(state.play_dict["opponent"]['r'])
    # add number of 'p' on the board
    count += len(state.play_dict["opponent"]['p'])
    # add number of 's' on the board
    count += len(state.play_dict["opponent"]['s'])

    return count


def mean_distance_to_attack(state):
    player_token_list = [item for sublist in state.play_dict["player"].values() for item in sublist]
    target_dict = {"r":"s", "s":"p", "p":"r"}
    sum_distance = 0
    count = 0

    for token_pos in player_token_list:
        token_type = get_symbol_by_location("player", state.play_dict, token_pos)
        target_type = target_dict[token_type]
        # a list of token pos that we can eat
        target_list = state.play_dict["opponent"][target_type]
        if target_list:
            sub_count = 0
            sub_sum_distance = 0
            for target_pos in target_list:
                sub_sum_distance += least_distance(token_pos, target_pos)
                sub_count += 1
            sum_distance += sub_sum_distance / sub_count
            count += 1
    if count:
        return sum_distance/count
    else:
        return 0


def min_distance_to_attack(state):
    player_token_list = [item for sublist in state.play_dict["player"].values() for item in sublist]
    target_dict = {"r":"s", "s":"p", "p":"r"}
    min_distance = 66 # just set an arbitrary initial number

    for token_pos in player_token_list:
        token_type = get_symbol_by_location("player", state.play_dict, token_pos)
        target_type = target_dict[token_type]
        target_list = state.play_dict["opponent"][target_type]
        # a list of token pos that we can eat
        if target_list:
            # find the the token that is closest to our token
            target_pos = closest_one(token_pos, target_list)
            if least_distance(target_pos, token_pos) < min_distance:
                min_distance = least_distance(target_pos, token_pos)
    if min_distance == 66:
        return 0
    else:
        return min_distance


def mean_distance_to_defense(state):
    player_token_list = [item for sublist in state.play_dict["player"].values() for item in sublist]
    target_dict = {"r":"s", "s":"p", "p":"r"}
    sum_distance = 0
    count = 0

    for token_pos in player_token_list:
        token_type = get_symbol_by_location("player", state.play_dict, token_pos)
        counter_type = target_dict[target_dict[token_type]]
        # a list of token pos that we can eat
        counter_list = state.play_dict["opponent"][counter_type]
        if counter_list:
            sub_count = 0
            sub_sum_distance = 0
            for counter_pos in counter_list:
                sub_sum_distance += least_distance(token_pos, counter_pos)
                sub_count += 1
            sum_distance += sub_sum_distance / sub_count
            count += 1
    if count:
        return sum_distance/count
    else:
        return 0


def min_distance_to_defense(state):
    player_token_list = [item for sublist in state.play_dict["player"].values() for item in sublist]
    target_dict = {"r":"s", "s":"p", "p":"r"}
    min_distance = 66 # just set an arbitrary initial number

    for token_pos in player_token_list:
        token_type = get_symbol_by_location("player", state.play_dict, token_pos)
        counter_type = target_dict[target_dict[token_type]]
        # a list of token pos that we can eat
        counter_list = state.play_dict["opponent"][counter_type]
        if counter_list:
            # find the the token that is closest to our token
            counter_pos = closest_one(token_pos, counter_list)
            if least_distance(counter_pos, token_pos) < min_distance:
                min_distance = least_distance(counter_pos, token_pos)
    if min_distance == 66:
        return 0
    else:
        return min_distance
    

def enemy_token_in_danger(state):
    action_list = get_all_valid_action(state, "player")
    # all_valid_action = [("SLIDE",start, end), ("SWING",start, end), ("THROW",symbol_type, point)...]
    count = 0
    target_dict = {"r":"s", "s":"p", "p":"r"}
    for action in action_list:
        if action[0] == "THROW":
            token_type = action[1]
            target_type = target_dict[token_type]
            if action[2] in state.play_dict["opponent"][target_type]:
                count += 1
        elif action[0] == "SLIDE" or action[0] == "SWING":
            token_type = get_symbol_by_location("player", state.play_dict, action[1])
            target_type = target_dict[token_type]
            if action[2] in state.play_dict["opponent"][target_type]:
                count += 1
    return count


def token_in_danger(state):
    action_list = get_all_valid_action(state, "opponent")
    # all_valid_action = [("SLIDE",start, end), ("SWING",start, end), ("THROW",symbol_type, point)...]
    count = 0
    target_dict = {"r":"s", "s":"p", "p":"r"}
    for action in action_list:
        if action[0] == "THROW":
            token_type = action[1]
            target_type = target_dict[token_type]
            if action[2] in state.play_dict["player"][target_type]:
                count += 1
        elif action[0] == "SLIDE" or action[0] == "SWING":
            token_type = get_symbol_by_location("opponent", state.play_dict, action[1])
            target_type = target_dict[token_type]
            if action[2] in state.play_dict["player"][target_type]:
                count += 1
    return count


def num_throw(state):
    return state.throws_left


def support_distance(state):
    sum_distance = 0
    target_dict = {"r":"s", "s":"p", "p":"r"}
    for token_type in ['r', 'p', 's']:
        for token_pos in state.play_dict["player"][token_type]:
            sup_type = target_dict[token_type]
            sup_list = state.play_dict["player"][sup_type]
            if sup_list:
                sup_pos = closest_one(token_pos, sup_list)
                sum_distance += least_distance(sup_pos, token_pos)
    return sum_distance




        
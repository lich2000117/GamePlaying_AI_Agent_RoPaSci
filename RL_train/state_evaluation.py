import numpy as np
from RL.state import State, isGameEnded
from RL.util import get_symbol_by_location, closest_one, least_distance
from math import tanh
import os
import csv

def state_evaluation(state, txt = False):

    WINNING_REWARD = 1
    DRAW_REWARD = -0.1
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
                w = [10, 5, -5, 1, -1, 2, 3, -2, -3]
        else:
            with open("RL_train/weights.csv") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                row = next(csv_reader)
                # print("csv: ", row)
                for num in row:
                    w.append(float(num))

        feature_array = []                                   # initial parameter
        feature_array.append(board_count(state))                    # 10
        feature_array.append(hostile_token_in_throw_range(state))   # 5
        feature_array.append(token_in_enemy_throw_range(state))     # -5
        feature_array.append(token_on_board(state))                 # 1
        feature_array.append(enemy_token_on_board(state))           # -1
        feature_array.append(mean_distance_to_attack(state))        # -2
        feature_array.append(min_distance_to_attack(state))         # 3
        feature_array.append(mean_distance_to_defense(state))       # 5  
        feature_array.append(min_distance_to_defense(state))        # -3

        state_value = 0
        if txt == True:
            print("w:", w)
            print("feature array: ", feature_array)
        for i in range(0, len(w)):
            state_value += feature_array[i] * w[i]
        
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
    


def hostile_token_in_throw_range(state):
    value = 0
    total_throws = 9
    have_thrown = total_throws - state.throws_left
    # got all the positions of tokens of one players in a list
    # [(r1,q1),(r2,q2),(r3,q3)...(rn,qn)] 
    throw_range = tuple()
    enemy_token_list = [item for sublist in state.play_dict["opponent"].values() for item in sublist]
    if state.side == 'upper':
        throw_range = range(4, 3-have_thrown, -1)
        for token in enemy_token_list:
            if token[0] in throw_range:
                value += 1
    else:
        throw_range = range(-4, -3+have_thrown, +1)
        for token in enemy_token_list:
            if token[0] in throw_range:
                value += 1
    return value - 1


def token_in_enemy_throw_range(state):
    value = 0
    total_throws = 9
    enemy_throw_range = tuple()
    enemy_have_thrown = total_throws - state.enemy_throws_left
    # got all the positions of tokens of one players in a list
    # [(r1,q1),(r2,q2),(r3,q3)...(rn,qn)] 
    player_token_list = [item for sublist in state.play_dict["player"].values() for item in sublist]
    if state.side == 'upper':
        enemy_throw_range = range(-4, -3+enemy_have_thrown , +1)
        for token in player_token_list:
            if token[0] in enemy_throw_range:
                value += 1
    else:
        enemy_throw_range = range(4, 3-enemy_have_thrown, -1)
        for token in player_token_list:
            if token[0] in enemy_throw_range:
                value += 1
    return value - 1



        
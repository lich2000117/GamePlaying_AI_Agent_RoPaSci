import numpy as np
from RL.state import State, isGameEnded
import _pickle as cPickle
from math import tanh
import os
import csv

def state_evaluation(state):

    WINNING_REWARD = 999
    DRAW_REWARD = -100

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
        if os.stat("RL/weights.csv").st_size == 0:
                w = [10, 5, -5]
        else:
            with open("RL/weights.csv") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                row = next(csv_reader)
                w = []
                for num in row:
                    w.append(float(num))
        # with open(r"weights.pickle", "wb") as output_file:
        #     cPickle.dump(w, output_file)
        # pickle_file will be closed at this point, preventing your from accessing it any further
        feature_array = np.array([])
        np.append(feature_array, board_count(state))
        np.append(feature_array, hostile_token_in_throw_range(state))
        np.append(feature_array, token_in_enemy_throw_range(state))

        
        W = np.array([])
        for i in range(0, len(feature_array)):
            np.append(W, w[i])
        
        return feature_array.dot(W)
    

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



        
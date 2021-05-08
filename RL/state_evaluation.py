import numpy as np
from RL.state import State

def state_evaluation(state):
    # state is in the form of (play_dict, player's throw left, opponnet's throw left, player's side)
    feature_array = np.array([])
    np.append(feature_array, board_count(state))
    np.append(feature_array, hostile_token_in_throw_range(state))
    np.append(feature_array, token_in_enemy_throw_range(state))

    w = [10, 5, -5]
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
        
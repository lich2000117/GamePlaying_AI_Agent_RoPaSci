def state_evaluation(state):
    # state is in the form of (play_dict, player's throw left, opponnet's throw left, player's side)
    feature_list = []
    feature_list.append(board_count(state))
    
    

def board_count(state):
    """this function is used to count how many more tokens we have than our opponent"""

    count = state[1] - state[2]
    # with respect to num of token 'r'
    count += len(state[0]['player']['r']) - len(state[0]['opponent']['r'])

    # with respect to num of token 'p'
    count += len(state[0]['player']['p']) - len(state[0]['opponent']['p'])

    # with respect to num of token 's'
    count += len(state[0]['player']['s']) - len(state[0]['opponent']['s'])
    return count



def hostile_token_in_throw_range(state):
    value = 0
    total_throws = 9
    have_thrown = total_throws - state[1]
    # got all the positions of tokens of one players in a list
    # [(r1,q1),(r2,q2),(r3,q3)...(rn,qn)] 
    enemy_token_list = [item for sublist in state[0]["opponent"].values() for item in sublist]
    if state[3] == 'upper':
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
    enemy_have_thrown = total_throws - state[2]
    # got all the positions of tokens of one players in a list
    # [(r1,q1),(r2,q2),(r3,q3)...(rn,qn)] 
    player_token_list = [item for sublist in state[0]["player"].values() for item in sublist]
    if state[3] == 'upper':
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
        
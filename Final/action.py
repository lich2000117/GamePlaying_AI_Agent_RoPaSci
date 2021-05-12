# def get_all_valid_action(state, whichPlayer= 'player', Throw = True):
#     # state =  (play_dict, player's throws left, opponnet's throws left, player's side)
from Final.util import action_throw, move_action, least_distance, get_six_adj_nodes, is_point_valid

def get_all_valid_action(player, state):
    # state =  (play_dict, player's throws left, opponnet's throws left, player's side)
    # all_valid_action = [("SLIDE",start, end), ("SWING",start, end), ("THROW",symbol_type, point)...]
    all_valid_action = []
    throw_list = []
    move_list = []

    # get all the slide and swing action 
    move_list = get_all_valid_move(player, state)
    all_valid_action += move_list

    # get all the throw action
    
    if state.throws_left > 0:
        throw_list = get_all_valid_throw(state)
        if throw_list:
            for throw in throw_list:
                for type in ['r', 'p', 's']:
                    throw_action = action_throw(type, throw)
                    all_valid_action.append(throw_action)

    return all_valid_action


def get_all_valid_throw(state):
    """This function is used to generate all the possible throw"""
    have_thrown = 9 - state.throws_left
    #print("Now I have ", state.throws_left, "times of throw")
    # print("I have thrown ", have_thrown, "times")
    #print(state.side)
    throw_list = []
    if state.side == "upper":
        for row in range(4, 3 - have_thrown, -1):
            for col in range(-4, 5):
                if abs(row + col) <= 4:
                    throw_list.append((row, col))
        return throw_list
    elif state.side == "lower":
        for row in range(-4, -3 + have_thrown):
            for col in range(-4, 5):
                if abs(row + col) <= 4:
                    throw_list.append((row, col))
        return throw_list
    else:
        print("Cannont throw")
        return []


def get_all_valid_move(player, state):

    ## all_valid_move = [("SLIDE",start, end), ("SWING",start, end)...]
    all_valid_move = []

    for type in state.play_dict[player].keys():
        for token_pos in state.play_dict[player][type]:
            # generate valid move for each token
            move_token = (token_pos, type)
            valid_move_list = []
            move_list = []

            # add six adjancent nodes 
            adj_nodes = get_six_adj_nodes(move_token[0]) 
            move_list += adj_nodes

            # check whether each token can swing
            swing_nodes = set()
            for node in adj_nodes:
                player_token_list = [item for sublist in state.play_dict[player].values() for item in sublist]       
                if node in player_token_list:
                    for swing_node in get_six_adj_nodes(node):
                        if least_distance(swing_node, move_token[0]) == 2:
                            swing_nodes.add(swing_node)
            move_list += list(swing_nodes)

            # check the validity of each move(not off the grid)
            for move in move_list:
                if is_point_valid(move):
                    valid_move_list.append(move)

            # format the valid move 
            for move in valid_move_list:
                all_valid_move.append(move_action(move_token[0], move))

    return all_valid_move
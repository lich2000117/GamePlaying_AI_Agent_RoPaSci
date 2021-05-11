from RL_train.state import State
from RL_train.action import get_all_valid_action
from copy import copy, deepcopy
from RL_train.state_evaluation import state_evaluation
from RL_train.util import get_symbol_by_location
def defensive_action_evaluation(state, action):
    # add our action into the board and get a new state
    new_state = add_action_to_play_dict(state, "player", action)
    action_list = get_all_valid_action(new_state, "opponent")
    min_score = 999
    for op_action in action_list:
        second_state = add_action_to_play_dict(state, "opponent", op_action)
        state_score = state_evaluation(second_state)
        if state_score < min_score:
            min_score = state_score
    return min_score
















#______________________________________________ function used ______________________________________________ #
def add_action_to_play_dict(state, player, action):
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


# If two symbols place together, determine what to do with play_dict
def eliminate_and_update_board(state, target_dict):
    # target_dict = {"r":"s", "s":"p", "p":"r"}
    # first find tokens that need to be eliminated
    for symbol_type, target_symbol in target_dict.items():
        #list of all locations of this type
        list_locations_of_type = state.play_dict["player"][symbol_type]\
                                + state.play_dict["opponent"][symbol_type]
        #Iterate Through the locations and remove its target_symbol
        for position in reversed(list_locations_of_type):
            #  get what types are at location, 
            types_at_location = set(get_symbol_by_location("player", state.play_dict, position)\
                    + get_symbol_by_location("opponent", state.play_dict, position))
            # if three types all occurs, remove all of the symbols of all types at that location
            if (len(types_at_location) == 3):
                remove_all_type_symbols_at_location(state, "s", position)
                remove_all_type_symbols_at_location(state, "r", position)
                remove_all_type_symbols_at_location(state, "p", position)
            remove_all_type_symbols_at_location(state, target_symbol, position)


# Remove all symbols of that type at that location
def remove_all_type_symbols_at_location(state, removetype, location):
    state.play_dict["player"][removetype] = \
                    list(filter(lambda a: a != location, state.play_dict["player"][removetype]))
    state.play_dict["opponent"][removetype] = \
                    list(filter(lambda a: a != location, state.play_dict["opponent"][removetype]))
        
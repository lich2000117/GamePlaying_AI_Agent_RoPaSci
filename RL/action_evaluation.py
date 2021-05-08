from RL.util import get_symbol_by_location, closest_one, least_distance
from RL.state_evaluation import state_evaluation
import copy

def action_evaluation(state, action):
    # state = (play_dict, player's throw left, opponnet's throw left, player's side)
    # action = ("SLIDE",start, end) or ("SWING",start, end) or ("THROW",symbol_type, point)
    """this function returns a score that equals
            Score = value_of_action + value_of_postAction_state"""
    action_score = 0
    state_score = 0
    ################ chasing action reward parameter ###################
    CHASING_REWARD = 5

    ################ fleeing action reward parameter ###################
    FLEE_REWARD = 3
    SCALE = 2
    ALERT_DISTANCE = 3

    ################ approaching action reward parameter ###################
    APPROACHING_REWARD = 3

    ################ throw-elimination action reward parameter ###################
    THROW_ELIMINATION_REWARD = 10

    target_dict = {'r':'s', 'p':'r', 's':'p'}
    # evaluation of action
    if action[0] == "THROW":
        # ("THROW", symbol_type, point)
        # reward throw action that try to eliminate hostile tokens with high possibility
        # high possibility means there multiple hostile tokens within the throw range
        # or there are hostile tokens being chased
        throw_range = get_throw_range(state)[0]
        enemy_token_list = [item for sublist in state[0]["opponent"].values() for item in sublist]
        player_token_list = [item for sublist in state[0]["player"].values() for item in sublist]
        count = 0

        # count how many enemy tokens are in danger
        # token_in_danger = #token within throw range + #token being chased outside throw range

        # first count how many hostile tokens are in our throw range 
        for enemy_token_pos in enemy_token_list:
            if enemy_token_pos[0] in throw_range:
                count += 1
        
        # then count how many enemy tokens are being chased

        # list below is used to store pos of tokens within throw range and also being chased
        # mark the tokens as they are not good throw options
        enemy_token_chased_list = []

        for enemy_token_pos in enemy_token_list:
            enemy_token_type = get_symbol_by_location('opponent', state[0], enemy_token_pos)
            counter_token_type = target_dict[target_dict[enemy_token_type]]
            counter_token_list = state[0]['player'][counter_token_type]
            for counter_token_pos in counter_token_list:
                if least_distance(counter_token_pos, enemy_token_pos) == 1:
                    if enemy_token_pos[0] not in throw_range:
                        count += 1
                    else:
                        enemy_token_chased_list.append(enemy_token_pos)

                    # break to avoid multiple count
                    break

        # next check out whether this throw action is either
        # 1. throw on hostile token    2. throw on friendly token   3.throw on empty grid
        target_type = target_dict[action[1]]
        counter_type = target_dict[target_dict[action[1]]]
        # throw action1: throw on hostile token
        if action[2] in enemy_token_list:
            # reward possible direct throw elimination
            if action[2] in state[0]["opponent"][target_type]:
                # if hostile token is already in danger, no need to use throw
                if action[2] not in enemy_token_chased_list:
                    action_score += THROW_ELIMINATION_REWARD * (1 - 1/count)
            # punish being eliminated
            elif action[2] in state[0]["opponent"][counter_type]:
                action_score -= THROW_ELIMINATION_REWARD
    

        # throw action2: throw on friendly token
        elif action[2] in player_token_list:
            # punish eliminating friendly token
            if action[2] in state[0]["player"][target_type]:
                action_score -= THROW_ELIMINATION_REWARD 
            # punish being eliminated
            elif action[2] in state[0]["opponent"][counter_type]:
                action_score -= THROW_ELIMINATION_REWARD


        # throw action3: throw on empty grid
        else:
            action_score += 0

        
        

    elif action[0] == "SLIDE" or action[0] == "SWING":
        token_type = get_symbol_by_location("player", state[0], action[1])
        # Next is a few of lists that store position information of 
        # hostile_token, friendly_token and target_token
        # for example, if my token is 'r'
        # then hostile token will be 'p', because 'p' eats 'r'
        # friendly token will be 's', because 's' counters 'p'
        # target token will be 's', because 'r' eliminates 's'
        hostile_token_type = target_dict[target_dict[token_type]]
        hostile_token_list = state[0]["opponent"][hostile_token_type] # may need to consider draw situation
        friendly_token_type = target_dict[token_type]
        friendly_tokens_list = state[0]['player'][target_dict[token_type]] 
        target_token_type = target_dict[token_type]
        target_token_list = state[0]['opponent'][target_token_type]

        # reward action1: try to eliminate hostile token
        if action[2] in state[0]["opponent"][target_dict[token_type]]:
            action_score += CHASING_REWARD
        

        # reward action2: flee from hostile token
        if hostile_token_list:
            hostile_token = (closest_one(action[1], hostile_token_list), hostile_token_type)
            # only reward flee action when hostile token is close enough
            if least_distance(hostile_token[0], action[1]) <= ALERT_DISTANCE:
                # reward action that make the distance larger
                if least_distance(hostile_token[0], action[1]) < least_distance(hostile_token[0], action[2]):
                    # reward swing action more than slide action
                    diff = least_distance(hostile_token[0], action[2]) - least_distance(hostile_token[0], action[1])
                    if diff == 2:
                        action_score += FLEE_REWARD
                    elif diff == 1:
                        action_score += FLEE_REWARD - SCALE
                    elif diff == 0:
                        action_score += 0
                    else:
                        action_score -= FLEE_REWARD + SCALE

                # when being chased
                # reward flee action that run towards friendly tokens for possible swing to get rid of chasing token
                if friendly_tokens_list:
                    friendly_token = (closest_one(action[1], friendly_tokens_list), friendly_token_type)
                    diff = least_distance(friendly_token[0], action[1]) - least_distance(friendly_token[0], action[2])
                    if diff == 1:
                        action_score += FLEE_REWARD - SCALE
                    elif diff == 2:
                        action_score += FLEE_REWARD
        

        # reward action3: approaching to opponent's tokens
        approaching_score = 0
        if target_token_list:
            for token_pos in target_token_list:
                target_token = (token_pos, target_token_type)
                pre_distance = least_distance(action[1], target_token[0])
                post_distance = least_distance(action[2], target_token[0])

                # reward swing more than slide
                diff = pre_distance - post_distance
                if diff == 2:
                    approaching_score += SCALE*0.5

                # reward more if it is close, pose more danger to opponent
                if post_distance > 2:
                    approaching_score += APPROACHING_REWARD - SCALE
                elif post_distance == 2:
                    approaching_score += APPROACHING_REWARD
                elif post_distance == 1:
                    approaching_score += APPROACHING_REWARD + SCALE

        action_score += approaching_score

    # create new state and update with the action for further evaluation
    new_state = add_action_to_play_dict(state, "player", action)
    eliminate_and_update_board(new_state, target_dict)

    # evaluation of post-action state
    state_score = state_evaluation(new_state)


    return action_score + state_score






#_____________________________________________________________________________________
def get_throw_range(state):
    """This function is used to get the throw range of both player, it returns a tuple
        which is (player_throw_range, opponent_throw_range)
    """
    have_thrown = 9 - state.throw_left
    enemy_have_thrown = 9 - state.enemy_throw_left
    player_throw_range = range()
    enemy_throw_range = range()
    if state.side == "upper":
        player_throw_range = range(4, 3 - have_thrown, -1)
        enemy_throw_range = range(-4, -3 + enemy_have_thrown, +1) 
        return (player_throw_range, enemy_throw_range) 
    elif state.side == "lower":
        player_throw_range = range(-4, -3 + have_thrown, +1)
        enemy_throw_range = range(4, 3 - enemy_have_thrown, -1)
        return (player_throw_range, enemy_throw_range) 
    else:
        exit()


def add_action_to_play_dict(state, player, action):
    """
    This function copy the previous state and add action on the new board and return the new
    state 
    """
    player_throw_left = state[1]
    enemy_throw_left = state[2]
    new_play_dict = state[0]
    player_side = state[3]
    new_state = [new_play_dict, player_throw_left, enemy_throw_left, player_side]
    if action[0] in "THROW":
        #If throw, add a symbol onto board
        symbol_type = action[1]
        location = action[2]
        new_state[0][player][symbol_type].append(location)
        #reduce available throw times by 1
        if player == "opponent":
            new_state[2] -= 1
        else:
            new_state[1] -= 1
    else:
        move_from = action[1]
        symbol_type = get_symbol_by_location(player, new_state[0], move_from)
        move_to = action[2]
        # move token from start to end, simply update play_dict

        # move the token by adding new position and remove old one
        new_state[0][player][symbol_type].remove(move_from)
        new_state[0][player][symbol_type].append(move_to)
    return new_state


# If two symbols place together, determine what to do with play_dict
def eliminate_and_update_board(state, target_dict):
    # target_dict = {"r":"s", "s":"p", "p":"r"}
    # first find tokens that need to be eliminated
    for symbol_type, target_symbol in target_dict.items():
        #list of all locations of this type
        list_locations_of_type = state[0]["player"][symbol_type]\
                                + state[0]["opponent"][symbol_type]
        #Iterate Through the locations and remove its target_symbol
        for position in reversed(list_locations_of_type):
            #  get what types are at location, 
            types_at_location = set(get_symbol_by_location("player", state[0], position)\
                    + get_symbol_by_location("opponent", state[0], position))
            # if three types all occurs, remove all of the symbols of all types at that location
            if (len(types_at_location) == 3):
                remove_all_type_symbols_at_location(state, "s", position)
                remove_all_type_symbols_at_location(state, "r", position)
                remove_all_type_symbols_at_location(state, "p", position)
            remove_all_type_symbols_at_location(state, target_symbol, position)


# Remove all symbols of that type at that location
def remove_all_type_symbols_at_location(state, removetype, location):
    state[0]["player"][removetype] = \
                    list(filter(lambda a: a != location, state[0]["player"][removetype]))
    state[0]["opponent"][removetype] = \
                    list(filter(lambda a: a != location, state[0]["opponent"][removetype]))
        






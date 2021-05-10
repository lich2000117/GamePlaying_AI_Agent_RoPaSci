from RL.state_evaluation import state_evaluation
from copy import deepcopy
from RL.state import State
from RL.util import get_symbol_by_location, least_distance, closest_one, get_current_player_nodes_count

def action_evaluation(whichPlayer,state, action):
    # state = (play_dict, player's throw left, opponnet's throw left, player's side)
    # action = ("SLIDE",start, end) or ("SWING",start, end) or ("THROW",symbol_type, point)
    """this function returns a score that equals
            Score = value_of_action + value_of_postAction_state"""

    AGGRESIVE_WEIGHT = 1
    DEFENSIVE_WEIGHT = 1
    PUNISHMENT_WEIGHT = 1


    
    aggresive_score = 0
    defense_score = 0
    punishment_score = 0
    state_score = 0

    reward_list = []
    ################ chasing action reward parameter ###################
    CHASING_REWARD = 5
    ELIMINATION_REWARD = 10

    ################ fleeing action reward parameter ###################
    FLEE_REWARD = 7
    SCALE = 2
    ALERT_DISTANCE = 4

    ################ approaching action reward parameter ###################
    APPROACHING_REWARD = 3

    ################ avoid danger action reward parameter ###################
    AVOID_DANGER_REWARD = 5

    ################ throw-elimination action reward parameter ###################
    THROW_ELIMINATION_REWARD = 5
    THROW_DEFENSE_REWARD = 2   #throw on least have symbol
    THROW_ATTACK_REWARD = 2


    # Check the evaluation is used on which side
    if whichPlayer == "player":
        ourPlayer = "player"
        opponent = "opponent"
    else:
        ourPlayer = "opponent"
        opponent = "player"

    target_dict = {'r':'s', 'p':'r', 's':'p'}
    # evaluation of action
    if action[0] == "THROW":
        # ("THROW", symbol_type, point)
        # reward throw action that try to eliminate hostile tokens with high possibility
        # high possibility means there multiple hostile tokens within the throw range
        # or there are hostile tokens being chased
        throw_range = get_throw_range(state)[0]
        enemy_token_list = [item for sublist in state.play_dict[opponent].values() for item in sublist]
        player_token_list = [item for sublist in state.play_dict[ourPlayer].values() for item in sublist]
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
            enemy_token_type = get_symbol_by_location(opponent, state.play_dict, enemy_token_pos)[0]
            counter_token_type = target_dict[target_dict[enemy_token_type]]
            counter_token_list = state.play_dict[ourPlayer][counter_token_type]
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
            if action[2] in state.play_dict[opponent][target_type]:
                # if hostile token is already in danger, no need to use throw
                if action[2] not in enemy_token_chased_list:
                    aggresive_score += THROW_ELIMINATION_REWARD * (1 - 1/count)
                    reward_list.append("Throw elimination with high possibility +" + str(THROW_ELIMINATION_REWARD * (1 - 1/count)))
            # punish being eliminated
            elif action[2] in state.play_dict[opponent][counter_type]:
                punishment_score -= THROW_ELIMINATION_REWARD
                reward_list.append("be eliminated throw punishment -" + str(THROW_ELIMINATION_REWARD))
    

        # throw action2: throw on friendly token
        elif action[2] in player_token_list:
            # punish eliminating friendly token
            if action[2] in state.play_dict[ourPlayer][target_type]:
                punishment_score -= THROW_ELIMINATION_REWARD 
                reward_list.append("throw: eliminating friendly token punishment -"+str(THROW_ELIMINATION_REWARD))
            # punish being eliminated
            elif action[2] in state.play_dict[ourPlayer][counter_type]:
                reward_list.append("throw: on counter friendly token punishment -"+str(THROW_ELIMINATION_REWARD))
                punishment_score -= THROW_ELIMINATION_REWARD

        # throw action3: throw on empty grid
        else:
            reward_list.append("throw on empty grid - 2")
            punishment_score -= SCALE


        # reward throw action2: throw type of token currently we dont have
        least_have_type = sorted(get_current_player_nodes_count(state, "player"), key=get_current_player_nodes_count(state, "player").get)[0]
        if action[1] == least_have_type:
            defense_score += THROW_DEFENSE_REWARD

        # reward throw action3: throw counter type of tokens that enemy has more than ours
        counter = {}
        count = 0
        for type in ['r', 'p', 's']:
            count = len(state.play_dict[ourPlayer][type]) - len(state.play_dict[opponent][target_dict[type]])
            counter[type] = count
        
        value = -1 * (counter[action[1]]+1) * THROW_ATTACK_REWARD
        aggresive_score += value
        reward_list.append("throw counter token reward +" + str(value))
        
            
        
    elif action[0] == "SLIDE" or action[0] == "SWING":
        token_type = get_symbol_by_location(ourPlayer, state.play_dict, action[1])
        # Next is a few of lists that store position information of 
        # hostile_token, friendly_token and target_token
        # for example, if my token is 'r'
        # then hostile token will be 'p', because 'p' eats 'r'
        # friendly token will be 's', because 's' counters 'p'
        # target token will be 's', because 'r' eliminates 's'
        hostile_token_type = target_dict[target_dict[token_type]]
        hostile_token_list = state.play_dict[opponent][hostile_token_type] # may need to consider draw situation
        friendly_token_type = target_dict[token_type]
        friendly_tokens_list = state.play_dict[ourPlayer][target_dict[token_type]] 
        target_token_type = target_dict[token_type]
        target_token_list = state.play_dict[opponent][target_token_type]

        # reward action1: try to eliminate hostile token
        if action[2] in state.play_dict[opponent][target_token_type]:
            reward_list.append("Chasing enemy token +" + str(CHASING_REWARD))
            aggresive_score += CHASING_REWARD
        # punish action: eliminate friendly token or be eliminated by friendly token
        elif action[2] in state.play_dict[ourPlayer][target_token_type]:
            reward_list.append("punishment: eliminate friendly token -" + str(ELIMINATION_REWARD))
            punishment_score -= ELIMINATION_REWARD
        elif action[2] in state.play_dict[ourPlayer][hostile_token_type]:
            reward_list.append("Chasing enemy token -" + str(CHASING_REWARD))
            punishment_score -= ELIMINATION_REWARD

        # reward action2: flee from hostile token
        if hostile_token_list:
            hostile_token = (closest_one(action[1], hostile_token_list), hostile_token_type)
            # only reward flee action when hostile token is close enough
            if least_distance(hostile_token[0], action[1]) <= ALERT_DISTANCE:
                # reward action that make the distance larger
                if least_distance(hostile_token[0], action[1]) <= least_distance(hostile_token[0], action[2]):
                    # reward swing action more than slide action
                    if least_distance(hostile_token[0], action[1]) == 1:
                        defense_score += FLEE_REWARD * SCALE
                        reward_list.append("danger close flee +" + str(FLEE_REWARD * SCALE))
                    diff = least_distance(hostile_token[0], action[2]) - least_distance(hostile_token[0], action[1])
                    if diff == 2:
                        defense_score += FLEE_REWARD
                        reward_list.append("swing flee +" + str(FLEE_REWARD))
                        # reward the special swing that jump vertically
                        if isSpecialSwing(action[1], action[2]):
                            defense_score += FLEE_REWARD - SCALE
                            reward_list.append("special swing flee +" + str(FLEE_REWARD - SCALE))
                    elif diff == 1:
                        defense_score += FLEE_REWARD - SCALE
                        reward_list.append("slide flee +" + str(FLEE_REWARD - SCALE))
                    elif diff == 0:
                        defense_score += 0
                    else:
                        reward_list.append("move close to enemy -" + str(FLEE_REWARD + SCALE))
                        punishment_score -= FLEE_REWARD + SCALE

                # when being chased
                # reward flee action that run towards friendly tokens for possible swing to get rid of chasing token
                if friendly_tokens_list:
                    friendly_token = (closest_one(action[1], friendly_tokens_list), friendly_token_type)
                    diff = least_distance(friendly_token[0], action[1]) - least_distance(friendly_token[0], action[2])
                    if diff == 1:
                        defense_score += FLEE_REWARD - SCALE
                        reward_list.append("slide flee towards friendly +" + str(FLEE_REWARD - SCALE))
                    elif diff == 2:
                        # reward swing
                        defense_score += FLEE_REWARD
                        reward_list.append("swing flee towards friendly +" + str(FLEE_REWARD))
        

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
                    reward_list.append("swing approach to enemy+" + str(SCALE*0.5))
                    approaching_score += SCALE*0.5

                # reward more if it is close, pose more danger to opponent
                if diff > 0:
                    if post_distance > 2:
                        approaching_score += APPROACHING_REWARD - SCALE
                        reward_list.append("approach to enemy but at least 3 steps away +" + str(APPROACHING_REWARD - SCALE))
                    elif post_distance == 2:
                        reward_list.append("approach to enemy 2 steps away +" + str(APPROACHING_REWARD))
                        approaching_score += APPROACHING_REWARD
                    elif post_distance == 1:
                        reward_list.append("approach to enemy 1 steps away +" + str(APPROACHING_REWARD+SCALE))
                        approaching_score += APPROACHING_REWARD + SCALE
        aggresive_score += approaching_score

        # reward action4: move token that is in enemy throw range
        # this action could lead to opponent's a throw-elimination miss
        enemy_throw_range = get_throw_range(state)[1]
        if action[1][0] in enemy_throw_range:
            reward_list.append("move token within enemy throw range" + str(AVOID_DANGER_REWARD))
            defense_score += AVOID_DANGER_REWARD

        

    # create new state and update with the action for further evaluation
    new_state = add_action_to_play_dict(state, ourPlayer, action)
    eliminate_and_update_board(new_state, target_dict)
    # evaluation of post-action state
    state_score = state_evaluation(new_state)

    # if definitely win, prefer to eat our own token
    if state_score > 800:
        total_score = -PUNISHMENT_WEIGHT *  punishment_score \
                + state_score
 
    total_score = AGGRESIVE_WEIGHT  *  aggresive_score + DEFENSIVE_WEIGHT  *  defense_score + PUNISHMENT_WEIGHT *  punishment_score + state_score

    out_score_dict = {"total_score": total_score,
                        "state_score": state_score,
                        "aggresive_score": aggresive_score,
                        "defense_score": defense_score,
                        "punishment_score": punishment_score,
                        "reward_list": reward_list
                        }
    return out_score_dict







#_____________________________________________________________________________________
def get_throw_range(state):
    """This function is used to get the throw range of both player, it returns a tuple
        which is (player_throw_range, opponent_throw_range)
    """
    have_thrown = 9 - state.throws_left
    enemy_have_thrown = 9 - state.enemy_throws_left
    player_throw_range = tuple()
    enemy_throw_range = tuple()
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

def isSpecialSwing(start, end):
    if start[0] + 2 == end[0] and start[1] == end[1]:
        return True
    elif start[0] == end[0] and start[1] + 2 == end[1]:
        return True
    elif start[0] - 2 == end[0] and start[1] + 2 == end[1]:
        return True
    elif start[0] - 2 == end[0] and start[1] == end[1]:
        return True
    elif start[0] == end[0] and start[1] - 2 == end[1]:
        return True
    elif start[0] + 2 == end[0] and start[1] - 2 == end[1]:
        return True
    else:
        return False

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
        






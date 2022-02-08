from Final.state_evaluation import state_evaluation
from copy import deepcopy
from Final.util import get_symbol_by_location, least_distance, closest_one, get_current_player_nodes_count, get_six_adj_nodes

def action_evaluation(playerClass, whichPlayer,state, action):
    # state = (play_dict, player's throw left, opponnet's throw left, player's side)
    # action = ("SLIDE",start, end) or ("SWING",start, end) or ("THROW",symbol_type, point)
    """this function returns a score that equals
            Score = value_of_action + value_of_postAction_state"""
            
    AGGRESIVE_WEIGHT = 1
    DEFENSIVE_WEIGHT = 1
    PUNISHMENT_WEIGHT = 1.5
    


    
    aggresive_score = 0
    defense_score = 0
    punishment_score = 0
    state_score = 0

    reward_list = []
    ################ chasing action reward parameter ###################
    CHASING_REWARD = 5
    ELIMINATION_REWARD = 10

    ################ fleeing action reward parameter ###################
    FLEE_REWARD = 6
    SCALE = 2
    ALERT_DISTANCE = 3

    ################ approaching action reward parameter ###################
    APPROACHING_REWARD = 4

    ################ avoid danger action reward parameter ###################
    AVOID_DANGER_REWARD = 1
    INTERCEPT_REWARD = 12

    ################ throw-elimination action reward parameter ###################
    THROW_ELIMINATION_REWARD = 5
    THROW_DEFENSE_REWARD = 1  #throw on least have symbol
    THROW_ATTACK_REWARD = 1

    

    # Check the evaluation is used on which side
    if whichPlayer == "player":
        ourPlayer = "player"
        opponent = "opponent"
        prefer_throw = playerClass.Our_Eval_Weight["prefer_throw"]
        THROW_ELIMINATION_REWARD =  prefer_throw
            
    else:
        ourPlayer = "opponent"
        opponent = "player"
        AGGRESIVE_WEIGHT = playerClass.Enemy_Eval_Weight["aggresive"]
        DEFENSIVE_WEIGHT = playerClass.Enemy_Eval_Weight["defensive"]
        prefer_throw = playerClass.Enemy_Eval_Weight["prefer_throw"]
        THROW_ELIMINATION_REWARD = prefer_throw
    
    contact_area_dict = {'r':[],'p':[], 's':[]}
    state_analysis(state, contact_area_dict, ourPlayer, opponent)

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
                    enemy_token_chased_list.append(enemy_token_pos)
                    if enemy_token_pos[0] not in throw_range:
                        count += 1
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
                    friend_symbol = get_symbol_by_location(ourPlayer, state.play_dict, action[2])
                    # if the throwing location doesn't have out own token
                    if not friend_symbol:
                        # if the throwing location is at predicted location (predict enemy move)
                        if action[2] in playerClass.predicted_enemy_action[2]:
                            # check if we have a friendly near by been chasing
                            for friend_token in player_token_list:
                                friend_symbol = get_symbol_by_location(ourPlayer, state.play_dict, friend_token)
                                if friend_symbol == counter_type:
                                    # we take intersection of been chased firendly and enemy nodes
                                    friend_area = set(get_six_adj_nodes(friend_token))
                                    enemy_area = set(get_six_adj_nodes(action[2]))
                                    contact_area = friend_area.intersection(enemy_area)
                                    # if we are sure that next move is on intersection and the distance is 2 not 1 (since enemy eliminate friend when dist = 1)
                                    if len(contact_area) == 1:
                                        if action[2] in contact_area:
                                            aggresive_score += THROW_ELIMINATION_REWARD
                                            reward_list.append("Throw elimination with certainty +" + str(THROW_ELIMINATION_REWARD))
                                            
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
        least_have_type = sorted(get_current_player_nodes_count(state, whichPlayer), key=get_current_player_nodes_count(state, whichPlayer).get)[0]
        if action[1] == least_have_type:
            defense_score += THROW_DEFENSE_REWARD

        # reward throw action3: throw counter type of tokens that enemy has more than ours
        counter = {}
        count = 0
        for type in ['r', 'p', 's']:
            count = len(state.play_dict[ourPlayer][type]) - len(state.play_dict[opponent][target_dict[type]])
            counter[type] = count
        
        value = -1 * (counter[action[1]]+1) * THROW_ATTACK_REWARD
        aggresive_score += value/2
        reward_list.append("throw counter token reward +" + str(value))
        
            
        
    elif action[0] == "SLIDE" or action[0] == "SWING":
        token_type = get_symbol_by_location(ourPlayer, state.play_dict, action[1])
        # Next is a few of lists that store position information of 
        # hostile_token, friendly_token and target_token
        # for example, if my token is 'r'
        # then hostile token will be 'p', because 'p' eats 'r'
        # friendly token will be 's', because 's' counters 'p'
        # target token will be 's', because 'r' eliminates 's'
        enemy_same_token_list = state.play_dict[opponent][token_type]
        hostile_token_type = target_dict[target_dict[token_type]]
        hostile_token_list = state.play_dict[opponent][hostile_token_type] # may need to consider draw situation
        friendly_token_type = target_dict[token_type]
        friendly_tokens_list = state.play_dict[ourPlayer][target_dict[token_type]] 
        target_token_type = target_dict[token_type]
        target_token_list = state.play_dict[opponent][target_token_type]

        # punishment Action 1, been eliminate friendly token or be eliminated by friendly token
        if action[2] in state.play_dict[ourPlayer][target_token_type]:
            reward_list.append("punishment: eliminate friendly token -" + str(ELIMINATION_REWARD))
            punishment_score -= ELIMINATION_REWARD
        if action[2] in state.play_dict[ourPlayer][hostile_token_type]:
            reward_list.append("Been Chased enemy token -" + str(ELIMINATION_REWARD))
            punishment_score -= ELIMINATION_REWARD

        # reward action1: try to eliminate hostile token
        if action[2] in state.play_dict[opponent][target_token_type]:
            reward_list.append("Chasing enemy token +" + str(ELIMINATION_REWARD))
            aggresive_score += ELIMINATION_REWARD
        

        # reward action2: flee from hostile token
        if hostile_token_list:
            hostile_token = (closest_one(action[1], hostile_token_list), hostile_token_type)
            # only reward flee action when hostile token is close enough
            if least_distance(hostile_token[0], action[1]) <= ALERT_DISTANCE:
                # reward action that make the distance larger
                if least_distance(hostile_token[0], action[1]) < least_distance(hostile_token[0], action[2]):
                    # reward swing action more than slide action
                    if least_distance(hostile_token[0], action[1]) == 0:
                        defense_score += (FLEE_REWARD + SCALE)/(1+least_distance(hostile_token[0], action[1]))
                        reward_list.append("danger close flee +" + str(FLEE_REWARD * SCALE))
                    else:
                        #if not dangerous, and we don't have a counter for chasing nodes, prefer throw
                        if not friendly_tokens_list:
                            playerClass.Our_Eval_Weight["prefer_throw"] = 999
                    diff = least_distance(hostile_token[0], action[2]) - least_distance(hostile_token[0], action[1])
                    if diff == 2:
                        defense_score += FLEE_REWARD
                        reward_list.append("swing flee +" + str(FLEE_REWARD))
                        # reward the special swing that jump vertically
                        if isSpecialSwing(action[1], action[2]):
                            defense_score += (FLEE_REWARD - SCALE)/(1+least_distance(hostile_token[0], action[1]))
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
                
                 # when being chased
                # reward flee action that run towards enemy same tokens for possible
                if enemy_same_token_list:
                    cloest_enemy_same_token = (closest_one(action[1], enemy_same_token_list), token_type)
                    diff = least_distance(cloest_enemy_same_token[0], action[1]) - least_distance(cloest_enemy_same_token[0], action[2])
                    distance_with_enemy = least_distance(cloest_enemy_same_token[0], action[2])
                    # if next step can directly move onto enemy same token
                    if distance_with_enemy == 0:
                        # reward swing
                        defense_score += FLEE_REWARD + SCALE * 2
                        reward_list.append("enemy_same_location:" + str(cloest_enemy_same_token[0]) + "hide inside enemy same type +" + str(FLEE_REWARD))
                    else:
                        # if move towards that type, reword
                        if diff == 1:
                            defense_score += (FLEE_REWARD - SCALE)/2
                            reward_list.append("flee towards enemy same type +" + str(FLEE_REWARD - SCALE))
        

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
                        # if no hostile token throw another token to eat others
                        if not hostile_token_list:
                            if len(friendly_tokens_list) < 2:
                                playerClass.Our_Eval_Weight["prefer_throw"] = 999
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
            
        # reward action5: intercept enemy hostile token
        if action[2] in contact_area_dict[token_type]:
            towards_location = get_symbol_by_location(whichPlayer, state.play_dict, action[2]) == target_token_type
            # check if target location is empty or we can eat 
            if (towards_location == target_token_type) or (towards_location == ""): 
                aggresive_score += INTERCEPT_REWARD
                reward_list.append("prevent hostile token from coming" + str(INTERCEPT_REWARD))
        

    # create new state and update with the action for further evaluation
    new_state = add_action_to_play_dict(state, ourPlayer, action)
    eliminate_and_update_board(new_state, target_dict)
    # evaluation of post-action state
    state_score = state_evaluation(new_state, ourPlayer, opponent)


    total_score = AGGRESIVE_WEIGHT  *  aggresive_score + DEFENSIVE_WEIGHT  *  defense_score + PUNISHMENT_WEIGHT *  punishment_score + state_score
    # if definitely win, prefer to Do any action 
    if state_score > 1000:
        if whichPlayer == "player":
            playerClass.Our_Eval_Weight["prefer_throw"] = 999
            total_score = AGGRESIVE_WEIGHT  *  aggresive_score + DEFENSIVE_WEIGHT  *  defense_score + PUNISHMENT_WEIGHT *  punishment_score + state_score
    else:
        # reset parameter
        playerClass.Our_Eval_Weight["prefer_throw"] = 1

    out_score_dict = {"total_score": round(total_score,3),
                        "state_score": round(state_score,3),
                        "aggresive_score": round(aggresive_score,3),
                        "defense_score": round(defense_score,3),
                        "punishment_score": round(punishment_score,3),
                        "reward_list": reward_list
                        }
    return out_score_dict



def state_analysis(state, contact_area_dict, whichPlayer, opponent):
    """get adjacent area of a been chased token"""
    target_dict = {"r":"s", "s":"p", "p":"r"}
    for token_type in ['r', 'p', 's']:
        counter_type = target_dict[target_dict[token_type]]
        for token_pos in state.play_dict[whichPlayer][token_type]:
            hostile_token_list = state.play_dict[opponent][counter_type]
            if hostile_token_list:
                hostile_token_pos = closest_one(token_pos, hostile_token_list)
                if least_distance(token_pos, hostile_token_pos) == 2:
                    contact_areaA = set(get_six_adj_nodes(token_pos))
                    contact_areaB = set(get_six_adj_nodes(hostile_token_pos))
                    contact_area = contact_areaA.intersection(contact_areaB)
                    for area in list(contact_area):
                        if area in state.play_dict[whichPlayer].values():
                            contact_area.remove(area)
                    contact_area_dict[target_dict[token_type]] += (list(contact_area))




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
        






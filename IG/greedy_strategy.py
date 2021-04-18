import random
from IG.util import *
from IG.random_algorithms import *

# Do action with BFS,
# if cannot find path, return FALSE
def BFS_Action(player_class, play_dict, target_dict):
    move_list = []
    for counter, symbol_type in target_dict.items():
        player_counter_list = find_player_symbols(player_class.play_dict, "player", counter)
        target_list = find_player_symbols(player_class.play_dict, "opponent", symbol_type)
        # Check if player have counter symbol and Enemy have symbols can be eliminate
        if (player_counter_list) and (target_list):
            target = target_list[0] 
            ''' 
            if using neareest node to eliminate others, sort the player_counter_list
            choosing closest node to target
            '''
            if player_class.BFS_TUNE_MODE:
                player_counter_list = sorted(player_counter_list, key=lambda x : least_distance(x, target))
            start_token = player_counter_list[0] 
            # BFS search, dodges blocks, returns a path
            next_board_dict = play_dict
            try: 
                path = Search_Path(counter, start_token, target, player_class.play_dict, next_board_dict) 
                # only take second step in the BFS solution
                next_step = path[1]
                if (least_distance(start_token, next_step) == 2):
                    return action_swing(start_token,next_step)
                else:
                    return action_slide(start_token,next_step)
            except:
            #     #if cannot find a path, pass to next action
                 pass
    return False


def greedy_throw(player_class):
    '''
    Trhow a node that can directly eat enemy node
    if cannot, throw least nodes we have
    '''
    # greedy Throw, throw directly to eat enemy symbol
    for counter_symbol, symbol_type in player_class.target_dict.items():
        target_list = player_class.play_dict["opponent"][symbol_type]
        for target in target_list:
            if check_node_in_throw_range(player_class, target):
                return action_throw(counter_symbol, target)
    return False
    

   
def greedy_action(player_class):
    '''
    # Greedy action, 
    # Move first,
    # Throw and Eat Enemy directly
    '''
    num_nodes = sum(get_current_player_nodes_count(player_class, "player").values())

    # if there's symbol on board, do BFS first then throw
    
    #BFS
    # if have throws left, first do greedy search and move and eat
    action = BFS_Action(player_class, player_class.play_dict, player_class.target_dict)
    if action:
        print("\n^^^^^^^^^^^^^^ BFS MOVING ... ^^^^^^^^^^^^^^^\n")
        return action

    ###  GREEDY THROW       
    # if cannot use BFS, try greedy throw
    if (player_class.throws_left > 0):
        action = greedy_throw(player_class)
        if action:
            print("\n^^^^^^^^^^^^^^ GREEDY THROW ^^^^^^^^^^^^^^^\n")
            return action

    # RANDOM MOVE
    # if cannot greedy throw and cannot do BFS, do random swing or slide
    if num_nodes > 0:
        # if reached same game state three times, breakt the tie
        if (player_class.same_state_count >= 3) and (player_class.BREAK_TIE):

            # break tie by random throw
            if (player_class.throws_left>0):
                print("\n^^^^^^^^^^^^^^BREAKING TIE, THROW^^^^^^^^^^^^^^^\n")
                if (player_class.REFINED_THROW):
                    return refined_random_throw(player_class, player_class.REFINED_THROW)
                else:
                    return random_throw(player_class)
        print("\n^^^^^^^^^^^^^^RANDOM SWING/SLIDE^^^^^^^^^^^^^^^\n")
        return do_random_slide_swing(player_class)
    print("\n^^^^^^^^^^^^^^RANDOM THROW^^^^^^^^^^^^^^^\n") 

    if (player_class.REFINED_THROW):
        return refined_random_throw(player_class, player_class.REFINED_THROW)
    else:
        return random_throw(player_class)

    

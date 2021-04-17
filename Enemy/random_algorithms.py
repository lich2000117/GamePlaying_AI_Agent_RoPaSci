import random
from IG.util import *

def random_throw(player_class):
    
    #randomly generate valid throw range
    random_row_num = random.choice(player_class.throw_range)
    random_col_num = random.randint(-(4 - abs(random_row_num)), 4 - abs(random_row_num))
    target_point = (random_row_num, random_col_num)
    symbol_type = random.choice(["s", "p", "r"])  #random select symbol
    return action_throw(player_class, symbol_type, target_point)


   
def random_action(player_class):
    '''
    # Random do action, 
    # 0 for random throw,
    # 1 for random move    
    '''
    action_num = random.randint(0,1)

    # if no symbol on board, must throw
    if sum(get_current_player_nodes_count(player_class).values()) <= 0:
        if player_class.throws_left <= 0:
            print("Error! play_dict is empty and no throw left")
            assert(1==0)
        return random_throw(player_class)

    # if have throws left
    if (player_class.throws_left > 0):
        # randomly choose throw or swing/slide
        if (action_num == 0):
            return random_throw(player_class)
    # if not throw, do swing or slide
    return do_random_slide_swing(player_class)

    


#function that randomly moves one node including swing or slides
def random_move_one_node(start_loc, play_dict):

    #get 6 adjacent nodes 
    next_point_list = get_six_adj_nodes(start_loc)

    swing_node = []
    # get all available movable location points into lists including swings
    player_token_list = [item for sublist in play_dict["player"].values() for item in sublist]
    for point in next_point_list:
        if point in player_token_list:
            for node in get_six_adj_nodes(point):
                if least_distance(start_loc, node) == 2:
                    swing_node.append(node)
            next_point_list = next_point_list + swing_node ## add swing nodes
    
    # Shuffle the next location and return location
    random.shuffle(next_point_list)
    for point in next_point_list:
        if is_point_on_map(play_dict, point):
            # if that's a swing, return swing action, otherwise slide
            if point in swing_node:
                return action_swing(start_loc,point)
            else:
                return action_slide(start_loc,point)



#Random Get nodes and Do Swing or Slide
def do_random_slide_swing(player_class):
    assert(player_class.play_dict != {})   
    # random select output as:  ('s', []) or ('r', []) or ('p', [])
    # select with nodes inside, not return empty list
    while True:
        random_set = random.choice(list(player_class.play_dict["player"].items()))
        # if have valid node list, break the random loop
        if (random_set[1]):
            symbol_location = random.choice(random_set[1])
            symbol_type = random_set[0]
            break
    return random_move_one_node(symbol_location, player_class.play_dict)

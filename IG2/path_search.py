from IG2.util import least_distance
## BFS Algorithm:
# childrens: valid surrounding points
def BFS_Search(type, visited, start, end, play_dict, bfs_queue):
    childrens, visited = get_children(type, visited, play_dict, start, end)
    #initialize queue if not yet,
    if childrens:
        if not bfs_queue:
            bfs_queue = [childrens]
        else:
            bfs_queue.append(childrens)
    #Check each children to see if reached destination
    for child in childrens:
        if (tuple(child) == tuple(end)):
            return visited
    # remove from the queue
    bfs_queue[0].pop(0)
    if not bfs_queue[0]:
        bfs_queue.pop(0)
    #If search completed and no results, get error
    if not bfs_queue:
        raise ValueError("BFS can't find the Solution!")
    #Start another another round of search start at the first of the queue.
    return BFS_Search(type, visited, bfs_queue[0][0], end, play_dict, bfs_queue)

# returns a list of children's location and visited nodes
def get_children(type, visited, play_dict, cur_point, end):
    children_list = []
    # cur_X = cur_point[0]
    # cur_Y = cur_point[1]

    priority_list = []
    next_point_list = get_six_adj_nodes(cur_point)   #get six adj nodes

    #Add swing nodes:
    #for point in next_point_list:
    player_token_list = [item for sublist in play_dict["player"].values() for item in sublist]
    for point in next_point_list:
        if point in player_token_list:
            swing_node = []
            for node in get_six_adj_nodes(point):
                if least_distance(cur_point, node) == 2:
                    swing_node.append(node)
                    
            next_point_list = next_point_list + swing_node ## add swing nodes

    # considered by distance when added
    for point in next_point_list:
        priority_list.append((least_distance(point, end), point))
    priority_list = sorted(priority_list)
    next_point_list =  []
    for point in priority_list:
        next_point_list.append(point[1])

    
    visited_list = [item for sublist in list(visited.values()) for item in sublist]

    #Check next step nodes's validility
    #visited list for reverse finding BFS's path. {(parent):[(child),(child),(child)], ....} 
    for point in next_point_list:
        if ((point not in visited_list) 
                    and (is_point_valid(point)) 
                        and (check_counter_node(play_dict, type, point))):
            children_list.append(list(point))
            if tuple(cur_point) in visited.keys():
                visited[tuple(cur_point)].append(point)
            else:
                visited[tuple(cur_point)] =[point]
    return [children_list, visited]

    
#function that returns next step by using DFS,
# implementing reverse path finding
def get_path_by_dfs(type, start, end, play_dict):
    bfs_queue = [[list(start)]]
    visited = {}
    out_path = [end]
    map_dict = BFS_Search(type, visited, start, end, play_dict, bfs_queue)
    #start from the end and doing reverse path finding:
    cur_lookup = end
    while (True):
        for prev_node, children in map_dict.items():
            if cur_lookup in children:
                cur_lookup = prev_node
                out_path.append(cur_lookup)
                # If reach the start, return the path
                if (cur_lookup == start):
                    out_path.reverse()
                    return out_path



#check if cur_point will be eliminated by tar_point
#return true if cur_point will be eliminated by tar_point
# cur_point: (x,y)
# tar_point: (x,y)
def check_counter_node(next_board_dict, type, tar_point):
    R_node_list = find_player_symbols(next_board_dict, "player", "r") + find_player_symbols(next_board_dict, "opponent", "r")
    P_node_list = find_player_symbols(next_board_dict, "player", "p") + find_player_symbols(next_board_dict, "opponent", "p")
    S_node_list = find_player_symbols(next_board_dict, "player", "s") + find_player_symbols(next_board_dict, "opponent", "s")
    upper_R_list = find_player_symbols(next_board_dict, "player", "r")
    upper_P_list = find_player_symbols(next_board_dict, "player", "p")
    upper_S_list = find_player_symbols(next_board_dict, "player", "s")
    # Rock eaten by Paper or eliminate friendly Sissors
    if type == "r":
        if (tar_point in P_node_list) or (tar_point in upper_S_list):
            return False
    # Paper eaten by Scissor or eliminate friendly Rocks
    if type == "p":
        if (tar_point in S_node_list) or (tar_point in upper_R_list):
            return False
    # Scissor eaten by Rock or eliminate friendly Paper
    if type == "s":
        if (tar_point in R_node_list) or (tar_point in upper_P_list):
            return False
    return True



# params:
#           cur_point = (x_coordinate, y_coordinate)
# check if a point is valid(not off the map)
def is_point_valid(cur_point):
    if abs(cur_point[0]) > 4 or abs(cur_point[1]) > 4:
        return False
    if abs(cur_point[0] + cur_point[1]) > 4:
        return False
    else:
        return True



# Find upper/lower player's all symbols given specific type
##    find_player_symbols(play_dict, "upper", "R") ------  find upper player's all rocks
#      return a list of tuples [(x,y),(x,y),(x,y)]
#       if the pocket is empty, return False
def find_player_symbols(play_dict, player_side, symbol_type):
    node_list = play_dict[player_side][symbol_type]
    if node_list:
        out = node_list.copy()
        return out
    else:
        return []


#get six adacent nodes coordinates
# Start from top left corner
def get_six_adj_nodes(cur_point):
    cur_X = cur_point[0]
    cur_Y = cur_point[1]
    six_nodes = [(cur_X+1, cur_Y-1), (cur_X+1, cur_Y), 
                        (cur_X, cur_Y+1), (cur_X-1, cur_Y+1), 
                        (cur_X-1, cur_Y), (cur_X, cur_Y-1)]
    return six_nodes

#Search Algorithm for Part1,
# Called per step
##
##  
##
#input:
#   start: (x_coordinate, y_coordinate)
#   end: (x_coor, y_coor)
#output:
#   path: [(x,y),(x,y),(x,y)]
def Search_Path(type, start, end, play_dict):
    path = []
    #BFS:
    path = get_path_by_dfs(type, start, end, play_dict)
    if path:
        return path
    else:
        return False    # need to perform algorithms to move two nodes away
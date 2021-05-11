
class State:
    
    def __init__(self, play_dict, throws_left, enemy_throws_left, side):
        self.play_dict =  play_dict
        self.throws_left = throws_left
        self.enemy_throws_left = enemy_throws_left
        self.side = side
        self.target_dict = {'r':'s', 'p':'r', 's':'p'}


def isGameEnded(state):
    num_tokens = len(state.play_dict["player"]['r'] + \
                    state.play_dict["player"]['p'] + state.play_dict["player"]['s'])
    enemy_num_tokens = len(state.play_dict["opponent"]['r'] + \
                            state.play_dict["opponent"]['p'] + state.play_dict["opponent"]['s'])
    num_throws = state.throws_left
    enemy_num_throws = state.enemy_throws_left
    target_dict = {"r":"s", "s":"p", "p":"r"}

    # end condition1: one player has no token or throw left
    if num_tokens == 0 and num_throws == 0:
        if enemy_num_tokens != 0 or enemy_num_throws != 0:
            return (True, "Loser")
        else:
            # both players have no token and throw, the game is ended as draw,
            return (True, "Draw")
    elif enemy_num_tokens == 0 and enemy_num_throws == 0:
        if num_tokens != 0 or num_throws != 0:
            return (True, "Winner")
        else:
            # draw
            return (True, "Draw")
    else:
        pass
    
    # end condition2: one player has an invincible token, the other player has no throws.
    # win if the other player has no invincible token, otherwise draw.
    isInvincible_enemy = False
    isInvincible = False
    if num_throws == 0:
        for type in ['r', 'p', 's']:
            # for example type = 'r'
            if state.play_dict["opponent"][type]:
                # counter type will be 'p'
                counter_type = target_dict[target_dict[type]]
                if len(state.play_dict["player"][counter_type]) == 0:
                    # if enemy has 'r' while i dont have 'p', and I have no throws left
                    # 'r' is invincible
                    isInvincible_enemy = True
    elif enemy_num_throws == 0:
        for type in ['r', 'p', 's']:
            # for example type = 's', i have sissors
            if state.play_dict["player"][type]:
                # counter type will be 'r'
                counter_type = target_dict[target_dict[type]]
                if len(state.play_dict["opponent"][counter_type]) == 0:
                    # if I have 's' while enemy doesnt have 'r', and enemy has no throws left 
                    # 's' is invincible
                    isInvincible = True
    else:
        pass
    
    if isInvincible:
        if isInvincible_enemy:
            # draw
            return (True, "Draw")
        else:
            # i am winning
            return (True, "Winner")
    elif isInvincible_enemy:
        # lose
        return (True, "Loser") 

    return (False, "Unknown")
            





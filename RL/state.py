class State:
    
    def __init__(self, play_dict, throw_left, enemy_throw_left, side):
        self.play_dict = play_dict
        self.throw_left = throw_left
        self.enemy_throw_left = enemy_throw_left
        self.side = side
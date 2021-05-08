class State:
    
    def __init__(self, play_dict, throws_left, enemy_throws_left, side):
        self.play_dict = play_dict
        self.throws_left = throws_left
        self.enemy_throws_left = enemy_throws_left
        self.side = side
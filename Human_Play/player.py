

class Player:
    
    
    def __init__(self, player):
        a = 2




    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        # Random Action defined in random_algorithms.py
        return input('''Enter Input: \n("THROW","s", (1,1)), ("SLIDE",(0,1), (1,0)) ("SWING",(0,1), (1,0))''')
        
    
    def update(self, opponent_action, player_action):
        a = 1

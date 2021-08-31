# RoPaSci360 GamePlaying Agent


# Artificial Intelligence COMP30024
## Project Report
## Group Member: ******* Jiaqi Wu, ******* Chenghao Li
### Overview:
IG is the name of the agent we created to play the board game ”RoPaSci360”. The 
structure which IG used was inspired by reinforcement learning where an agent learns by 
collecting reward and then constantly approximating the innate value function. However, 
due to our inability and lack of knowledge to implement some crucial techniques used in 
RL, like using Deep Neural Network to learn a value function approximator and using 
machine learning to find best features to represent states etc. In the end, we managed to 
implement a shallow paradigm which utilises the reward mechanism to make our agent 
perform complex actions. On the way of improvising, Li, by using the reward mechanism as 
an evaluation model, also developed a prediction system of the opponent which can 
predict the opponent's next greedy move and take advantage of it. Also temporal 
difference learning was also implemented to help IG to learn better value representation of 
each state he visited.

### Keyword: 
Reinforcement learning, reward mechanism, prediction system, temporal difference learning.







## Report: 
<!-- 
In partA, the game basically ends when all upper nodes eliminate its target symbols in all lower nodes. To do so, for each symbol of upper’s, we need to implement a search algorithm to find a possible route for them that leads each from starting position to position of the lower’s token it aims to eliminate, while at the same time bypassing blocks.
So, in this project we implement a search algorithm that is a mix of BFS and greedy search algorithm, the program could find each node’s counter symbol and manage to eliminate them.
 
Further analysis of RoPaSci board game:
States:
Every position of Upper and lower symbols and their type(“R”, “P” or “S”) & positions of blocks; turn; For each upper’s symbol in each turn, whether it has been moved or not.
Action:
1) 	change the positions of all upper’s tokens, either 1 or 2 hexes away.(slide or swing)
2) 	resolve the battle when there are two symbols on the same hex
Goal Test:
Explicit goal test. The game ends when there is no lower’s symbol on the board
Path Cost:
number of turns to eliminate all of lower’s symbol

 
N: numbers of lower symbols to be eliminated
d: BFS tree depth or distance between Upper’s symbol and eliminated lower’s symbol
b: branching factor / Tree depth
Algorithm
Reason:
In this project, we implemented Breadth-first search as our base algorithm. We choose BFS rather than DFS for the reason that we may end up with an infinite loop for searching paths or end up with large tree depth (A single path that covers the whole board). As the board is continuously linked with hex grids with limited board size, expanding our search region layer by layer using BFS performs better.


Efficiency:
M = 61 (#nodes on board)
Our BFS algorithm at worst case takes O(d*M) space and O(d*M) time where M is the number of nodes since it always tries to cover the whole board as long as the target is not reached. And the function is called each time a node moves its location. The distance is 1 and it moves d times to get to the target so the complexity is O(d*M).

Completeness:
The BFS algorithm is complete as it expands from the center node to cover the whole board at the final stage. So if there’s a solution, the algorithm always finds them and returns a reliable result.

Optimality:
For the most of the time, it will find the optimal solution. Under the situation of one-to-one(one upper token is to eliminate one lower token), it will give the optimal solution. When there are more than two upper symbols, BFS is unable to consider routes that contain future-turn possible cooperation between friendly tokens(swing action). These routes seem by BFS to take longer steps, but actually take fewer steps because of one or multiple swing actions. BFS can only consider swing action when two friendly tokens are nearby at the current turn.

Heuristics:
Heuristics have been used. When expanding new nodes, for example, a center node will consider its six adjacent nodes, the algorithm will calculate the distance between each adjacent node and its target node , it helps the BFS algorithm to choose which adjacent node should be explored first.(the hex that is closer to the target hex) Therefore, this heuristic slightly increases the performance of our program but not taken whole algorithm as A* Search. 
 









N: numbers of lower symbols to be eliminated
d: BFS tree depth or distance between Upper’s symbol and eliminated lower’s symbol
b: branching factor / Tree depth

Branching factor, search tree depth and configurations of nodes:
Positions:
If the nodes are placed together instead of distributed far away, space and time cost will be reduced as the tree depth decreases (find solutions earlier because of using BFS search).
If the nodes are placed at the corner, its branching factor will be reduced as the available children are less but the tree depth may be deeper.
If the nodes are placed near the center of the board its branching factor may be large and tree depth may be shallower than at the corner. 
Number of nodes:
If multiple nodes are placed on the board, it may reduce the tree depth as more options are available for BFS to reach(find nearest one)

Time and space complexity with placements of nodes:
Positions:
However, no matter where the nodes are placed, the worst time and space complexity are O(dM) where M is 60 (number of nodes onboard) and d is steps taken to get there.
Number of nodes:
As the algorithm tears apart of the synchronising playing (move all nodes at the same time) to linear solving(move one node at a time),  for each movement a node make, it has to do a BFS process, so for a single node, it takes d steps to get to the target, it takes d times searches. Therefore, to find a solution, in the worst case for N nodes waiting to be eliminated, it has to do O(d*N*M) (number of lower nodes for elimination) calculations. 
 
 

 -->

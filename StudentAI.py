import math
import random
from copy import deepcopy
from random import randint
from BoardClasses import Move, Board, Checker


# The following part should be completed by students.
# Students can modify anything except the class name and exisiting functions and varibles.


class MCTS_Node:
    def __init__(self, move = None, parent = None, board = None, player_color = None) -> None:
        self.move = move
        self.parent = parent
        self.board = deepcopy(board)
        self.children = []
        self.val = 0.0
        self.visits = 0.0
        self.player_color = player_color
        self.untried_moves = self.board.get_all_possible_moves(player_color)

    def UCT_select_child(self):
        c = math.sqrt(2)
        best_child = None
        best_score = -float('inf')
        for child in self.children:
            if child.visits > 0:
                win_ratio = child.val / child.visits
                uct_score = win_ratio + c * math.sqrt(math.log(self.visits) / child.visits)
            else:
                uct_score = float('inf')
            if uct_score > best_score:
                best_score = uct_score
                best_child = child
        return best_child

    def add_child(self, move, board):
        child_board = deepcopy(board)
        child_board.make_move(move, self.player_color)
        opponent_color = 1 if self.player_color == 2 else 2
        child_node = MCTS_Node(move = move, parent = self, board = child_board,
                               player_color = opponent_color)
        self.children.append(child_node)
        for moveset in self.untried_moves:
            if move in moveset:
                moveset.remove(move)
                break
        return child_node

    def update(self, result):
        self.visits += 1.0
        if result == self.player_color:
            self.val += 1.0


def MCTS(root: MCTS_Node, current_color, iterations) -> None:
    opponent = {1: 2, 2: 1}
    for _ in range(iterations):
        node = root

        # 寻找有未尝试走法的节点，如果没有，则使用UCT选择子节点
        while node.children and not any(moves for moves in node.untried_moves if moves):
            node = node.UCT_select_child()

        # 从未尝试的走法中选择一个走法进行扩展
        untried_moves = [move for sublist in node.untried_moves for move in sublist if sublist]
        if untried_moves:
            move = random.choice(untried_moves)
            node = node.add_child(move, node.board)

        # 模拟随机对局并更新节点
        simulation_result = simulate_random_games(node.board, node.player_color)
        while node is not None:
            node.update(simulation_result)
            node = node.parent


# 速度太慢 弃用 之后可以参考
# def heuristic_move_score(board, move, player_color):
#     score = 0.0
#     for pos in move.seq:
#         checker = board.board[pos[0]][pos[1]]
#         if checker.color == player_color:
#             if checker.is_king:
#                 score += 5  # 王棋的权重
#             else:
#                 score += 1  # 普通棋子的权重
#             # if board.is_center_square(pos):
#             #     score += 2  # 占据中心的权重
#     return score

def simulate_random_games(board, current_color):
    board = deepcopy(board)
    opponent = {1: 2, 2: 1}

    while True:
        possible_moves = board.get_all_possible_moves(current_color)

        # 移除空的移动列表
        possible_moves = [m for m in possible_moves if m]

        # 一但一方获胜则结束循环
        if board.is_win(current_color) == current_color:
            return current_color
        if board.is_win(opponent[current_color]) == opponent[current_color]:
            return opponent[current_color]

        # 应用启发式规则 - 优先移动能吃掉其他棋子的棋子
        capture_moves = [m for sublist in possible_moves for m in sublist if len(m.seq) > 2]
        if capture_moves:
            move = random.choice(capture_moves)
        else:
            move = random.choice(random.choice(possible_moves))

        board.make_move(move, current_color)

        current_color = opponent[current_color]


class StudentAI:
    def __init__(self, col, row, p) -> None:
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()
        self.color = 2
        self.opponent = {1: 2, 2: 1}

    def get_move(self, move: Move):
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1
        root = MCTS_Node(board = self.board, player_color = self.color)
        MCTS(root, self.color, iterations = 100) #需要调整
        best_move = max(root.children, key = lambda c: c.val / c.visits).move
        self.board.make_move(best_move, self.color)
        return best_move




# minimax 版
"""
from random import randint
from BoardClasses import Move
from BoardClasses import Board
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2


    def evaluate(self, board):
        white_score = 0
        black_score = 0

        # need to find better weight values or find new weight rules
        piece_weight = 1
        king_weight = 1.5
        edge_weight = 0.5
        center_weight = 0.5

        for row in range(board.row):
            for col in range(board.col):
                checker = board.board[row][col]

                #for white pieces score
                if checker.color == 'W':
                    white_score += piece_weight
                    if checker.is_king:
                        white_score += king_weight
                    if col == 0 or col == board.col - 1:
                        white_score += edge_weight
                    if row == 0 or row == board.row - 1:
                        white_score += center_weight

                # for black pieces score
                elif checker.color == 'B':
                    black_score += piece_weight
                    if checker.is_king:
                        black_score += king_weight
                    if col == 0 or col == board.col - 1:
                        black_score += edge_weight
                    if row == 0 or row == board.row - 1:
                        black_score += center_weight

        if self.color == 1:
            return black_score - white_score
        else:
            return white_score - black_score

    def minimax(self, board, depth, alpha, beta, is_max_player):
        # if reached the search depth limit, or some player wins, return the current score
        if depth == 0 or board.is_win(self.color) or board.is_win(self.opponent[self.color]):
            return self.evaluate(board)

        # traverse all possible moves of the current player
        if is_max_player:
            max_player_score = float('-inf')
            for move in board.get_all_possible_moves(self.color):
                for m in move:
                    board.make_move(m, self.color)
                    current_score = self.minimax(board, depth - 1, alpha, beta, False) # pass in alpha and beta, switch players
                    board.undo()
                    max_player_score = max(max_player_score, current_score)
                    alpha = max(alpha, current_score)
                    if beta <= alpha:
                        break
            return max_player_score
        # traverse all possible moves of the opponent
        else:
            min_player_score = float('inf')
            for move in board.get_all_possible_moves(self.opponent[self.color]):
                for m in move:
                    board.make_move(m, self.opponent[self.color])
                    current_score = self.minimax(board, depth - 1, alpha, beta, True)  # pass in alpha and beta, switch players
                    board.undo()
                    min_player_score = min(min_player_score, current_score)
                    beta = min(beta, current_score)
                    if beta <= alpha:
                        break
            return min_player_score

    def find_best_move(self, board, depth):
        best_move = None
        alpha = float('-inf')
        beta = float('inf')

        for move in board.get_all_possible_moves(self.color):
            for m in move:
                board.make_move(m, self.color)
                score = self.minimax(board, depth - 1, alpha, beta, self.color == 2)
                board.undo()
                if self.color == 1 and score > alpha: # for black use alpha
                    alpha = score
                    best_move = m
                elif self.color == 2 and score < beta: # for white use beta
                    beta = score
                    best_move = m

        return best_move

    # get_move() with best move
    def get_move(self, move):
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1

        # call the find_best_move() to get the best move
        best_move = self.find_best_move(self.board, 3)  # example, depth set to 3, change later
        self.board.make_move(best_move, self.color)
        return best_move
"""
import math
import random
from copy import deepcopy
from random import randint
from BoardClasses import Move, Board, Checker


# The following part should be completed by students.
# Students can modify anything except the class name and exisiting functions and varibles.


class MCTS_Node:
    def __init__(self, move=None, parent=None, board=None, player_color=None) -> None:
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
        best_score = -float("inf")
        for child in self.children:
            if child.visits > 0:
                win_ratio = child.val / child.visits
                uct_score = win_ratio + c * math.sqrt(
                    math.log(self.visits) / child.visits
                )
            else:
                uct_score = float("inf")
            if uct_score > best_score:
                best_score = uct_score
                best_child = child
        return best_child

    def add_child(self, move, board):
        child_board = deepcopy(board)
        child_board.make_move(move, self.player_color)
        opponent_color = 1 if self.player_color == 2 else 2
        child_node = MCTS_Node(
            move=move, parent=self, board=child_board, player_color=opponent_color
        )
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

    def simulate_random_games(self):
        board = deepcopy(self.board)
        current_color = self.player_color
        opponent = {1: 2, 2: 1}

        while True:
            possible_moves = board.get_all_possible_moves(current_color)

            # 一但一方获胜则结束循环
            if board.is_win(current_color) == current_color:
                return current_color
            if board.is_win(opponent[current_color]) == opponent[current_color]:
                return opponent[current_color]

            # 应用启发式规则
            move = self.heuristic_choose_move(possible_moves)

            board.make_move(move, current_color)
            current_color = opponent[current_color]

    def heuristic_choose_move(self, possible_moves):
        # 移除空的移动列表
        possible_moves = [m for m in possible_moves if m]

        # 启发式规则 - 优先考虑能吃子的走法
        capture_moves = [
            m for sublist in possible_moves for m in sublist if len(m.seq) > 2
        ]
        if capture_moves:
            return random.choice(capture_moves)

        # 其他启发式规则可以在这里添加

        # 如果没有吃子走法，随机选择一个走法
        return random.choice(random.choice(possible_moves))


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
        root = MCTS_Node(board=self.board, player_color=self.color)
        self.run_mcts(root)
        best_move = max(root.children, key=lambda c: c.val / c.visits).move
        self.board.make_move(best_move, self.color)
        return best_move

    def run_mcts(self, root):
        iterations = 100  # 或根据需要调整迭代次数
        for _ in range(iterations):
            node = root

            # 寻找有未尝试走法的节点，如果没有，则使用UCT选择子节点
            while node.children and not any(
                moves for moves in node.untried_moves if moves
            ):
                node = node.UCT_select_child()

            # 从未尝试的走法中选择一个走法进行扩展
            untried_moves = [
                move for sublist in node.untried_moves for move in sublist if sublist
            ]
            if untried_moves:
                move = random.choice(untried_moves)
                node = node.add_child(move, node.board)

            # 启发式模拟随机对局并更新节点
            simulation_result = node.simulate_random_games()
            while node is not None:
                node.update(simulation_result)
                node = node.parent

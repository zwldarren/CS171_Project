import math
import random
import time
from copy import deepcopy
from BoardClasses import Move, Board, Checker
from typing import List

# The following part should be completed by students.
# Students can modify anything except the class name and exisiting functions and varibles.


class MCTS_Node:
    def __init__(self, board: Board, player_color, move=None, parent=None) -> None:
        self.move = move
        self.parent = parent
        self.board = deepcopy(board)
        self.children = []
        self.val = 0.0
        self.visits = 0.0
        self.player_color = player_color
        self.opponent = {1: 2, 2: 1}
        self.untried_moves = self.board.get_all_possible_moves(player_color)

    def UCT_select_child(self):
        c = math.sqrt(2)
        best_score = -float("inf")
        best_child = MCTS_Node(board=self.board, player_color=self.player_color)
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
            win_confidence = (self.val / self.visits) if self.visits > 0 else 0
            self.val += 1.0 + win_confidence  # More weight to consistent wins
        # elif result == self.opponent[self.player_color]:
        #   self.val -= 1.0  # Subtract score if opponent wins

    def simulate_random_games(self):
        board = deepcopy(self.board)
        current_color = self.player_color

        while True:
            possible_moves = board.get_all_possible_moves(current_color)

            # 一但一方获胜则结束循环
            if board.is_win(current_color) == current_color:
                return current_color
            if (
                board.is_win(self.opponent[current_color])
                == self.opponent[current_color]
            ):
                return self.opponent[current_color]

            # 应用启发式规则
            move = self.heuristic_choose_move(possible_moves)

            board.make_move(move, current_color)
            current_color = self.opponent[current_color]

    def heuristic_choose_move(self, possible_moves):
        # filter out empty moves
        possible_moves = [m for m in possible_moves if m]

        # choose the move with the most captures
        capture_move = self.get_capture_move(possible_moves)
        if capture_move:
            return capture_move

        # choose the move that is safe
        safe_moves = self.get_safety_move(possible_moves)
        if safe_moves:
            return random.choice(safe_moves)

        return random.choice(random.choice(possible_moves))

    def get_capture_move(self, possible_moves: List[List[Move]]):
        # 找到能吃最多子的走法
        max_capture = 2
        capture_moves = []
        for moveset in possible_moves:
            for move in moveset:
                if len(move) > max_capture:
                    max_capture = len(move)
                    capture_moves = [move]
                elif len(move) == max_capture:
                    capture_moves.append(move)
        if capture_moves:
            return random.choice(capture_moves)
        return None

    def get_safety_move(self, possible_moves):
        # Implement logic to determine if the move exposes the piece to risk
        safe_moves = []
        opponent = {1: 2, 2: 1}
        opponent_color = opponent[self.player_color]

        for moveset in possible_moves:
            for move in moveset:
                is_safe = True
                target_row, target_col = move.seq[-1]

                # Checking adjacent squares for opponent pieces
                adjacent_positions = [
                    (target_row - 1, target_col - 1),  # upper left
                    (target_row - 1, target_col + 1),  # upper right
                    (target_row + 1, target_col - 1),  # lower left
                    (target_row + 1, target_col + 1),  # lower right
                ]

                for pos in adjacent_positions:
                    if self.is_in_board(*pos):
                        adj_piece = self.board.board[pos[0]][pos[1]]
                        if adj_piece.color == opponent_color:
                            # Check if opponent piece can capture the moved piece
                            if self.can_be_captured(
                                pos, (target_row, target_col), opponent_color
                            ):
                                is_safe = False
                                break

                if is_safe:
                    safe_moves.append(move)

        return safe_moves if safe_moves else None

    def can_be_captured(self, opponent_pos, target_pos, opponent_color):
        # Check if a piece at opponent_pos can capture a piece at target_pos
        row_diff = target_pos[0] - opponent_pos[0]
        col_diff = target_pos[1] - opponent_pos[1]

        # The direction the opponent piece would move to capture
        capture_direction = (row_diff * 2, col_diff * 2)
        capture_pos = (
            opponent_pos[0] + capture_direction[0],
            opponent_pos[1] + capture_direction[1],
        )

        # Use the Board's is_valid_move method to check for a valid capture
        return self.board.is_valid_move(
            opponent_pos[0],
            opponent_pos[1],
            capture_pos[0],
            capture_pos[1],
            opponent_color,
        )

    def is_in_board(self, row, col):
        # Check if the position is within the board boundaries
        return 0 <= row < self.board.row and 0 <= col < self.board.col


class Minimax:
    def __init__(self, board, player_color):
        self.board = board
        self.color = player_color
        self.opponent = {1: 2, 2: 1}

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

                # for white pieces score
                if checker.color == "W":
                    white_score += piece_weight
                    if checker.is_king:
                        white_score += king_weight
                    if col == 0 or col == board.col - 1:
                        white_score += edge_weight
                    if row == 0 or row == board.row - 1:
                        white_score += center_weight

                # for black pieces score
                elif checker.color == "B":
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
        if (
            depth == 0
            or board.is_win(self.color)
            or board.is_win(self.opponent[self.color])
        ):
            return self.evaluate(board)

        # traverse all possible moves of the current player
        if is_max_player:
            max_player_score = float("-inf")
            for move in board.get_all_possible_moves(self.color):
                for m in move:
                    board.make_move(m, self.color)
                    current_score = self.minimax(
                        board, depth - 1, alpha, beta, False
                    )  # pass in alpha and beta, switch players
                    board.undo()
                    max_player_score = max(max_player_score, current_score)
                    alpha = max(alpha, current_score)
                    if beta <= alpha:
                        break
            return max_player_score
        # traverse all possible moves of the opponent
        else:
            min_player_score = float("inf")
            for move in board.get_all_possible_moves(self.opponent[self.color]):
                for m in move:
                    board.make_move(m, self.opponent[self.color])
                    current_score = self.minimax(
                        board, depth - 1, alpha, beta, True
                    )  # pass in alpha and beta, switch players
                    board.undo()
                    min_player_score = min(min_player_score, current_score)
                    beta = min(beta, current_score)
                    if beta <= alpha:
                        break
            return min_player_score

    def find_minmax_best_move(self, board, depth):
        best_move = None
        alpha = float("-inf")
        beta = float("inf")

        for move in board.get_all_possible_moves(self.color):
            for m in move:
                board.make_move(m, self.color)
                score = self.minimax(board, depth - 1, alpha, beta, self.color == 2)
                board.undo()
                if self.color == 1 and score > alpha:  # for black use alpha
                    alpha = score
                    best_move = m
                elif self.color == 2 and score < beta:  # for white use beta
                    beta = score
                    best_move = m

        return best_move


class StudentAI:
    def __init__(self, col, row, p) -> None:
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()
        self.color = 2
        self.opponent = {1: 2, 2: 1}
        self.total_time = 0
        self.max_total_time = 300

    def get_move(self, move: Move):
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1
        root = MCTS_Node(board=self.board, player_color=self.color)

        start_time = time.time()
        self.run_mcts(root)
        elapsed_time = time.time() - start_time
        self.total_time += elapsed_time

        if self.total_time > self.max_total_time * 0.9:
            # 时间不够时采用minmax算法快速决定
            # best_move = max(root.children, key=lambda c: c.visits).move
            minimax = Minimax(self.board, self.color)
            best_move = minimax.find_minmax_best_move(self.board, 5)
        else:
            best_move = max(root.children, key=lambda c: c.val / c.visits).move
        self.board.make_move(best_move, self.color)
        return best_move

    def run_mcts(self, root: MCTS_Node):
        # if the game is in the late stage, decrease the iteration number
        if self.total_time > self.max_total_time * 0.7:
            iterations = 150
        else:
            iterations = 300  # change the iteration number here
        for _ in range(iterations):
            if self.total_time > self.max_total_time * 0.9:
                break
            node = root

            # select a node to explore
            while node.children and not any(
                moves for moves in node.untried_moves if moves
            ):
                node = node.UCT_select_child()

            # choose untried move
            untried_moves = [
                move for sublist in node.untried_moves for move in sublist if sublist
            ]
            if untried_moves:
                move = random.choice(untried_moves)
                node = node.add_child(move, node.board)

            # simulate random games
            simulation_result = node.simulate_random_games()
            while node is not None:
                node.update(simulation_result)
                node = node.parent

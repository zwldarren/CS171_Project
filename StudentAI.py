import math
import random
from copy import deepcopy
from BoardClasses import Move, Board, Checker
from typing import List

# The following part should be completed by students.
# Students can modify anything except the class name and exisiting functions and varibles.


class MCTS_Node:
    board_cache = {}

    def __init__(self, board: Board, player_color, move=None, parent=None) -> None:
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
            self.val += 1.0

    def simulate_random_games(self):
        board_hash = hash(str(self.board.board))
        if board_hash in MCTS_Node.board_cache:
            return MCTS_Node.board_cache[board_hash]
        board = deepcopy(self.board)
        current_color = self.player_color
        opponent = {1: 2, 2: 1}

        while True:
            possible_moves = board.get_all_possible_moves(current_color)

            # 一但一方获胜则结束循环
            if board.is_win(current_color) == current_color:
                MCTS_Node.board_cache[board_hash] = current_color
                return current_color
            if board.is_win(opponent[current_color]) == opponent[current_color]:
                MCTS_Node.board_cache[board_hash] = opponent[current_color]
                return opponent[current_color]

            # 应用启发式规则
            move = self.heuristic_choose_move(possible_moves)

            board.make_move(move, current_color)
            current_color = opponent[current_color]

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
        
        # # 优先防守
        # if self.is_ahead_in_pieces():
        #     defensive_moves = [m for m in possible_moves if self.is_defensive_move(m)]
        #     if defensive_moves:
        #         return random.choice(defensive_moves)

        # choose the move that promotes a piece
        promotion_moves = self.get_promotion_move(possible_moves)
        if promotion_moves:
            return random.choice(promotion_moves)
        
        # choose the move that controls the center of the board
        center_moves = self.get_center_control_move(possible_moves)
        if center_moves:
            return random.choice(center_moves)

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

    def get_promotion_move(self, possible_moves: List[List[Move]]):
        # if the move is a sequence of moves, check if the last move is a promotion
        promotion_row = 0 if self.player_color == 1 else self.board.row - 1
        for moveset in possible_moves:
            for move in moveset:
                if move.seq[-1][0] == promotion_row:
                    return move
        return None

    def get_center_control_move(self, possible_moves: List[List[Move]]):
        # Assuming the center of the board is strategically important
        center_rows = [self.board.row // 2 - 1, self.board.row // 2]
        center_cols = [self.board.col // 2 - 1, self.board.col // 2]
        for moveset in possible_moves:
            for move in moveset:
                end_pos = move.seq[-1]
                if end_pos[0] in center_rows and end_pos[1] in center_cols:
                    return move
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
            opponent_pos[0], opponent_pos[1], capture_pos[0], capture_pos[1], opponent_color
        )

    def is_in_board(self, row, col):
        # Check if the position is within the board boundaries
        return 0 <= row < self.board.row and 0 <= col < self.board.col

    # def is_defensive_move(self, move):
    #     # Implement logic to check if the move is good for defense
    #     # This might involve checking if the move helps in blocking opponent moves or protecting key pieces
    #     pass

    # def is_ahead_in_pieces(self):
    #     # Check if the current player is ahead in terms of piece count
    #     my_pieces = sum(
    #         1
    #         for row in self.board.board
    #         for piece in row
    #         if piece.color == self.player_color
    #     )
    #     opponent_pieces = sum(
    #         1
    #         for row in self.board.board
    #         for piece in row
    #         if piece.color != "." and piece.color != self.player_color
    #     )
    #     return my_pieces > opponent_pieces


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

    def run_mcts(self, root: MCTS_Node):
        iterations = 100  # change the iteration number here
        for _ in range(iterations):
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

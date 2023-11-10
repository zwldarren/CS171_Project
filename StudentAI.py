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

        # for self.color: 2 is black 1 is white
        if self.color == 1:
            return black_score - white_score
        else:
            return white_score - black_score

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        # if reached the search depth limit, or some player wins, return the current score
        if depth == 0 or board.is_win(self.color) or board.is_win(self.opponent[self.color]):
            return self.evaluate(board)

        # traverse all possible moves of the current player
        if maximizing_player:
            max_eval = float('-inf')
            for move in board.get_all_possible_moves(self.color):
                for m in move:
                    board.make_move(m, self.color)
                    eval = self.minimax(board, depth - 1, alpha, beta, False) # pass in alpha and beta
                    board.undo()
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval) # update alpha
                    if beta <= alpha:
                        break
            return max_eval
        # traverse all possible moves of the opponent
        else:
            min_eval = float('inf')
            for move in board.get_all_possible_moves(self.opponent[self.color]):
                for m in move:
                    board.make_move(m, self.opponent[self.color])
                    eval = self.minimax(board, depth - 1, alpha, beta, True)  # pass in alpha and beta
                    board.undo()
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)  # update beta
                    if beta <= alpha:
                        break
            return min_eval

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

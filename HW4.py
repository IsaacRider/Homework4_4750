# Partners: 
# Isaac Rider 
# Joey Gallichio
# Spencer Berger

# HW 4 4750 Description
# Implement minimax algorithm to play a two-player, four-in-a-row game, which is a
# variation of tic-tac-toe: two players, X and O, take turns marking the spaces in a 5×6 grid.
# The player who succeeds in placing 4 of their marks consecutively in a horizontal, vertical,
# or diagonal row wins the game. See an example below where X player plays first and wins
# the game.

# Successor function: a player may place a piece at any
# empty space next to an existing piece horizontally,
# vertically, or diagonally on the board.

# Tie-breaking of moves: break ties in increasing order
# of column number first (smaller column number has
# higher priority) and then increasing order of row
# number (smaller row number has higher priority).

import time
import numpy as np # type: ignore
import copy

ROWS = 5
COLS = 6
X_PLAYER = 'X'
O_PLAYER = 'O'
EMPTY = ' '

class FourInARow:
    DIRECTIONS = [
        (0, 1),   # Horizontal
        (1, 0),   # Vertical
        (1, 1),   # Diagonal down-right
        (1, -1)   # Diagonal down-left
    ]

    nodesGenerated = 0

    def __init__(self):
        self.board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        self.board[3][4] = X_PLAYER  # Player 1's first move
        self.player_turn = O_PLAYER

    def is_valid_move(self, row, col):
        return 0 <= row < ROWS and 0 <= col < COLS and self.board[row][col] == EMPTY

    def make_move(self, row, col, player):
        if self.is_valid_move(row, col):
            self.board[row][col] = player
            return True
        return False

    def print_board(self):
        print("  0 1 2 3 4 5")
        x = 0
        for row in self.board:
            print(x, end=" ")
            x += 1
            print(' '.join(row))
        print("\n")

    def check_winner(self):
        """ Check if there is a winner """
        for row in range(ROWS):
            for col in range(COLS):
                if self.board[row][col] != EMPTY:
                    if self.check_direction(row, col, 1, 0) or \
                       self.check_direction(row, col, 0, 1) or \
                       self.check_direction(row, col, 1, 1) or \
                       self.check_direction(row, col, 1, -1):
                        return self.board[row][col]
        return None

    def check_direction(self, row, col, delta_row, delta_col):
        """ Check if there are 4 consecutive pieces in a direction """
        consecutive = 0
        player = self.board[row][col]
        for i in range(4):
            r = row + delta_row * i
            c = col + delta_col * i
            if 0 <= r < ROWS and 0 <= c < COLS and self.board[r][c] == player:
                consecutive += 1
            else:
                break
        return consecutive == 4

    def get_available_moves(self):
        """ Get a list of valid moves sorted by column and then row """
        moves = []
        for col in range(COLS):
            for row in range(ROWS):
                if self.is_valid_move(row, col):
                    # Add move if it is adjacent to existing pieces
                    if any(self.board[r][c] != EMPTY 
                       for r in range(max(0, row-1), min(ROWS, row+2)) 
                       for c in range(max(0, col-1), min(COLS, col+2))):
                        moves.append((row, col))
    # Tie-breaking: sort by column first, then by row
        moves.sort(key=lambda x: (x[1], x[0]))
        return moves
    
    def count_patterns(self, player):
        two_side_open_3 = 0
        one_side_open_3 = 0
        two_side_open_2 = 0
        one_side_open_2 = 0

        for row in range(ROWS):
            for col in range(COLS):
                if self.board[row][col] != player:
                    continue
                for delta_row, delta_col in self.DIRECTIONS:
                    # Check for 3-in-a-row
                    count = 1
                    for i in range(1, 4):
                        r = row + delta_row * i
                        c = col + delta_col * i
                        if 0 <= r < ROWS and 0 <= c < COLS and self.board[r][c] == player:
                            count += 1
                        else:
                            break

                    if count == 3:
                        pre_r = row - delta_row
                        pre_c = col - delta_col
                        post_r = row + delta_row * 3
                        post_c = col + delta_col * 3
                        pre_open = (0 <= pre_r < ROWS and 0 <= pre_c < COLS and self.board[pre_r][pre_c] == EMPTY)
                        post_open = (0 <= post_r < ROWS and 0 <= post_c < COLS and self.board[post_r][post_c] == EMPTY)
                        if pre_open and post_open:
                            two_side_open_3 += 1
                        elif pre_open or post_open:
                            one_side_open_3 += 1

                    # Check for 2-in-a-row
                    if count == 2:
                        pre_r = row - delta_row
                        pre_c = col - delta_col
                        post_r = row + delta_row * 2
                        post_c = col + delta_col * 2
                        pre_open = (0 <= pre_r < ROWS and 0 <= pre_c < COLS and self.board[pre_r][pre_c] == EMPTY)
                        post_open = (0 <= post_r < ROWS and 0 <= post_c < COLS and self.board[post_r][post_c] == EMPTY)
                        if pre_open and post_open:
                            two_side_open_2 += 1
                        elif pre_open or post_open:
                            one_side_open_2 += 1

        return two_side_open_3, one_side_open_3, two_side_open_2, one_side_open_2

    def evaluate_board(self, player):
        """ Evaluate the board based on the heuristic function """
        opponent = X_PLAYER if player == O_PLAYER else O_PLAYER

        # Count patterns for the current player
        me_two_open_3, me_one_open_3, me_two_open_2, me_one_open_2 = self.count_patterns(player)

        # Count patterns for the opponent
        opp_two_open_3, opp_one_open_3, opp_two_open_2, opp_one_open_2 = self.count_patterns(opponent)

        # Calculate heuristic score based on the provided formula
        h = (200 * me_two_open_3) - (80 * opp_two_open_3) \
            + (150 * me_one_open_3) - (40 * opp_one_open_3) \
            + (20 * me_two_open_2) - (15 * opp_two_open_2) \
            + (5 * me_one_open_2) - (2 * opp_one_open_2)

        return h

    def minimax(self, depth, is_maximizing, alpha, beta, player, ply_limit):
        opponent = X_PLAYER if player == O_PLAYER else O_PLAYER
        winner = self.check_winner()
        
        # Increment node counter for each new state explored
        FourInARow.nodesGenerated = FourInARow.nodesGenerated + 1

        if winner == player:
            return 1000, None
        elif winner == opponent:
            return -1000, None
        elif depth == ply_limit or not self.get_available_moves():
            return self.evaluate_board(player), None

        best_move = None
        if is_maximizing:
            max_eval = -float('inf')
            for move in self.get_available_moves():
                board_copy = copy.deepcopy(self)
                board_copy.make_move(move[0], move[1], player)
                eval, _ = board_copy.minimax(depth+1, False, alpha, beta, player, ply_limit)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in self.get_available_moves():
                board_copy = copy.deepcopy(self)
                board_copy.make_move(move[0], move[1], opponent)
                eval, _ = board_copy.minimax(depth+1, True, alpha, beta, player, ply_limit)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

def play_game():
    game = FourInARow()
    print("After first move:")
    game.print_board()

    move_count = 0
    while not game.check_winner() and game.get_available_moves():
        current_player = X_PLAYER if game.player_turn == X_PLAYER else O_PLAYER
        ply_limit = 2 if current_player == X_PLAYER else 4
        
        # Reset node count before each move
        FourInARow.nodesGenerated = 0

        start_time = time.time()
        score, best_move = game.minimax(0, True, -float('inf'), float('inf'), current_player, ply_limit)
        elapsed_time = time.time() - start_time

        if best_move:
            game.make_move(best_move[0], best_move[1], current_player)
            game.print_board()
            print(f"Player {current_player} moves to {best_move}. Minimax Score: {score}, Nodes Generated: {FourInARow.nodesGenerated}, Time: {elapsed_time:.4f}s")
        game.player_turn = O_PLAYER if game.player_turn == X_PLAYER else X_PLAYER
        move_count += 1

    winner = game.check_winner()
    if winner:
        print(f"Player {winner} wins!")
    else:
        print("It's a tie!")

if __name__ == "__main__":
    play_game()

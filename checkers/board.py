# function:
#   Manages board activities: moving checkers, board state, etc.
import pygame

from .constants import BLACK, ROWS, RED, SQUARE_SIZE, COLS, WHITE, UP, DOWN
from .piece import Piece


class Board:
    def __init__(self):
        self.board = []
        self.red_remaining = self.white_remaining = 12
        self.red_kings = self.white_kings = 0
        self.selected_piece = None
        self.create_board()

    def draw_squares(self, win):
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, ROWS, 2):
                pygame.draw.rect(win, RED, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)
        piece.set_selected(False)

        if row == ROWS - 1 or row == 0:
            piece.make_king()
            if piece.color == WHITE:
                self.white_kings += 1
            else:
                self.red_kings += 1

    def get_piece(self, row, col):
        return self.board[row][col]

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row >= 5:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == RED or piece.king:  # Check upwards
            moves.update(self._traverse_left(row-1, max(row-3, -1), UP, piece.color, left))
            moves.update(self._traverse_right(row-1, max(row-3, -1), UP, piece.color, right))
        if piece.color == WHITE or piece.king: # Check upwards
            moves.update(self._traverse_left(row+1, min(row+3, ROWS), DOWN, piece.color, left))
            moves.update(self._traverse_right(row+1, min(row+3, ROWS), DOWN, piece.color, right))
        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            # check off the board or we're back where we started
            if left < 0 or (r == self.selected_piece.row and left == self.selected_piece.col):
                break
            current = self.board[r][left]
            if current == 0:  # an empty square
                if skipped and not last:  # We've jumped before and not currently
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last  # keeping track of last jumped piece at current new valid square

                if last:  # Did we just jump an opponent's piece before landing on valid square?
                    # Check valid moves from current valid square
                    # if selected piece is a king check opposition direction for additional valid moves
                    if self.selected_piece.king:
                        last_row = last[0].row
                        last_col = last[0].col
                        if step == UP:
                            step = DOWN
                            row = min(r + 3, ROWS)
                        else:
                            step = UP
                            row = max(r - 3, -1)

                        if not (r+step == last_row and left - 1 == last_col):
                            moves.update(self._traverse_left(r+step, row, step, color, left-1, skipped=moves[(r, left)]))
                        if not (r + step == last_row and left + 1 == last_col):
                            moves.update(self._traverse_right(r+step, row, step, color, left+1, skipped=moves[(r, left)]))
                        step = DOWN if step == UP else UP  # Revert back to the original direction

                    if step == UP:
                        row = max(r-3, -1)
                    else:
                        row = min(r+3, ROWS)
                    moves.update(self._traverse_left(r+step, row, step, color, left-1, skipped=last))
                    moves.update(self._traverse_right(r+step, row, step, color, left+1, skipped=last))
                break

            elif current.color == color:
                break
            else:
                last = [current]  # We're jumping opponent's piece

            left -= 1
        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            # if selected piece is a king check opposition direction for additional valid moves
            if right >= COLS or (r == self.selected_piece.row and right == self.selected_piece.col):
                break
            current = self.board[r][right]
            if current == 0:  # an empty square
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last

                if last:  # Did we just jump an opponent's piece before landing on valid square?
                    # Check valid moves from current valid square
                    # if selected piece is a king check opposition direction for additional valid moves
                    if self.selected_piece.king:
                        last_row = last[0].row
                        last_col = last[0].col
                        if step == UP:
                            step = DOWN
                            row = min(r + 3, ROWS)
                        else:
                            step = UP
                            row = max(r - 3, -1)

                        if not (r+step == last_row and right - 1 == last_col):
                            moves.update(self._traverse_left(r+step, row, step, color, right-1, skipped=moves[(r, right)]))
                        if not (r + step == last_row and right + 1 == last_col):
                            moves.update(self._traverse_right(r+step, row, step, color, right+1, skipped=moves[(r, right)]))
                        step = DOWN if step == UP else UP  # Revert back to the original direction

                    if step == UP:
                        row = max(r - 3, -1)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r+step, row, step, color, right-1, skipped=last))
                    moves.update(self._traverse_right(r+step, row, step, color, right+1, skipped=last))  # row-1
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1
        return moves

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == RED:
                    self.red_remaining -= 1
                else:
                    self.white_remaining -= 1

    def winner(self):
        if self.red_remaining <= 0:
            return WHITE
        elif self.white_remaining <= 0:
            return RED
        else:
            None

    def set_selected_piece(self, piece):
        self.selected_piece = piece

    def get_selected_piece(self):
        return self.selected_piece



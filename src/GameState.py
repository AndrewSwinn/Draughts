# Class to contain the state of the game.
#
# A complete game takes 32 bytes to store.
#
# A gigabyte of memory should be able to store 25,500,000 window states.
#
# With a branching factor of 7 that gives a Breadth First tree depth of 8.7
#
# Black counters represented by  1. Black kings +2.
# White counters represented by -1. White kings -2.
#
# Game can only be changed using the moveCounter method
#

import numpy as np

class GameState:

    def __init__(self, game_state=None, counters=None):

        self.black_weights = np.array(
            [[8, 4, 6, 8, 10, 12, 14, 16],
             [8, 2, 3, 4, 5, 6, 7, 8],
             [8, 2, 3, 4, 5, 6, 7, 8],
             [8, 4, 6, 8, 10, 12, 14, 16]])

        self.white_weights = np.array(
            [[16, 14, 12, 10, 8, 6, 4, 8],
             [8, 7, 6, 5, 4, 3, 2, 8],
             [8, 7, 6, 5, 4, 3, 2, 8],
             [16, 14, 12, 10, 8, 6, 4, 8]])

        if game_state is None:

         #   self.board     = np.zeros((4, 8), dtype=np.int8)
            self.bitboard = bytearray(b'\x11\x11\x11\x11\x11\x11\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF')
            self.score     = 0
            self.game_over = False

            if counters is None:

                for col in range(0,4):

                    for row in range(0, 3):

                        self.set_square(col, row,       1)
                        self.set_square(col, 7 - row,  -1)

            else:

                # option to allow a custom Game State. Useful for testing

                for black in counters[0]: self.set_square(black[0], black[1],  1)

                for white in counters[1]: self.set_square(white[0], white[1], -1)

        else:

            self.__init__()

            for col in range(0, 4):

                for row in range(0, 8):

                    self.set_square(col, row, game_state.get_square(col, row))

        self._evaluate_position()

    def __str__(self):

        output = ""

        for row in range (7, -1, -1):

            if row % 2 == 1: output = output + ' '

            for column in range (0, 4):


                if   self.get_square(column, row) == -1: counter = 'w'
                elif self.get_square(column, row) == -2: counter = 'W'
                elif self.get_square(column, row) ==  1: counter = 'b'
                elif self.get_square(column, row) ==  2: counter = 'B'
                else: counter = '.'

                output = output + counter + ' '

            output = output + '\n'

        output = output + 'Score : ' + str(self.score) + '\n'

        return output

    def __hash__(self):

        return int.from_bytes(self.bitboard, 'big')

    def get_square(self, col, row):

        square_pair = self.bitboard[col // 2 + row * 2]

        square = square_pair // 16 if col % 2 == 0 else square_pair % 16

        if square > 8: square = square - 16

        #    return self.board[col, row]
        return square

    def set_square(self, col, row, value):

        b_value  = value if value >= 0 else 16 + value

        square_pair = self.bitboard[col // 2 + row * 2]

        squares = [square_pair // 16, square_pair % 16]

        squares[col % 2] = b_value

        square_pair = squares[0] * 16 + squares[1]

        self.bitboard[col // 2 + row * 2] = square_pair

        #self.board[col, row] = value

    def move_counter(self, path):

        path_length = len(path)

        for i, start_square in enumerate(path[:-1]):

            end_square = path[i+1]

            col_changes_one = [-1, 0] if start_square[1] % 2 == 0 else [0, 1]

            counter = self.get_square(start_square[0], start_square[1])

            king_row = 7 if counter == 1 else 0

            self.set_square(start_square[0], start_square[1], 0)

            if  end_square[1] == king_row :
                self.set_square(end_square[0],   end_square[1],  np.sign(counter) * 2 )
            else:
                self.set_square(end_square[0],   end_square[1],  counter)


            jump = False
            # remove jumped counter (if needed)
            if   start_square[1] - end_square[1] ==  2: jump, jumped_row = True, start_square[1] - 1 # backwards
            elif start_square[1] - end_square[1] == -2: jump, jumped_row = True, start_square[1] + 1 # forewards

            if jump:

                if   end_square[0] < start_square[0]: jumped_col = start_square[0] + col_changes_one[0]
                elif end_square[0] > start_square[0]: jumped_col = start_square[0] + col_changes_one[1]

                self.set_square(jumped_col, jumped_row, 0)

        self._evaluate_position()

    def _drag_moves(self, player, path):

        paths = []

        start = path[-1]

        col, row = start[0], start[1]

        row_changes     = [player] if abs(self.get_square(col, row)) == 1 else [1, -1]

        col_changes_one = [-1, 0] if row % 2 == 0 else [0, 1]

        for row_change in row_changes:

            if (self.get_square(col, row) == player or self.get_square(col, row) == player * 2) and (row + row_change) <= 7 and (row + row_change) >= 0 :

                for col_change in col_changes_one:

                    if col + col_change >= 0 and col + col_change <= 3:

                         if  self.get_square(col + col_change, row + row_change ) == 0 :

                            new_path = path.copy()
                            new_path.append((col + col_change, row + row_change))
                            paths.append(new_path)

        return paths

    def _jumps_available(self, player, path):

        jumps = []

        start = path[-1]

        col, row = start[0], start[1]

        row_changes = [player] if self.get_square(col,row) == player else [1, -1]

        col_changes_one = [-1, 0] if row % 2 == 0 else [0, 1]
        col_changes_two = [-1, +1]

        for row_change in row_changes:

            # only consider jumps that land on rows 0 to 7
            if row + (2 * row_change) < 8 and row + (2 * row_change) >= 0:

                for i, col_change in enumerate(col_changes_one):

                    #only consider jumps that land in columns 0 to 3
                    if col + col_changes_two[i] < 4 and col + col_changes_two[i] >= 0:

                        if self.get_square(col + col_change, row + row_change) in [-1 * player, -2 * player]  and self.get_square(col + col_changes_two[i], row + (2 * row_change)) == 0:

                            new_path = path.copy()
                            new_path.append((col + col_changes_two[i], row + (2 * row_change)))
                            jumps.append(new_path)

        return jumps

    def _jump_moves(self, player, path, paths):

        jumps = self._jumps_available(player, path)

        #if no jumps are available (end of a path) AND the length of the path > 1 (i.e. not just a start square)
        if len(jumps) == 0 and len(path) > 1:

            paths.append(path)

        else:

            for jump in jumps:

                new_game = GameState(self)

                new_game.move_counter(path=[jump[-2], jump[-1]])

                new_game._jump_moves(player, jump, paths)

        return paths

    def getLegalActions(self, player):

        # legal actions take the form of an array of tuples ( [(Start), (To)] )
        # [(To)] is needed because if a jump move is made, and another is available it MUST be taken.

        legal_actions = []

        #Search for jumps
        for col in range(4):

            for row in range(8):

              # search for legal moves from square [col, row]

                if np.sign(self.get_square(col, row)) == np.sign(player) :

                    for jump in self._jump_moves(player, path=[(col, row)], paths=[]):

                        legal_actions.append(jump)

        #if no jumps available, search for drags

        if legal_actions == []:

            for col in range(4):

                for row in range(8):

                  # search for legal moves from square [col, row]

                    if np.sign(self.get_square(col, row)) == np.sign(player) :

                        for drag in self._drag_moves(player, [(col, row)]):

                            legal_actions.append(drag)

        return legal_actions

    def swap_player(self):

        # invert the colours of the counters and flip vertically and horiontally

        temp_game = GameState(self)

        for col in range(4):
            for row in range(8):

                self.set_square(col, row,  temp_game.get_square( 3 - col, 7 - row) * -1)

        self._evaluate_position()

        return self

    def _evaluate_position(self):

        blacks, whites = 0, 0

        for col in range(4):

            for row in range(8):

                if self.get_square(col, row) ==  1: blacks  = blacks + self.get_square(col, row) * self.black_weights[col, row]
                if self.get_square(col, row) == -1: whites  = whites - self.get_square(col, row) * self.white_weights[col, row]

                if self.get_square(col, row) ==  2: blacks = blacks + 20
                if self.get_square(col, row) == -2: whites = whites + 20

        self.score = blacks - whites

        if blacks == 0 or whites == 0:

            self.game_over = True

    def is_terminal(self):

        return self.game_over



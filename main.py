from src.Draughts import Draughts
from src.Draughts import Player
from src.GameState import GameState
from src.GameSearch import GameSearch

import time

if __name__ == '__main__':

    if 1 == 2:

        play = 0

        player_index = 0

        game = GameState()

        players = [Player(1, 1, 'Human', 'Waiting', 'Black', 3), Player(2, -1, 'Computer', '', 'White', 8)]

        while game.is_terminal() is not True:

            player = players[player_index]

            print(player.colour, play)

            print(game.getLegalActions(player.counter))

            searcher = GameSearch(player)

            search = searcher.alpha_beta_sort_search(game)

            if search['path'] == 98:

                print('Stuck')
                break

            else:

                game.move_counter(search['path'])

            print(game)

            player_index = 1 - player_index
            play = play + 1



    else:

        game = Draughts(1000, 1000)

        game.MainLoop()

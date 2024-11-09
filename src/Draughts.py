import pygame
import multiprocessing as mp
from ordered_hash_set import OrderedSet

from src.Display    import Display
from src.Display    import Counter
from src.GameState  import GameState
from src.GameSearch import GameSearch


class BackgroundThinker():

    def __init__(self, status, qInput, qOutput):

        self.status  = status
        self.qInput  = qInput
        self.qOutput = qOutput

        prior_states = OrderedSet()

        while self.status['GameState'] != 'Quit':

            if not self.qInput.empty():

                (player, game_state) = self.qInput.get()

                agent = GameSearch(player)

                path = agent.alpha_beta_sort_search_nostalemate(game_state, prior_states)['path']

                new_state = GameState(game_state)

                new_state.move_counter(path)

                new_state_hash = hash(new_state)

                prior_states.add(new_state_hash)

                self.qOutput.put(path)

class Player():

    def __init__(self, number, counter, type, state, colour, searchdepth):

        self.number      = number
        self.counter     = counter
        self.type        = type
        self.state       = state
        self.colour      = colour
        self.searchdepth = searchdepth

        # class variable to manage human moves
        self.counter_chosen     = False
        self.counter_placed     = False
        self.step               = 1


        # class variable to manage computer moves
        self.thinking    = False

    def _computer_move(self, display, game_state, qQuestion, qAnswer):

        return_path = None

        if not self.thinking:

            self.thinking = True

            self.state = 'Thinking'

            #Highlight movable squares
            display.highlight([path[0] for path in game_state.getLegalActions(self.counter)])

            qQuestion.put((self, game_state))

        if self.thinking and not qAnswer.empty():

            return_path = qAnswer.get()

            display.highlight(return_path[1:])

            self.thinking = False

        return return_path


    def _human_move(self, display, game_state, events):

        counterGroup = display.backgroundGroup
        dragGroup    = display.foregroundGroup
        status       = display.status

        return_path = None

        paths        = game_state.getLegalActions(self.counter)

        moveable_counters = [path[0] for path in paths]

        if self.counter_chosen is False:     moveable_squares = moveable_counters
        else:                                moveable_squares = [path[1] for path in paths if path[0] == self.counter_chosen]

        display.highlight(moveable_squares)

        pos = pygame.mouse.get_pos()

        x, y = pos

        for event in events:

            if event.type == pygame.MOUSEBUTTONDOWN:

                # Check to see if picking up a new counter or continuing to drag an already dragged counter
                if (len(dragGroup) > 0) : check_group = dragGroup
                else:                     check_group = counterGroup

                # Check to see if counter is the right colour
                # If the checkGroup is counterGroup the counter is removed and replaced into dragGroup
                for counter in check_group:

                    if counter.rect.collidepoint(pos) and counter.get_location() in moveable_counters :

                        counterGroup.remove(counter)
                        dragGroup.add(counter)

                        self.counter_chosen = counter.get_location()

            if event.type == pygame.MOUSEMOTION and self.counter_chosen != False :

                counter = dragGroup.sprites()[0]

                counter.rect.x = min(max(x - counter.radius, 0),1000 - 2 * counter.radius)

                counter.rect.y = min(max(y - counter.radius, 800 * 0.15), 800 - 2 * counter.radius)

            if (event.type == pygame.MOUSEBUTTONUP):

                # if a counter has been pickup up and is being moved, check to see if it has been moved to a legal square

                if  len(dragGroup) > 0:

                    print(dragGroup.sprites()[0])

                    for counter in dragGroup:

                        counter_paths = [path for path in paths if path[self.step - 1] == counter.get_location()]

                        # check to see if counter has been put back

                        if counter.get_location() == display.get_square(pos):

                            dragGroup.remove(counter)
                            counterGroup.add(counter)
                            self.counter_chosen = False
                            self.counter_placed = False

                            # check to see if counter has been placed in a legal square

                        elif display.get_square(pos) in  [path[1] for path in counter_paths] :

                           # Jump check
                            if abs(counter.get_location()[1] - display.get_square(pos)[1]) == 2:

                                jump_row = int((counter.get_location()[1] + display.get_square(pos)[1]) / 2)
                                col_dir  =     -counter.get_location()[0] + display.get_square(pos)[0]

                                if counter.get_location()[1] % 2 == 0:
                                    if col_dir  == 1: jump_col = counter.get_location()[0]
                                    else:             jump_col = counter.get_location()[0] - 1
                                else:
                                    if col_dir  == 1: jump_col = counter.get_location()[0] + 1
                                    else:             jump_col = counter.get_location()[0]

                                jump_counter = [counter for counter in counterGroup if counter.get_location() == (jump_col, jump_row)][0]

                                jump_counter.taken()

                            counter.location = [display.get_square(pos)]


                            dragGroup.remove(counter)
                            counterGroup.add(counter)

                            return_path =  [path for path in counter_paths if path[1] == display.get_square(pos)][0][:2]

                            self.counter_chosen = False
                            self.counter_placed = False


        return return_path


    def take_turn(self, display, game_state, qQuestion, qAnswer, events):

        if self.type == 'Computer':

            return self._computer_move(display, game_state, qQuestion, qAnswer)

        if self.type == 'Human':

            return self._human_move(display, game_state, events)


class Draughts():

    def __init__(self, width, height, game_state=None):

        pygame.init()

        # create dictionary used to manage the app and control the flow of the game
        self.status = {'GameState': 'Playing', 'Turn': 1, 'Player': -1 }

        #set up multithreading mode and queues
        mp.set_start_method('spawn')
        self.qQuestion = mp.Queue()
        self.qAnswer   = mp.Queue()
        self.thinker   = mp.Process(target=BackgroundThinker, args=(self.status, self.qQuestion, self.qAnswer))
        self.thinker.start()

        self.players = [Player(1,  1, 'Human',    'Waiting', 'Black', 3),
                        Player(2, -1, 'Computer', ''       , 'White', 3)]

        self.display = Display(status=self.status, players=self.players, width=width, height=height)

        self.game_state = GameState(game_state)


    def MainLoop(self):

        for turn in range(200):

            for player in self.players:

                turn_taken = False

                while not turn_taken:

                    if self.status['GameState'] == 'Quit': break

                    events = pygame.event.get()

                    self.display.update(status=self.status, events=events)

                    if self.status['GameState'] != 'Moving':

                        #remove taken counters
                        for counter in self.display.backgroundGroup:
                            if counter.type == 'Taken':
                                self.display.backgroundGroup.remove(counter)


                        path = player.take_turn(self.display, self.game_state, self.qQuestion, self.qAnswer, events)

                        if path is not None:

                            jump = (abs(path[1][1] - path[0][1]) == 2)

                            if path[0] == 99:
                                print('Winner')
                                break

                            else:

                                self.game_state.move_counter(path)

                            if player.type == 'Computer':

                                turn_taken = True

                                self.display.make_move(path)


                            if player.type == 'Human':

                                turn_taken = True

                                if jump:

                                    next_steps = self.game_state.getLegalActions(player.number)

                                    if next_steps is not None:

                                        for step in next_steps:

                                            if (abs(step[1][1] - step[0][1]) == 2)  and (step[0] == path[1]) :

                                                turn_taken = False

                    if turn_taken:
                        print('Turn: ', turn, 'Player, ', player.number)
                        print(self.game_state)
                        print()


                if self.status['GameState'] == 'Quit': break

            if self.status['GameState'] == 'Quit': break

            if self.game_state.game_over: break






        self.thinker.kill()








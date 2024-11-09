import pygame
import pygame_widgets
from   pygame_widgets.slider import Slider
from   pygame_widgets.button import Button


class Board(pygame.surface.Surface):

    def  __init__(self, **kwargs):

        width   = kwargs['width']
        height  = kwargs['height']
        colours = kwargs['colours']

        super().__init__((width, height))

        self.set_colorkey(colours['Transparent'])

        frame = pygame.Rect(0, 0, width, height)

        self.gridCoords = []

        pygame.draw.rect(self, colours['White'], frame)

        self.square_size   = int(width / 8)

        for row in range(7 ,-1,  -1):

            rowCoord = self.square_size * row

            columnCoords = []

            for col in range(4):

                columnCoord = self.square_size * col * 2 + self.square_size * (1- (row % 2))

                columnCoords.append((columnCoord, rowCoord))

                square = pygame.Rect( columnCoord , rowCoord, self.square_size, self.square_size )

                pygame.draw.rect(self, colours['Grey'],square,)

            self.gridCoords.append(columnCoords)

class Lamp(pygame.sprite.Sprite):

    def __init__(self, **kwargs):

        super().__init__()

        self.squaresize = (kwargs['width'] * 0.8) / 8

        self.colours = kwargs['colours']
        self.location = kwargs['location']

        lamp_width = 8

        self.image = pygame.Surface((self.squaresize, self.squaresize))

        self.image.set_colorkey(self.colours['Transparent'])

        pygame.draw.rect(self.image, self.colours['Green'],       (0,          0,          self.squaresize,                  self.squaresize)                , width=lamp_width)
        pygame.draw.rect(self.image, self.colours['Transparent'], (lamp_width, lamp_width, self.squaresize - 2 * lamp_width, self.squaresize -2 * lamp_width ))

        self.rect = self.image.get_rect()

class Counter(pygame.sprite.Sprite):

    def  __init__(self, **kwargs):

        super().__init__()

        self.squaresize = (kwargs['width'] * 0.8) / 8
        self.radius     = (kwargs['width'] * 0.8) / 20
        self.player     = kwargs['player']

        self.colours    = kwargs['colours']
        self.location   = kwargs['location']
        self.type       = 'Pawn'

        colourBorder = self.colours['Blue']
        colourDisk   = self.colours[self.player.colour]

        self.image  = pygame.Surface((self.squaresize, self.squaresize))

        self.image.set_colorkey(self.colours['Transparent'])

        pygame.draw.rect(self.image, self.colours['Transparent'], (0, 0, self.squaresize, self.squaresize))

        pygame.draw.circle(self.image, colourDisk,   center=(self.squaresize/2, self.squaresize/2), radius=self.radius, width=0)
        pygame.draw.circle(self.image, colourBorder, center=(self.squaresize/2, self.squaresize/2), radius=self.radius, width=2)

        self.rect = self.image.get_rect()


    def get_location(self):

        return self.location[0]

    def taken(self):

        self.type = 'Taken'

        pygame.draw.polygon(self.image, self.colours['Red'],
                            ( (15,25), (25,15), (50,40), (75,15), (85,25), (60,50), (85,75), (75,85), (50,60), (25,85), (15,75), (40,50) ), width=0)


    def move(self, display):

        moved = False

        if self.type == 'Taken':

           coords = (0, display.calcCoords(self.location[0][0], self.location[0][1])[1] )

        else:

            coords = display.calcCoords(self.location[0][0], self.location[0][1])

        displaced = (coords[0] - self.rect.x, coords[1] - self.rect.y)

        if   displaced[0] > 0: speedX = 1
        elif displaced[0] < 0: speedX = -1
        else:                  speedX = 0

        if   displaced[1] > 0: speedY = 1
        elif displaced[1] < 0: speedY = -1
        else:                  speedY = 0

        if speedX == 0 and speedY == 0:

            if ((self.location[0][1] == 7 and self.player.number ==1 ) or  (self.location[0][1] == 0 and self.player.number == 2)) and self.type == 'Pawn':

                self.type = 'King'

                pygame.draw.polygon(self.image, self.colours['Yellow'], ((30,30), (30,70), (70, 70), (70,30), (60,55), (50,40), (40,55)), width=0)

            if len(self.location) > 1:

                moved = True

                self.location = self.location[1:]
        else:

            moved = True

        self.rect.x = self.rect.x + speedX

        self.rect.y = self.rect.y + speedY

        return moved




class Display():

    def __init__(self, **kwargs):

        # Create the window and set the class variables

        self.width           = kwargs['width']
        self.height          = kwargs['height']
        self.status          = kwargs['status']
        self.players         = kwargs['players']

        self.backgroundGroup = pygame.sprite.Group()
        self.foregroundGroup = pygame.sprite.Group()
        self.lampGroup       = pygame.sprite.Group()
        self.lamponGroup     = pygame.sprite.Group()


        # create colour dictionary
        self.colours = {'Red': (200, 0, 0), 'Yellow': (200, 200, 0), 'Blue': (0, 0, 200), 'Green': (0, 200, 0),
                        'Grey': (100, 100, 100), 'Black': (0, 0, 0),
                        'White': (255, 255, 255), 'Transparent': (1, 1, 1), 'Background': (0, 200, 200)}

        # Create the window
        self.window  = pygame.display
        self.window.set_caption('Draughts')
        self.surface = self.window.set_mode((self.width, self.height))

        #create the background and the board Rect and Surface objects
        self.board = Board(width=self.width * 0.8, height=self.height * 0.8, colours=self.colours)
        self.background = pygame.Rect( 0, 0, self.width, self.height )
        self.board_pos  = (self.width * 0.1, self.height * 0.1)

        #   create widgets for game control
        self.slidersPreChange = [0, 1]

        self.sliders = [ Slider(self.surface, (self.width * 0.2), 20, 30, 20, handleColour=(1, 0, 0), handleRadius=10, min=0, max=1, step=1, initial=0),
                         Slider(self.surface, (self.width * 0.6), 20, 30, 20, handleColour=(1, 0, 0), handleRadius=10, min=0, max=1, step=1, initial=1)]

        self.searchdepth = [ Slider(self.surface, (self.width * 0.2), 60, 120, 20, handleColour=(1, 0, 0), handleRadius=10, min=2, max=10, step=1, initial=6),
                             Slider(self.surface, (self.width * 0.6), 60, 120, 20, handleColour=(1, 0, 0), handleRadius=10, min=2, max=10, step=1, initial=6)]

        self.buttons = [ Button(self.surface, (self.width * 0.2) ,self.height * 0.92, 150, 50, text='New Game', fontSize=30, inactiveColour=self.colours['Green'], onClick=self.new_game),
                         Button(self.surface, (self.width * 0.6), self.height * 0.92, 100, 50, text='Quit',     fontSize=30, inactiveColour=self.colours['Red']  , onClick=self.quit)]

        for col in range(0, 4):

            for r in range(0, 3):

                for player in self.players:

                    if player.number == 1:
                        row = r
                    else:
                        row = 7 - r

                    counter = Counter(player=player, location=[(col, row)], colours=self.colours, width=self.width, height=self.height )

                    self.backgroundGroup.add(counter)

        for col in range(0, 4):

            for row in range(0, 8):

                lamp = Lamp(location=(col, row), colours=self.colours, width=self.width, height=self.height)

                lamp.rect.x, lamp.rect.y = self.calcCoords(col, row)

                self.lampGroup.add(lamp)


        self.window.update()

    def quit(self):

        self.status['GameState'] = 'Quit'

    def new_game(self):

        self.status['GameState'] = 'Reset'
        self.status['Player']    = -1
        self.status['Turn']      = 1

        for counter in self.backgroundGroup: counter.dest = counter.home

    def move_counters(self):

        moved = False

        for counter in self.backgroundGroup:

            if counter.move(self): moved = True

        return moved

    def make_move(self, path):

        #Sets counter path, and removes 'jumped counters'

        counter = [counter for counter in self.backgroundGroup if counter.location[0] == path[0]][0]

        counter.location = path[1:]

        for i, square in enumerate(path):

            #skip the starting square
            if i > 0:
                # Jump check
                if abs(path[i -1][1] - square[1]) == 2:

                    jump_row = int((path[i -1][1] + square[1]) / 2)
                    col_dir = square[0] - path[i - 1][0]
                    row_dir = 1 if square[1] > path[i - 1][1] else -1

                    if path[i -1][1] % 2 == 0:

                        if col_dir == 1:
                            jump_col = path[i -1][0]
                        else:
                            jump_col = path[i -1][0] - 1

                    else:

                        if col_dir == 1:
                            jump_col = path[i -1][0] + 1
                        else:
                            jump_col = path[i -1][0]

                    jump_counter = [counter for counter in self.backgroundGroup if counter.location[0] == (jump_col, jump_row)][0]

                    jump_counter.taken()
                    #self.backgroundGroup.remove(jump_counter)





    def calcCoords(self, counterColumn, counterRow):


        Xcoord = self.board_pos[0] + self.board.gridCoords[counterRow][counterColumn][0]

        Ycoord = self.board_pos[1] + self.board.gridCoords[counterRow][counterColumn][1]

        return (Xcoord, Ycoord)



    def get_square(self, pos):

        row_coord, col_coord = None, None

        gridX = pos[0] - self.board_pos[0]

        gridY = pos[1] - self.board_pos[1]

        for i, row in enumerate(self.board.gridCoords):

            if abs(row[0][1] + 0.5 * self.board.square_size- gridY) < 0.5 * self.board.square_size : row_coord = i

            for j, square in enumerate(row):

                if abs(square[0] + 0.5 * self.board.square_size - gridX) < 0.5 * self.board.square_size: col_coord = j

        return(col_coord, row_coord)


    def highlight(self,squares):

        self.lamponGroup.empty()

        for lamp in self.lampGroup:

            if lamp.location in squares:

                self.lamponGroup.add(lamp)



    def update(self, **kwargs):

        events = kwargs['events']

        status = kwargs['status']

        x, y = pygame.mouse.get_pos()

        if status['GameState'] == 'Reset':

            status['GameState'] = '' if not self.move_counters() else 'Reset'

        if self.move_counters():  status['GameState'] = 'Moving'
        else:                     status['GameState'] = 'Playing'

        pygame.draw.rect(self.surface, self.colours['Background'], self.background)

        pygame_widgets.update(events)

        self.backgroundGroup.draw(self.surface)

        self.surface.blit(self.board, self.board_pos)

        player_type = lambda slider: 'Human' if slider.getValue() == 0 else 'Computer'

        for i, slider in enumerate(self.sliders):

            # change player description if slider toggle switched

            self.players[i].type = player_type(self.sliders[i])
            self.players[i].searchdepth = self.searchdepth[i].getValue()


            # check to see if the slider value has changed
         #   if self.sliders[i].getValue() != self.slidersPreChange:
         #       self.slidersPreChange = self.sliders[i].getValue()

        texts = [
            {'Message': self.players[0].type, 'Position': ((self.width * 0.05) + 200, 10), 'Size': (120, 36)},
            {'Message': self.players[1].type, 'Position': ((self.width * 0.55) + 100, 10), 'Size': (120, 36)}
        ]

        for text in texts:

            render = pygame.font.SysFont('arial', 32).render(text['Message'], False, self.colours['Black'], self.colours['Grey'])
            textRect = render.get_rect()
            textRect.topleft = text['Position']
            self.surface.blit(render, textRect)

        self.lamponGroup.draw(self.surface)

        self.backgroundGroup.draw(self.surface)
        self.foregroundGroup.draw(self.surface)

        self.window.update()

        return status



from src.GameState import  GameState
from ordered_hash_set import OrderedSet

class GameSearch:

    def __init__(self, Player):


        self.counter    = Player.counter
        self.MaxDepth   = Player.searchdepth

        self.Best       = None

    def search(self, game_state, depth=1):

        player = self.counter if depth % 2 == 1 else -1 * self.counter

        min_max = 1 if depth % 2 == 1 else -1  # 1 means MAX and -1 means MIN

        stuck = True

        if game_state.is_terminal() is False and (depth < self.MaxDepth):

            stuck = True

            Best = {'score': -20000000 * min_max}

            for path in game_state.getLegalActions(player):

                stuck = False

                successor = GameState(game_state)

                successor.move_counter(path)

                Candidate = self.search(successor, depth + 1)

                if min_max == 1:

                    if Candidate['score'] > Best['score']: Best = {'score': Candidate['score'], 'path': path}

                if min_max == -1:

                    if Candidate['score'] < Best['score']: Best = {'score': Candidate['score'], 'path': path}

            if stuck:

                return {'score': game_state.score, 'path': 98}

        else:  # terminal state or max depth

            return {'score': game_state.score, 'path': 99}

        self.Best = Best

       # print(' ' * depth, depth, Best, Candidate)

        return Best

    def alpha_beta_search(self, game_state, depth=1, alpha=-100000000, beta=100000000):

        player  =  self.counter if depth % 2 == 1 else -1 * self.counter

        min_max =  1 if depth % 2 == 1 else -1 # 1 means MAX and -1 means MIN

        stuck = True

        if game_state.is_terminal() is False and (depth < self.MaxDepth):

            stuck = True

            Best = {'score': -20000000 * min_max}

            for path in game_state.getLegalActions(player):

                stuck = False

                successor = GameState(game_state)

                successor.move_counter(path)

                Candidate = self.alpha_beta_search(successor, depth + 1, alpha, beta)

                if min_max ==  1:

                    if Candidate['score'] > Best['score']: Best = {'score':  Candidate['score'], 'path':path}

                    if Candidate['score'] > beta: return Best

                    alpha = max(alpha, Candidate['score'])

                if min_max == -1:

                    if Candidate['score'] < Best['score']: Best = {'score':  Candidate['score'], 'path':path}

                    if Candidate['score'] < alpha: return Best

                    beta = min(beta, Candidate['score'])

            if stuck:

                return {'score': game_state.score, 'path': [99]}

        else: # terminal state or max depth

            return {'score': game_state.score, 'path': [99]}

        self.Best = Best

       # print(' ' * depth, depth, Best, Candidate)

        return Best

    def alpha_beta_sort_search(self, game_state, depth=1, alpha=-100000000, beta=100000000):

        def row_move(x):

            start, end = x[0], x[-1]

            return end[1] - start[1]

        hash_table = OrderedSet()

        player = self.counter if depth % 2 == 1 else -1 * self.counter
        min_max = 1 if depth % 2 == 1 else -1  # 1 means MAX and -1 means MIN
        sort_dir = False  if depth % 2 == 0 else True

        stuck = True

        if game_state.is_terminal() is False and (depth < self.MaxDepth):

            stuck = True

            Best = {'score': -20000000 * min_max}

            actions = game_state.getLegalActions(player)

            if len(actions) > 0:

                sorted_actions = sorted(actions, key=row_move, reverse=sort_dir)

                for path in sorted_actions:

                    stuck = False

                    successor = GameState(game_state)

                    successor.move_counter(path)

                    successor_hash = hash(successor)

                    if successor_hash not in hash_table:

                        hash_table.add(successor_hash)

                        Candidate = self.alpha_beta_search(successor, depth + 1, alpha, beta)

                        score = Candidate['score'] * self.counter

                        if min_max == 1:

                            if score > Best['score']: Best = {'score': score, 'path': path}

                            if score > beta: return Best

                            alpha = max(alpha, score)

                        if min_max == -1:

                            if score < Best['score']: Best = {'score': score, 'path': path}

                            if score < alpha: return Best

                            beta = min(beta, score)

            else:

                return {'score': game_state.score, 'path': [99]}

            if stuck:
                return {'score': game_state.score, 'path': [98]}

        else:  # terminal state or max depth

            return {'score': game_state.score, 'path': [99]}

        self.Best = Best

        # print(' ' * depth, depth, Best, Candidate)

        return Best

    def alpha_beta_sort_search_nostalemate(self, game_state, prior_states, depth=1, alpha=-100000000, beta=100000000):

        def row_move(x):

            start, end = x[0], x[-1]

            return end[1] - start[1]

        hash_table = OrderedSet()

        player = self.counter if depth % 2 == 1 else -1 * self.counter
        min_max = 1 if depth % 2 == 1 else -1  # 1 means MAX and -1 means MIN
        sort_dir = False  if depth % 2 == 0 else True

        stuck = True

        if game_state.is_terminal() is False and (depth < self.MaxDepth):

            stuck = True

            Best = {'score': -20000000 * min_max}

            actions = game_state.getLegalActions(player)

            sorted_actions = sorted(actions, key=row_move, reverse=sort_dir)

            for path in sorted_actions:

                stuck = True

                successor = GameState(game_state)

                successor.move_counter(path)

                successor_hash = hash(successor)

                if (successor_hash not in hash_table) and not(depth ==1 and successor_hash  in prior_states):

                    stuck = False

                    hash_table.add(successor_hash)

                    Candidate = self.alpha_beta_search(successor, depth + 1, alpha, beta)

                    score = Candidate['score'] * self.counter

                    if min_max == 1:

                        if score > Best['score']: Best = {'score': score, 'path': path}

                        if score > beta: return Best

                        alpha = max(alpha, score)

                    if min_max == -1:

                        if score < Best['score']: Best = {'score': score, 'path': path}

                        if score < alpha: return Best

                        beta = min(beta, score)

            if stuck:
                return {'score': game_state.score, 'path': [98]}

        else:  # terminal state or max depth

            return {'score': game_state.score, 'path': [99]}

        self.Best = Best

        return Best

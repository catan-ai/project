from copy import deepcopy
import consts
from dice import Dice
from player import Player, Road, Settlement
import itertools
import random

from draw import print_screen
import pygame
import math
import sys
import utils

MCTS_ITERS = 1
SIMULATE_DEPTH = 1
NEXT_PLAYER_SIM_ITERS = 1

class Node():
    """A lightweight tree node used only by Agent.mcts()."""
    __slots__ = ("board", "players", "player_turn",
                "parent", "action_taken",
                "children", "visits", "value", "untried_actions") # Use __slots__ to save on memory

    
    def __init__(self, board, players, parent=None, action_taken=None):
        self.board = board
        self.players = players #make sure passed in player is deep copied
        self.parent = parent # Parent node 
        self.action_taken = action_taken # action taken to get to this node
        self.children = []
        self.visits = 0
        self.value  = 0.0          # Cumulative reward

        self.untried_actions = self.players[0].getPossibleActions(
                                        self.board, self.players)

    def is_terminal(self) -> bool:
        return utils.get_winner(self.players) is not None
    
    def calculate_ucb(self, c: float) -> float:
        """
        Selection criteria for selecting next node. selects next node based on Upper-Confidence Bound
        (parent.visits is always ≥ this node's visits)
        """
        if self.visits == 0:
            return float("inf")
        return (self.value / self.visits) + \
                c * math.sqrt(math.log(self.parent.visits) / self.visits)
    
    def best_child(self, c:float):
        """
        Returns the child with maximum UCB  
        """
        
        bestchild = None
        bestchild_val = 0
        for child in self.children: 
            if child.calculate_ucb(c) > bestchild_val:
                bestchild = child
                bestchild_val = child.calculate_ucb(c)
        
        
        return bestchild 
    
    def add_child(self):
        """
        Pop one untried action, build successor state, return new node 
        """

        a = self.untried_actions.pop()

        current_player = self.players[0]
        next_board, next_player = current_player.stateActionTransition(self.board, current_player, self.players, a)

        next_players = deepcopy(self.players)
        next_players[0] = deepcopy(next_player)

        child = Node(next_board, next_players, self, a)

        self.children.append(child)
        return child 
    
    def simulate(self, depth: int = SIMULATE_DEPTH):
        """
        Simulate a random playout from this node to a terminal state or depth limit.
        """
        board = deepcopy(self.board)
        players = deepcopy(self.players)
        player_turn = 0
        while not self.is_terminal() and (depth := depth - 1) > 0:
            # Randomly select an action from possible actions
            actions = self.players[player_turn].getPossibleActions(board, players)
            action = random.choice(actions)

            # Simulate the action and get the new board and player state
            board, player = self.players[player_turn].stateActionTransition(self.board, self.players[player_turn], players, action)
            
            # Update the player to the "new" player
            players[player_turn] = player

        def calculate_player_points(player_turn):
            # Calculate the player's points
            points = players[player_turn].points

            # Check if the player has a longest road
            if players[player_turn].longest_road:
                points += 2

            # Check if the player has any development cards
            for card in players[player_turn].d_cards:
                if card.label == 'Point':
                    points += 1

            return points

        # Calculate agent's points
        points = calculate_player_points(player_turn)

        # Calculate the best other player's points
        other_player_points = []
        for i in range(len(players[1:])):
            other_player_points.append(calculate_player_points(i))

        # Calculate the difference between the agent's points and the best other player's points
        # Positive value means agent is winning, negative value means agent is losing
        return points - max(other_player_points)

# TODO
# - [ ] Write out testStateSpace.py to simulate 4 to 8 full turns to verify that the state action space functions work as intended
# - [ ] Write function buildSuccessorState(board, player, action) to build out the next state based on the player, board and action given 
# - [ ] Write function stateTransition_simulation(board, player) to simulate out one full turn after the ai player ends their turn to help with enumerating possible states to sample from  

class Action():
    """
        Possible names: 
        place_road 
        place_settlement
        place_city
        buy_dcard 
        play_yop 
        # play_knight 
        play_monopoly
        play_roadbuilder 
        end_turn 
    """
    def __init__(self, name, function=None, args={}):
        self.name = name
        self.function = function # function to call when action is taken
        self.args = args # args as a dictionary of arguments to pass to the function

    def do_action(self):
        if self.function is not None:
            return self.function(**self.args)
        else:
            raise ValueError("No function to call for action")
        
    def __str__(self):
        return f"Action(name={self.name})"
    
    def __repr__(self):
        return self.__str__()

class Agent(Player):
    def backpropagate(self, result: float, node: Node):
        while node is not None:
            node.visits += 1
            node.value += result
            node = node.parent

    def mcts(self, board, players):
        leaf = Node(board, players)

        time_remaining = MCTS_ITERS
        
        while (time_remaining := time_remaining - 1) > 0:
            # leaf <-- select(tree)
            # while not leaf.is_terminal() and len(leaf.untried_actions) == 0:
            #     # Select the best child node based on UCB
            #     leaf = leaf.best_child(1.0)
            # child = leaf.best_child(1.0)
            if len(leaf.untried_actions) == 0:
                leaf = leaf.best_child(1.0)
            # child <-- expand(leaf)
            if not leaf.is_terminal():
                leaf = leaf.add_child()
            # result <-- simulate(child)
            result = leaf.simulate()
            # backpropagate(result, child)
            self.backpropagate(result, leaf)

        # return the move (action) in Actions(state) whose node has highest number of playouts (visits)
        return max(leaf.children, key=lambda child: child.visits).action_taken
    
    def play_turn(self, board, players, simulate=False):
        # Copy the board and players to avoid modifying the original state
        # board = deepcopy(board)
        # players = deepcopy(players)

        action = None

        while action is None or action.name != "end_turn":
            # Get the possible actions for the player
            possible_actions = self.getPossibleActions(board, players)
            print("possible_actions", possible_actions) if len(possible_actions) > 1 else None

            # Pick an action from the possible actions
            action = self.pick_option(possible_actions, board, players, simulate)
            print("here") if len(possible_actions) > 1 else None
            # Perform the action
            action.do_action()

            print("\taction", action) if len(possible_actions) > 1 else None

            # Replace the player in the players list with the updated player
            for i, player in enumerate(players):
                if player.number == self.number:
                    players[i] = self
                    break

        # Return the board and player state after the action
        return board, players

    def pick_option(self, options, board, players, simulate=False):
        if simulate:
            return random.choice(options)

        # If only one option, return that option (like end turn, etc.)
        if len(options) == 1:
            return options[0]
        
        # She Monte on my Carlo til I Tree Search 
        action = self.mcts(board, players)
        return action

    def place_settlement(self, board, first, position=None):
        if position is None:
            choices = [num for num,pos in consts.SettlementPositions.items() if self.can_place_settlement(board, num, first)]
            choice = random.choice(choices)
        else:
            # Find settlement position and ensure they can place settlement
            choice = [num for num,pos in consts.SettlementPositions.items() if self.can_place_settlement(board, num, first) and pos == position][0]

        # Create settlement object and add to board
        settlement = Settlement(self, choice)
        board.settlements.append(settlement)
        self.settlements_left -= 1
        self.points += 1
        return settlement

    def place_road(self, board, settlement=None, position=None):
        if position is None:
            choices = []
            for num,pos in consts.RoadMidpoints.items():
                if pos not in [(road.start, road.end) for road in board.roads ]:
                        road = Road(self, num)
                        if settlement:
                            if road.start == settlement.position or road.end == settlement.position:
                                choices.append(road)
                        else:

                            roads_owned = [r for r in board.roads if r.color == self.color]
                            for test_r in roads_owned:
                                if road.start == test_r.start or test_r.end == road.end or road.start == test_r.end or road.end == test_r.start:
                                    choices.append(road)
                                    break

            # Randomly select a road from the available choices
            road = random.choice(choices)
        else:
            road = position

        board.roads.append(road)
        self.roads_left -= 1
        if self.roads_left <= 15 - 5:
            board.check_longest_road(self)

    def place_city(self, board, settlement=None):        
        if settlement is None:
            # Find a settlement to upgrade to a city
            choices = [settlement for settlement in board.settlements if settlement.player == self and settlement.city == False]
            settlement = random.choice(choices)
        settlement.make_city()

    def play_yop(self, board, resource1, resource2, card):
        self.play_d_card(card)

        if resource1 in self.hand:
            self.hand[resource1] += 1
        else:
            self.hand[resource1] = 1

        if resource2 in self.hand:
            self.hand[resource2] += 1
        else:
            self.hand[resource2] = 1      
    
    def play_monopoly(self, board, players, resourceType, card):
        self.play_d_card(card)

        # Collect all resources of a type from other players 
        for player in players:
            if player != self:
                if resourceType in player.hand and player.hand[resourceType] > 0:
                    amount_to_take = player.hand[resourceType]
                    self.hand[resourceType] += amount_to_take
                    player.hand[resourceType] = 0
        
    
    def play_roadbuilder(self, board, card, settle1, settle2, pos1, pos2):
        # Note that pos1 and pos2 are actual Roads, not positions
        self.play_d_card(card)

        # Allows player to place two free roads 
        self.place_road(board, settle1, pos1)
        self.place_road(board, settle2, pos2)
            

    def pick_tile_to_block(self, board, tile):
        num = consts.TilePositions.keys()[-1]

        for other_tile in board.tiles:
            other_tile.blocked = False
        tile.blocked = True
        settlements_blocking = consts.TileSettlementMap[num]
        players = []
        for settlement in board.settlements:
            if settlement.number in settlements_blocking and not settlement.player == self:
                players.append(settlement.player)
        players = list(set(players))
        return sorted(players, key=lambda player: player.number)
    
    def end_turn(self):
        return super().end_turn() # I think we can just do this 
    
    def getSuccessors(self, state):
        return

    # List(Actions) 
    def getPossibleActions(self, board, players):
        player = self
        # empty list to collect all possible actions
        list_of_actions = []

        # Use get_possible_purchases to get an idea of what purchases are available (road, city, settlement, dcard)
        possible_purchases = utils.get_possible_purchases(self, board, players, cancel=False)

        for purchase in possible_purchases:
            if purchase['label'] == 'city': # If we buy a city, upgrade the settlement
                for boardSettlement in board.settlements:
                    if boardSettlement.player == self and not boardSettlement.city:
                        # player = deepcopy(self)
                        list_of_actions.append(Action("place_city", args={"board": board, "settlement": boardSettlement}, function=player.place_city))
            elif purchase['label'] == 'settlement': # If we buy a settlement, check if we can place a settlement
                for settlementPos in consts.SettlementPositions:
                    if self.can_place_settlement(board, settlementPos, False):
                        # player = deepcopy(self)
                        list_of_actions.append(Action("place_settlement", args={"board": board, "first": False, "position": settlementPos}, function=player.place_settlement))
            elif purchase['label'] == 'road':

                # TODO: need to figure out how to establish whether there is a spot to put a road. the get_possible_purchases call above already accounts for whether the player has the resources to build a road, but it does not account for whether there is a spot to put the road (Note: this is probably a very very rare condition where you get "boxed in" by other players roads)

                roads = [(road.start, road.end) for road in board.roads ]
                for num,pos in consts.RoadMidpoints.items():
                    if pos not in roads:
                        road = Road(self, num)
                        roads_owned = [r for r in board.roads if r.color == self.color]
                        for test_r in roads_owned:
                            if road.start == test_r.start or test_r.end == road.end or road.start == test_r.end or road.end == test_r.start:
                                # action: place a road Road(aiPlayer, num)
                                # player = deepcopy(self)
                                list_of_actions.append(Action("place_road", args={"board": board, "settlement": None, "position": road}, function=player.place_road))
            elif purchase['label'] == 'd_card' and len(board.d_cards) > 0:
                # player = deepcopy(self)
                list_of_actions.append(Action("buy_dcard", args={"board": board}, function=player.pick_d_card))

        # Get possible development cards the player has in their hand to play
        # Note: cards in player.d_cards are valid cards to play (i.e. they were not bought on the current turn)
        # cards in player.d_cards_queue are cards that were bought this turn so they cannot be played until next turn
        # point cards cannot be played
        unique_player_dcards = set([card for card in self.d_cards if card.label != 'Point'])
                
        card_actions = [] 
        for card in unique_player_dcards:
            # Monopoly cards let you take all resources of a certain kind from all players
            if card.label == "Monopoly":
                # possible Monopoly actions are to select one of the four resource types to take
                for resource in consts.ResourceMap:
                    # player = deepcopy(self)
                    card_actions.append(Action("play_monopoly", args={"resourceType": resource, "card": card, "players": players}, function=player.play_monopoly))

            elif card.label == "Road Builder":
                # TODO: Possibly make this more efficient. I was lazy and did it naively
                # temporary board and aiPlayer to simulate different first road placements
                temp_board = deepcopy(board)
                temp_player = deepcopy(self)
                # simulate placing first of two roads
                roads1 = [(road.start, road.end) for road in board.roads ]
                for num,pos in consts.RoadMidpoints.items():
                    if pos not in roads1:
                        road1 = Road(self, num)
                        roads_owned1 = [r for r in board.roads if r.color == self.color]
                        for test_r1 in roads_owned1:
                            if road1.start == test_r1.start or test_r1.end == road1.end or road1.start == test_r1.end or road1.end == test_r1.start:
                                temp_player.place_road(temp_board, road1, road1)
                                
                                
                                # Now from this point simulate placing a second road
                                roads2 = [(road.start, road.end) for road in temp_board.roads ]
                                for num,pos in consts.RoadMidpoints.items():
                                    if pos not in roads2:
                                        road2 = Road(temp_player, num)
                                        roads_owned2 = [r for r in board.roads if r.color == temp_player.color]
                                        for test_r2 in roads_owned2:
                                            if road2.start == test_r2.start or test_r2.end == road2.end or road2.start == test_r2.end or road2.end == test_r2.start:    
                                                # player = deepcopy(self)
                                                card_actions.append(Action("roadbuilder", args={"card": card, "settle1": road1, "settle2": road2, "pos1": road1, "pos2": road2}, function=player.play_roadbuilder))


            # Year Of Plenty card lets you get any 2 resources for free
            elif card.label == "Year Of Plenty":
                # get all possible unique combos of 2 resources
                resource_combos = list(itertools.combinations_with_replacement(consts.ResourceMap, 2))
                for combo in resource_combos:
                    # player = deepcopy(self)
                    card_actions.append(Action("play_yop", args={"resource1": combo[0], "resource2": combo[1], "card": card}, function=player.play_yop))

        # if there are cards to play and the agent has not already played a card this round, add all possible card actions
        if len(card_actions) > 0 and not self.played_d_card:
            list_of_actions.extend(card_actions)

        # Last possible action of every "turn" is to end the turn
        # player = deepcopy(self)
        list_of_actions.append(Action("end_turn", function=player.end_turn))

        return list_of_actions
    
        
    def buildSuccessorState(self, board, player, action):
        """
        Take in the current board and player state, along with an action, and return the updated board/player state AFTER the action.
        """

        # Copies of the current board and player state so we can modify them 
        new_board = deepcopy(board)
        new_player = deepcopy(player)

        # Arguments associated with the action function 
        action.args["board"] = new_board

        # print(action.name) if action.name != "end_turn" else None

        action.do_action()  # Will call the function associated with the action 

        # Return board, player state AFTER the action 
        return new_board, new_player
    
    def stateTransitionSimulation(self, board, player, players):
        size = consts.SCREEN_SIZE
        screen = pygame.display.set_mode(size)
        new_board = deepcopy(board)
        new_player = deepcopy(player)
        new_players = deepcopy(players)

        player.end_turn()
        player_turn = (player.number + 1) % 4
        dice = Dice()
        first_turn = False
        winner = None
        while winner is None and player_turn != 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            comp_player = new_players[player_turn]
            comp_player.start_turn()
            def get_buttons(total = None):
                buttons = [
                        {
                            'label': 'End Turn',
                            'action': utils.end_turn,
                        }
                ]
                possible_purchases = utils.get_possible_purchases(comp_player, new_board, deepcopy(new_players), screen)

                def make_purchase():
                    return possible_purchases, 'Buy:'

                if len(possible_purchases) > 1:
                    buttons.append({
                        'label': 'Make Purchase',
                        'action': make_purchase
                    })
                d_cards = [{'label': card.label, 'action': card.make_action(screen, new_board, new_players, comp_player)} for card in comp_player.d_cards if card.label != 'Point'] 
                def play_d_card():
                    return d_cards + [{'label': 'cancel', 'action': lambda: ([], None)}], 'Which Card: '

                exchanges = comp_player.get_exchanges(screen, new_board, new_players)
                def exchange():
                    return exchanges + [{'label': 'cancel', 'action': lambda: ([], None)}], 'Exhange: '

                if exchanges:
                    buttons.append({
                        'label': 'Exchange',
                        'action': exchange,
                    })

                if d_cards and not comp_player.played_d_card:
                    buttons.append({
                        'label': 'Play D Card',
                        'action': play_d_card
                    })
                if total:
                    return buttons, 'Player ' + str(comp_player.number) + ', You Rolled: ' + str(total)
                else:
                    return buttons, 'Player ' + str(comp_player.number) + ': '

            def roll_dice():
                total = sum(dice.roll())
                utils.give_resources(new_board, total)
                return get_buttons(total)
            buttons = [{
                'label': 'Roll Dice',
                'action': roll_dice
            }]

            label = 'Player %s\'s Turn' % comp_player.number
            while buttons:
                print_screen(screen, new_board, label, new_players, buttons)
                option = comp_player.pick_option(buttons, board, players, True)
                buttons, label = option['action']()
                if not buttons and label != 'end':
                    buttons, label = get_buttons()
            comp_player.end_turn()
            player_turn = (player_turn + 1) % 4
            if player_turn == 0:
                first_turn = False
            winner = utils.get_winner(new_players)
        # print_screen(screen, new_board, 'Player ' + str(winner.number) + ' Wins!', new_players)
        # while True:
        #     event = pygame.event.wait()
        #     if event.type == pygame.QUIT:
        #         sys.exit()
        
        return (new_board, new_player)


    # State 
    def stateActionTransition(self, board, player, players, action: Action):
        
        # If the Action is deterministic (building anything or playing a monopoly, year of plenty, or road builder dcard)
        if (action.name in ["place_road", "place_city", "place_settlement", "play_monopoly", "play_yop", "play_roadbuilder"]):
            # Assuming that State is a combination of player (including recources and d_cards) and board objects,
            # buildSuccessorState will take the action and update these two objects and return the resulting objects
            # TODO: Implement buildSuccessorState
            board, player = self.buildSuccessorState(board, player, action)
            return board, player
        
        elif (action.name == "buy_dcard"):
            # get all cards in the dcard list for the board
            available_dcards = board.d_cards
            total_dcards = len(available_dcards)

            num_cards = {
                # "Knight": 0,
                "Point": 0,
                "Monopoly": 0,
                "Road Builder": 0,
                "Year Of Plenty": 0
            }

            for card in available_dcards:
                num_cards[card.label] += 1
            
            card_labels = list(num_cards.keys())
            weights = list(num_cards.values())

            sampled_label = random.choices(card_labels, weights=weights, k=1)[0]

            # Find and remove the first matching card with that label
            for i, card in enumerate(board.d_cards):
                if card.label == sampled_label:
                    sampled_card = board.d_cards.pop(i)  # remove and retrieve it
                    break

            player.d_card_queue.append(sampled_card)
            return board, player


        # elif action.name == "play_knight":
        #     # TODO: IMPLEMENT ROBBER STATE ACTION TRANSITION
        #     return board, player

        elif action.name == "end_turn":
            # For end turn, we have to consider the next state stochastically because of the options of other players.
            # We will handle next state by doing a "black box" sample from the environment's state transition function.
            # This means we will have a function that will take in current state, and generate a possible the next state
            # by simulating all the computer players action and stopping before our next dice roll

            # empty list that will be populated with board states to sample from 
            sample_space = []
            for _ in range(NEXT_PLAYER_SIM_ITERS):
                # TODO: Implement stateTransition_simulation
                sample_space.append(self.stateTransitionSimulation(board, player, players))

            # Return the sample
            return random.choice(sample_space)

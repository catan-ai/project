from copy import deepcopy
from typing import List
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

MCTS_ITERS = 10
SIMULATE_DEPTH = 2
NEXT_PLAYER_SIM_ITERS = 2

# Note some of the MCTS related code was inspired by https://ai-boson.github.io/mcts/ (mostly once we had an initial version and then had to fix hideous insects)

class Node():
    """A lightweight tree node used only by Agent.mcts()."""
    __slots__ = ("board", "players", "player_turn",
                "parent", "action_taken",
                "children", "visits", "value", "untried_actions") # Use __slots__ to save on memory

    
    def __init__(self, board, players, parent=None, action_taken=None):
        self.board = board
        self.players: List[Player] = players #make sure passed in player is deep copied
        self.parent: Node = parent # Parent node 
        self.action_taken: Action = action_taken # action taken to get to this node
        self.children: List[Node] = []
        self.visits = 0
        self.value  = 0.0          # Cumulative reward

        self.untried_actions = self.players[0].getPossibleActions(
                                        self.board, self.players)

    def __str__(self):
        return f"Node(board={self.board}, players={self.players}, action_taken={self.action_taken}, visits={self.visits}, value={self.value}, untried_actions={self.untried_actions}, children={len(self.children)})"
    
    def __repr__(self):
        return self.__str__()

    def is_terminal(self) -> bool:
        return utils.get_winner(self.players) is not None
    
    def is_fully_expanded(self) -> bool:
        """
        Check if all possible actions have been tried from this node.
        """
        return len(self.untried_actions) == 0
    
    def calculate_ucb(self, c: float) -> float:
        """
        Selection criteria for selecting next node. selects next node based on Upper-Confidence Bound
        (parent.visits is always ≥ this node's visits)
        """
        if self.visits == 0:
            return float("inf")
        return (self.value / self.visits) + \
                c * math.sqrt(math.log(self.parent.visits) / self.visits)
    
    def best_child(self, c: float = 1.0):
        """
        Returns the child with maximum UCB  
        """
        
        bestchild = self.children[0]
        bestchild_val = float("-inf")
        for child in self.children: 
            if child.calculate_ucb(c) > bestchild_val:
                bestchild = child
                bestchild_val = child.calculate_ucb(c)
        
        
        return bestchild 
    
    def expand(self):
        """
        Pop one untried action, build successor state, return new node 
        """

        # Randomly select an action from the untried actions, remove it from the list
        a = random.choice(self.untried_actions)
        self.untried_actions.remove(a)

        current_player: Agent = self.players[0]
        next_board, next_player = current_player.stateActionTransition(deepcopy(self.board), deepcopy(current_player), deepcopy(self.players), a)

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
        while not utils.get_winner(players) and (depth := depth - 1) > 0:
            # Randomly select an action from possible actions
            actions = players[player_turn].getPossibleActions(board, players)
            action = random.choice(actions)

            # Simulate the action and get the new board and player state
            board, player = players[player_turn].stateActionTransition(board, players[player_turn], players, action)
            
            # Update the player to the "new" player
            players[player_turn] = player

        def calculate_player_points(num):
            # Calculate the player's points
            points = players[num].points

            # Check if the player has a longest road
            if players[num].longest_road:
                points += 2

            # Check if the player has any development cards
            points += len([card for card in players[num].d_cards if card.label == 'Point'])

            return points

        # Calculate agent's points
        points = calculate_player_points(player_turn)

        # Calculate the best other player's points
        max_other = max(calculate_player_points(i+1) for i in range(len(players[1:])))

        # Calculate the difference between the agent's points and the best other player's points
        # Positive value means agent is winning, negative value means agent is losing
        return points - max_other

    def select(self):
        """
        Select a node from the tree using UCB.
        """
        # Traverse the tree until we reach a leaf node
        current_node = self
        while not current_node.is_terminal():
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node
    
    def print_tree(self, depth=0):
        """
        Print the tree for debugging purposes, starting from this node.
        """
        print("\t" * depth + str(self))
        for child in self.children:
            child.print_tree(depth + 1)

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
        make_exchange
        end_turn 
    """
    def __init__(self, name, function=None, args={}):
        self.name = name
        self.function = function # function to call when action is taken
        self.args = args # args as a dictionary of arguments to pass to the function

    def do_action(self, player=None):
        # If player is not None and not already set in args, set the player in the args
        if player is not None and "player" not in self.args:
            self.args["player"] = player

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
        root = Node(board, players)
        leaf = root
        
        for _ in range(MCTS_ITERS):
            # leaf <-- select(tree)
            #     Note that this also expands the tree when it finds a node that is not fully expanded
            leaf = leaf.select()
            # result <-- simulate(child)
            result = leaf.simulate()
            # backpropagate(result, child)
            self.backpropagate(result, leaf)

        # Select the best child of the root node
        return root.best_child(0.0).action_taken
    
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
            # Perform the action
            action.do_action(self)

            print("\taction", action) if len(possible_actions) > 1 else None

            # Replace the player in the players list with the updated player
            players[self.number - 1] = self

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
    
    def exchange(self, board, r1, r2, amt1, amt2, player=None):
        player = self if player is None else player
        if player.hand.get(r1, 0) + amt1 < 0:
            raise ValueError(f"Not enough {consts.ResourceMap[r1]} to perform the exchange. Have {player.hand.get(r1, 0)}, need {-amt1}.")
        player.hand[r1] += amt1
        player.hand[r2] += amt2

    def place_settlement(self, board, first, position=None, player=None):
        player = self if player is None else player
        if position is None:
            choices = [num for num,pos in consts.SettlementPositions.items() if player.can_place_settlement(board, num, first)]
            choice = random.choice(choices)
        else:
            # Find settlement position and ensure they can place settlement
            choice = [num for num,pos in consts.SettlementPositions.items() if player.can_place_settlement(board, num, first) and pos == position][0]

        # Create settlement object and add to board
        settlement = Settlement(player, choice)
        board.settlements.append(settlement)
        player.settlements_left -= 1
        player.points += 1
        return settlement

    def place_road(self, board, settlement=None, position=None, player=None):
        player = self if player is None else player
        if position is None:
            choices = []
            for num,pos in consts.RoadMidpoints.items():
                if pos not in [(road.start, road.end) for road in board.roads ]:
                        road = Road(player, num)
                        if settlement:
                            if road.start == settlement.position or road.end == settlement.position:
                                choices.append(road)
                        else:

                            roads_owned = [r for r in board.roads if r.color == player.color]
                            for test_r in roads_owned:
                                if road.start == test_r.start or test_r.end == road.end or road.start == test_r.end or road.end == test_r.start:
                                    choices.append(road)
                                    break

            # Randomly select a road from the available choices
            road = random.choice(choices)
        else:
            road = position

        board.roads.append(road)
        player.roads_left -= 1
        if player.roads_left <= 15 - 5:
            board.check_longest_road(player)

    def place_city(self, board, settlement=None, player=None):
        player = self if player is None else player
        if settlement is None:
            # Find a settlement to upgrade to a city
            choices = [settlement for settlement in board.settlements if settlement.player == player and settlement.city == False]
            settlement = random.choice(choices)
        settlement.make_city()

    def play_yop(self, board, resource1, resource2, card, player=None):
        player = self if player is None else player
        player.play_d_card(card)

        if resource1 in player.hand:
            player.hand[resource1] += 1
        else:
            player.hand[resource1] = 1

        if resource2 in player.hand:
            player.hand[resource2] += 1
        else:
            player.hand[resource2] = 1      
    
    def play_monopoly(self, board, players, resourceType, card, player=None):
        p = self if player is None else player
        p.play_d_card(card)

        # Collect all resources of a type from other players 
        for player in players:
            if player != p:
                if resourceType in player.hand and player.hand[resourceType] > 0:
                    amount_to_take = player.hand[resourceType]
                    p.hand[resourceType] += amount_to_take
                    player.hand[resourceType] = 0
        
    def play_roadbuilder(self, board, card, settle1, settle2, pos1, pos2, player=None):
        player = self if player is None else player

        # Note that pos1 and pos2 are actual Roads, not positions
        player.play_d_card(card)

        # Allows player to place two free roads 
        player.place_road(board, settle1, pos1)
        player.place_road(board, settle2, pos2)
            
    def end_turn(self, player=None):
        player = self if player is None else player

        player.d_cards += player.d_card_queue
        player.d_card_queue = []

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

        # Get possible exchanges the player can make
        exchanges = []
        settlements = [settlement for settlement in board.settlements if settlement.player == player]
        ports = [consts.Ports.get(settlement.number) for settlement in settlements if consts.Ports.get(settlement.number)]
        for resource in player.hand:
            if player.hand[resource] >= 2:
                if player.has_port(ports, resource):
                    exchanges.extend([Action("make_exchange", args={"r1": resource, "amt1": -2, "r2": r, "amt2": 1}, function=player.exchange) for r in player.hand])
                    break
            if player.hand[resource] >= 3:
                if self.has_port(ports):
                    exchanges.extend([Action("make_exchange", args={"r1": resource, "amt1": -3, "r2": r, "amt2": 1}, function=player.exchange) for r in player.hand])
                    break
            if player.hand[resource] >= 4:
                    exchanges.extend([Action("make_exchange", args={"r1": resource, "amt1": -4, "r2": r, "amt2": 1}, function=player.exchange) for r in player.hand])
        # if there are exchanges to make, add them to the list of actions
        if len(exchanges) > 0:
            list_of_actions.extend(exchanges)

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
                                                card_actions.append(Action("play_roadbuilder", args={"card": card, "settle1": road1, "settle2": road2, "pos1": road1, "pos2": road2}, function=player.play_roadbuilder))


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
    
        
    def buildSuccessorState(self, board, player, action: Action):
        """
        Take in the current board and player state, along with an action, and return the updated board/player state AFTER the action.
        """

        # Copies of the current board and player state so we can modify them 
        new_board = deepcopy(board)
        new_player = deepcopy(player)

        # Arguments associated with the action function 
        action.args["board"] = new_board

        # print(action.name) if action.name != "end_turn" else None

        action.do_action(new_player)  # Will call the function associated with the action 

        # Return board, player state AFTER the action 
        return new_board, new_player
    
    def stateTransitionSimulation(self, board, player, players):
        size = consts.SCREEN_SIZE
        screen = pygame.display.set_mode(size)
        new_board = deepcopy(board)
        new_players = deepcopy(players)

        new_players[0].end_turn()
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
        
        return new_board, new_players[0]


    # State 
    def stateActionTransition(self, board, player, players, action: Action):
        
        # If the Action is deterministic (building anything or playing a monopoly, year of plenty, or road builder dcard)
        if (action.name in ["place_road", "place_city", "place_settlement", "play_monopoly", "play_yop", "play_roadbuilder", "make_exchange"]):
            # Assuming that State is a combination of player (including recources and d_cards) and board objects,
            # buildSuccessorState will take the action and update these two objects and return the resulting objects
            board, player = self.buildSuccessorState(board, player, action)
            return board, player
        
        elif (action.name == "buy_dcard"):
            # get all cards in the dcard list for the board
            available_dcards = board.d_cards

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

        elif action.name == "end_turn":
            # For end turn, we have to consider the next state stochastically because of the options of other players.
            # We will handle next state by doing a "black box" sample from the environment's state transition function.
            # This means we will have a function that will take in current state, and generate a possible the next state
            # by simulating all the computer players action and stopping before our next dice roll

            # empty list that will be populated with board states to sample from 
            sample_space = []
            for _ in range(NEXT_PLAYER_SIM_ITERS):
                sample_space.append(self.stateTransitionSimulation(board, player, players))

            # Return the sample
            return random.choice(sample_space)
        
        else:
            raise ValueError(f"Action {action.name} does not have a defined state transition function.")

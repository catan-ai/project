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

        self.untried_actions = self.getPossibleActions(
                                        self.board, self.players)

        def is_terminal(self) -> bool:
            return utils.get_winner(self.players) is not None





        




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
            self.function(**self.args)
        else:
            raise ValueError("No function to call for action")

class Agent(Player):

    def mcts(self, board, players):
        # TODO fill in MCTS
        return
        return action

    def pick_option(self, options, board, players):
        # If only one option, return that option (like roll dice, end turn, etc.)
        if len(options) == 1:
            return options[0]
        
        # Something about Monte (money) Carlo Tree Search

        # She Monte on my Carlo til I Tree Search 

        # Get resource cards, updating hand
        return self.mcts(board, players)
        
        # Call getSuccessors from 

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

    def place_city(self, board, settlement):        
        settlement.make_city()

    def play_yop(self, board, resource1, resource2, card):
        self.play_d_card(card)
        
        self.hand[resource1] += 1
        self.hand[resource2] += 1        
    
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

        # empty list to collect all possible actions
        list_of_actions = []

        # Use get_possible_purchases to get an idea of what purchases are available (road, city, settlement, dcard)
        possible_purchases = utils.get_possible_purchases(player, board, players)

        for purchase in possible_purchases:
            if purchase['label'] == 'city': # If we buy a city, upgrade the settlement
                for boardSettlement in board.settlements:
                    if boardSettlement.player == self and not boardSettlement.city:
                        player = deepcopy(self)
                        list_of_actions.append(Action("place_city", args={"board": board, "player": player, "settlement": boardSettlement}, function=player.place_city))
            if purchase['label'] == 'settlement': # If we buy a settlement, check if we can place a settlement
                for settlementPos in consts.SettlementPositions:
                    if self.can_place_settlement(board, settlementPos, False):
                        player = deepcopy(self)
                        list_of_actions.append(Action("place_settlement", args={"board": board, "player": player, "first": False, "position": settlementPos}, function=player.place_settlement))
            if purchase['label'] == 'road':

                # TODO: need to figure out how to establish whether there is a spot to put a road. the get_possible_purchases call above already accounts for whether the player has the resources to build a road, but it does not account for whether there is a spot to put the road (Note: this is probably a very very rare condition where you get "boxed in" by other players roads)

                roads = [(road.start, road.end) for road in board.roads ]
                for num,pos in consts.RoadMidpoints.items():
                    if pos not in roads:
                        road = Road(self, num)
                        roads_owned = [r for r in board.roads if r.color == self.color]
                        for test_r in roads_owned:
                            if road.start == test_r.start or test_r.end == road.end or road.start == test_r.end or road.end == test_r.start:
                                # action: place a road Road(aiPlayer, num)
                                player = deepcopy(self)
                                list_of_actions.append(Action("place_road", args={"board": board, "player": player, "settlement": None, "position": road}, function=player.place_road))
            if purchase['label'] == 'd_card' and len(board.d_cards) > 0:
                player = deepcopy(self)
                list_of_actions.append(Action("buy_dcard", args={"board": board}, function=player.pick_d_card))

        # Get possible development cards the player has in their hand to play
        # Note: cards in player.d_cards are valid cards to play (i.e. they were not bought on the current turn)
        # cards in player.d_cards_queue are cards that were bought this turn so they cannot be played until next turn
        # point cards cannot be played
        unique_player_dcards = set()
        for card in player.d_cards:
            if card.label != 'Point' and card not in unique_player_dcards:
                unique_player_dcards.add(card)
                
        card_actions = [] 

        for card in unique_player_dcards:
            # if card.label == "Knight":
            #     for num, pos in consts.TilePositions.items():
            #         tile = board.tiles[num]
            #         if tile.resource is not None and not tile.blocked:
            #             settlements_blocking = consts.TileSettlementMap[num]
            #             players = []
            #             for settlement in board.settlements:
            #                 if settlement.number in settlements_blocking and not settlement.player == self:
            #                     players.append(settlement.player)
            #             players = list(set(players))
            #             players_list = sorted(players, key=lambda player: player.number)
            #             for curplayer in players_list:
            #                 player = deepcopy(self)
            #                 card_actions.append(Action("play_knight")) # TODO: pass args and function
            # Monopoly cards let you take all resources of a certain kind from all players
            if card.label == "Monopoly":
                # possible Monopoly actions are to select one of the four resource types to take
                for resource in consts.ResourceMap:
                    player = deepcopy(self)
                    card_actions.append(Action("play_monopoly", args={"resourceType": resource, "card": card, "players": players}, function=player.play_monopoly))

            if card.label == "Road Builder":
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
                            if road.start == test_r1.start or test_r1.end == road.end or road.start == test_r1.end or road.end == test_r1.start:
                                temp_player.place_road(temp_board)
                                
                                
                                # Now from this point simulate placing a second road
                                roads2 = [(road.start, road.end) for road in temp_board.roads ]
                                for num,pos in consts.RoadMidpoints.items():
                                    if pos not in roads2:
                                        road2 = Road(temp_player, num)
                                        roads_owned2 = [r for r in board.roads if r.color == temp_player.color]
                                        for test_r2 in roads_owned2:
                                            if road.start == test_r2.start or test_r2.end == road.end or road.start == test_r2.end or road.end == test_r2.start:    
                                                player = deepcopy(self)
                                                card_actions.append(Action("roadbuilder", args={"card": card, "settle1": road1, "settle2": road2, "pos1": road1, "pos2": road2}, function=player.play_roadbuilder)) # TODO: not 100% sure arguments are correct here


            # Year Of Plenty card lets you get any 2 resources for free
            if card.label == "Year Of Plenty":
                # get all possible unique combos of 2 resources
                resource_combos = list(itertools.combinations_with_replacement(consts.ResourceMap, 2))
                for combo in resource_combos:
                    player = deepcopy(self)
                    card_actions.append(Action("play_yop", args={"resource1": combo[0], "resource2": combo[1], "card": card}, function=player.play_yop))

        # if there are cards to play and the agent has not already played a card this round, add all possible card actions
        if len(card_actions) > 0 and not self.played_d_card:
            list_of_actions.extend(card_actions)

        # Last possible action of every "turn" is to end the turn
        player = deepcopy(self)
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
        action.args["player"] = new_player

        action.do_action()  # Will call the function associated with the action 

        # Return board, player state AFTER the action 
        return new_board, new_player
    
    def stateTransitionSimulation(board, player, players, screen):
        new_board = deepcopy(board)
        new_player = deepcopy(player)
        new_players = deepcopy(players)

        player.end_turn()
        player_turn = (player_turn + 1) % 4
        dice = Dice()
        
        
        first_turn = False
        winner = None
        while winner is None and player.number != 1:
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
                possible_purchases = utils.get_possible_purchases(comp_player, new_board, new_players)

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
                if total == 7:
                    if first_turn:
                        while total == 7:
                            total = sum(dice.roll())
                    else:
                        for p in new_players:
                            if sum([p.hand[resource] for resource in p.hand]) > 7:
                                original = sum([p.hand[resource] for resource in p.hand])
                                needed_left = math.ceil(original / 2)
                                while sum([p.hand[resource] for resource in p.hand]) > needed_left:
                                    resources = [resource for resource in p.hand if p.hand[resource]]
                                    resources = list(set(resources))
                                    buttons = [{
                                            'resource': resource,
                                            'label': consts.ResourceMap[resource],
                                    } for resource in resources]
                                    options = print_screen(screen, new_board, 'Player ' + str(p.number) + ' Pick a resource to give away', new_players, buttons)
                                    resource_chosen = p.pick_option(buttons)
                                    p.hand[resource_chosen['resource']] -= 1

                        print_screen(screen, new_board, 'Player ' + str(comp_player.number) + ' rolled a 7. Pick a settlement to Block', new_players)
                        players_blocked = comp_player.pick_tile_to_block(new_board)
                        buttons = [
                                {
                                    'label': 'Player ' + str(player_blocked.number),
                                    'player': player_blocked
                                } for player_blocked in players_blocked
                        ]
                        if buttons:
                            print_screen(screen, new_board, 'Take a resource from:', new_players, buttons)
                            player_chosen = comp_player.pick_option(buttons)
                            player_chosen['player'].give_random_to(comp_player)

                utils.give_resources(new_board, total)
                return get_buttons(total)
            buttons = [{
                'label': 'Roll Dice',
                'action': roll_dice
            }]

            label = 'Player %s\'s Turn' % comp_player.number
            while buttons:
                print_screen(screen, new_board, label, new_players, buttons)
                option = comp_player.pick_option(buttons)
                buttons, label = option['action']()
                if not buttons and label != 'end':
                    buttons, label = get_buttons()
            comp_player.end_turn()
            player_turn = (player_turn + 1) % 4
            if player_turn == 0:
                first_turn = False
            winner = utils.get_winner(new_players)
        print_screen(screen, new_board, 'Player ' + str(winner.number) + ' Wins!', new_players)
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                sys.exit()
        
        return (new_board, new_player)


    # State 
    def stateActionTransition(self, board, player, action: Action):
        # If the Action is deterministic (building anything or playing a monopoly, year of plenty, or road builder dcard)
        if (action.name in ["place_road", "place_city", "place_settlement", "play_monopoly", "play_yop", "play_roadbuilder"]):
            # Assuming that State is a combination of player (including recources and d_cards) and board objects,
            # buildSuccessorState will take the action and update these two objects and return the resulting objects

            # TODO: Implement buildSuccessorState
            board, player = self.buildSuccessorState(board, player, action)
            return board, player

        elif (action.name == "buy_dcard"):
            # get all cards in the dcard list for the board
            available_dcards = board.dcards
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
            for i, card in enumerate(board.dcards):
                if card.label == sampled_label:
                    sampled_card = board.dcards.pop(i)  # remove and retrieve it
                    break

            player.d_card_queue.append(sampled_card)
            board, player = None # new state from adding the sampled card to the player's hand
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
            for i in range(1000):
                # TODO: Implement stateTransition_simulation
                sample_space.append(self.stateTransitionSimulation(board, player))

            # random number for sample
            random_number = random.randint(1000)

            # Return the sample
            return sample_space[random_number]

from copy import deepcopy
import game
import player
import consts
from board import Board
from draw import print_screen
from dice import Dice
from player import Player, ComputerPlayer, Road, Settlement
import itertools
import random


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
        play_knight 
        play_monopoly
        play_roadbuilder 
        end_turn 
    """
    def __init__(self, name, function=None, args=None):
        self.name = name
        self.function = function
        self.args = args

    def do_action(self):
        if self.function is not None:
            self.function(self.args)
        else:
            print(f"Action {self.name} has no function assigned to it.")
            return False
        return True


class Agent(Player):
    def pick_option(self, options):
        # If only one option, return that option (like roll dice, end turn, etc.)
        if len(options) == 1:
            return options[0]
        # Something about Monte (money) Carlo Tree Search

        # Get resource cards, updating hand
        
        # Call getSuccessors from 

    def place_settlement(self, board, first, position):
        # Find settlement position and ensure they can place settlement
        choice = [num for num,pos in consts.SettlementPositions.items() if self.can_place_settlement(board, num, first) and pos == position][0]

        # Create settlement object and add to board
        settlement = Settlement(self, choice)
        board.settlements.append(settlement)
        self.settlements_left -= 1
        self.points += 1
        return settlement

    def place_road(self, board, settlement=None, position=None):
        board.roads.append(position)
        self.roads_left -= 1
        if self.roads_left <= 15 - 5:
            board.check_longest_road(self)

    def place_city(self, board, settlement):        
        settlement.make_city()

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
    
    def getSuccessors(self, state):
        return

    # List(Actions) 
    def getPossibleActions(self, board):

        # empty list to collect all possible actions
        list_of_actions = []

        # Use get_possible_purchases to get an idea of what purchases are available (road, city, settlement, dcard)
        possible_purchases = game.get_possible_purchases(player, board, players)

        for purchase in possible_purchases:
            if purchase['label'] == 'city': # If we buy a city, upgrade the settlement
                for boardSettlement in board.settlements:
                    if boardSettlement.player == self and not boardSettlement.city:
                        list_of_actions.append(Action("place_city"))
            if purchase['label'] == 'settlement': # If we buy a settlement, check if we can place a settlement
                for settlementPos in consts.SettlementPositions:
                    if self.can_place_settlement(board, settlementPos, False):
                        list_of_actions.append(Action("place_settlement"))
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
                                list_of_actions.append(Action("place_road") )
            if purchase['label'] == 'd_card' and len(board.d_cards) > 0:
                list_of_actions.append(Action("buy_dcard") )

            list_of_actions.append(Action("buy_dcard"))

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
            if card.label == "Knight":
                for num, pos in consts.TilePositions.items():
                    tile = board.tiles[num]
                    if tile.resource is not None and not tile.blocked:
                        settlements_blocking = consts.TileSettlementMap[num]
                        players = []
                        for settlement in board.settlements:
                            if settlement.number in settlements_blocking and not settlement.player == self:
                                players.append(settlement.player)
                        players = list(set(players))
                        players_list = sorted(players, key=lambda player: player.number)
                        for curplayer in players_list:
                            card_actions.append(Action("play_knight"))
            # Monopoly cards let you take all resources of a certain kind from all players
            if card.label == "Monopoly":
                # possible Monopoly actions are to select one of the four resource types to take
                for resource in consts.ResourceMap:
                    card_actions.append(Action("play_monopoly"))

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
                                                card_actions.append(Action("roadbuilder"))


            # Year Of Plenty card lets you get any 2 resources for free
            if card.label == "Year Of Plenty":
                # get all possible unique combos of 2 resources
                resource_combos = list(itertools.combinations_with_replacement(consts.ResourceMap, 2))
                for combo in resource_combos:
                    card_actions.append(Action("play_yop"))

        # if there are cards to play and the agent has not already played a card this round, add all possible card actions
        if len(card_actions) > 0 and not self.played_d_card:
            list_of_actions.extend(card_actions)

        # Last possible action of every "turn" is to end the turn
        list_of_actions.append(Action(name="end_turn"))

        return list_of_actions
    
        
    def buildSuccessorState(self, board, player, action):
        """
        Take in the current board and player state, along with an action, and return the updated board/player state AFTER the action.
        """

        new_board = deepcopy(board)
        new_player = deepcopy(player)

        action.do_action()  # Will call the function associated with the action 

        # Need to modify the board and player based on action taken 
        # Is this going to be handled by the action function itself, or do we need to handle it here? 
        
        return


    # State 
    def stateActionTransition(self, board, player, action: Action):
        # If the Action is deterministic (building anything or playing a monopoly, year of plenty, or road builder dcard)
        if (action.name in ["place_road", "place_city", "place_settlement", "play_monopoly", "play_yop", "play_roadbuilder"]):
            # Assuming that State is a combination of player (including recources and d_cards) and board objects,
            # buildSuccessorState will take the action and update these two objects and return the resulting objects

            # TODO: Implement buildSuccessorState
            board, player = buildSuccessorState(board, player, action)
            return board, player

        elif (action.name == "buy_dcard"):
            # get all cards in the dcard list for the board
            available_dcards = board.dcards
            total_dcards = len(available_dcards)

            num_cards = {
                "Knight": 0,
                "Point": 0,
                "Monopoly": 0,
                "Road Builder": 0,
                "Year Of Plenty": 0
            }

            for card in available_dcards:
                num_cards[card.label] += 1
            
            card_labels = list(num_cards.keys())
            weights = list(num_cards.values())

            sampled_card = random.choices(card_labels, weights=weights, k=1)[0]

            board, player = None # new state from adding the sampled card to the player's hand
            return board, player


        elif action.name == "play_knight":
            # TODO: IMPLEMENT ROBBER STATE ACTION TRANSITION
            return board, player

        elif action.name == "end_turn":
            # For end turn, we have to consider the next state stochastically because of the options of other players.
            # We will handle next state by doing a "black box" sample from the environment's state transition function.
            # This means we will have a function that will take in current state, and generate a possible the next state
            # by simulating all the computer players action and stopping before our next dice roll

            # empty list that will be populated with board states to sample from 
            sample_space = []
            for i in range(1000):
                # TODO: Implement stateTransition_simulation
                sample_space.append(stateTransition_simulation(board, player))

            # random number for sample
            random_number = random.randint(1000)

            # Return the sample
            return sample_space[random_number]
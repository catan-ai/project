# From https://github.com/damargulis/catan/
# Any modifications will be noted via comments and commits

import consts
from draw import print_screen
import math
import pygame
import random
import sys

# Represents a player in the game 
class Player(object):
    def __init__(self, number):
        # Player ID and color 
        self.number = number
        self.color = consts.PlayerColors[number]

        # Player resources, initialized to zero 
        self.hand = {
                consts.Resource.BRICK: 0,
                consts.Resource.LUMBER: 0,
                consts.Resource.WOOL: 0,
                consts.Resource.GRAIN: 0,
                consts.Resource.ORE: 0,
        }
        # Other player stats, including development cards, roads, settlements, and cities 
        self.d_cards = []
        self.points = 0
        self.settlements_left = 5
        self.roads_left = 15
        self.cities_left = 4
        #self.longest_road = 0 # Don't know why they left this in 
        self.knights = 0
        self.longest_road = False
        self.largest_army = False

        # Initialize a queue for player development cards
        self.played_d_card = False
        self.d_card_queue = []

    # Add resource to player's hand 
    def take_resource(self, resource):
        self.hand[resource] += 1

    # Start a player turn, reset the development card flag 
    def start_turn(self):
        self.played_d_card = False

    # Play a development card, remove it from the player's hand and set the flag
    def play_d_card(self, card):
        self.d_cards.remove(card)
        self.played_d_card = True

    # End the player's turn, add any queued development cards to the player's hand
    def end_turn(self):
        self.d_cards += self.d_card_queue
        self.d_card_queue = []

    # Check if the player can afford a given item, based on the player's resources 
    def can_afford(self, item):
        for resource in consts.Costs[item]:
            if self.hand[resource] < consts.Costs[item][resource]:
                return False
        return True

    # Check if the player can buy a given item, based on the game board state 
    # Different from can_afford, which only checks the player's resources
    def can_buy(self, board, item):
        if item == 'd_card':
            return len(board.d_cards) > 0
        elif item == 'road':
            # TODO: and has a place to put it
            return self.roads_left > 0
        elif item == 'city':
            if self.cities_left > 0:
                for settlement in board.settlements:
                    if settlement.player == self and not settlement.city:
                        return True
            return False
        elif item == 'settlement':
            if self.settlements_left > 0:
                for settlement in consts.SettlementPositions:
                    if self.can_place_settlement(board, settlement, False):
                        return True
            return False

    # Pick and queue a development card 
    def pick_d_card(self, board, player=None):
        player = player if player else self
        card = board.d_cards.pop()
        player.d_card_queue.append(card)
        return card

    # Take resources from the player, based on the item purchased
    def purchase(self, item, board):
        for resource in consts.Costs[item]:
            self.hand[resource] -= consts.Costs[item][resource]

    # UI interaction to place a road on the board 
    def place_road(self, board, settlement=None, position=None):
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                for num,pos in consts.RoadMidpoints.items():
                    dist = math.hypot(pos[0] - event.pos[0], pos[1] - event.pos[1])
                    if dist < 20:
                        roads = [(road.start, road.end) for road in board.roads ]
                        if pos not in roads:
                            road = Road(self, num)
                            if settlement:
                                if road.start == settlement.position or road.end == settlement.position:
                                    board.roads.append(road)
                                    self.roads_left -= 1
                                    if self.roads_left <= 15 - 5:
                                        board.check_longest_road(self)
                                    return
                            else:
                                roads_owned = [r for r in board.roads if r.color == self.color]
                                for test_r in roads_owned:
                                    if road.start == test_r.start or test_r.end == road.end or road.start == test_r.end or road.end == test_r.start:
                                        board.roads.append(road)
                                        self.roads_left -= 1
                                        if self.roads_left <= 15 - 5:
                                            board.check_longest_road(self)
                                        return

    # UI Interaction to place a city on the board
    def place_city(self, board, settlement=None):
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                for settlement in board.settlements:
                    if settlement.player == self:
                        pos = settlement.position
                        dist = math.hypot(pos[0] - event.pos[0], pos[1] - event.pos[1])
                        if dist < 10:
                            settlement.make_city()
                            return

    # Check if a settlement can be placed on the board
    def can_place_settlement(self, board, settlement_number, first):
        settlements = [settlement.number for settlement in board.settlements]
        if settlement_number in settlements:
            return False
        numbers = [settlement.number for settlement in board.settlements ]
        connected_roads = [ road for road in consts.Roads if settlement_number in road ]
        adj = [ road[0] if road[1] == settlement_number else road[1] for road in connected_roads ]
        combined = set(adj).intersection(set(numbers))
        if len(combined) == 0:
            if first:
                return True
            else:
                pos = consts.SettlementPositions[settlement_number]
            roads = [ road for road in board.roads if road.player == self ]
            for road in roads:
                pos = consts.SettlementPositions[settlement_number]
                if pos == road.start or pos == road.end:
                    return True
        return False

    # UI interaction to place a settlement on the board
    def place_settlement(self, board, first, position=None):
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                for num,pos in consts.SettlementPositions.items():
                    dist = math.hypot(pos[0] - event.pos[0], pos[1] - event.pos[1])
                    if dist < 10:
                        if self.can_place_settlement(board, num, first):
                            settlement = Settlement(self, num)
                            board.settlements.append(settlement)
                            self.settlements_left -= 1
                            self.points += 1
                            return settlement

    # UI interaction to select an option (e.g. for trading or actions)
    def pick_option(self, options, board=None, players=None, simulate=False):
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                for option in options:
                    if is_inside(event.pos, option['pos']):
                        return option

    # Select which tyle to block with the robber 
    # Called in game.py 
    def pick_tile_to_block(self, board, tile=None):
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                for num, pos in consts.TilePositions.items():
                    dist = math.hypot(pos[0] - event.pos[0], pos[1] - event.pos[1])
                    if dist < consts.RESOURCE_RADIUS / 2:
                        tile = board.tiles[num]
                        if tile.resource is not None and not tile.blocked:
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

    # Steals a random resource from another player (also a function of the robber)
    def give_random_to(self, player):
        cards = [ resource for resource in self.hand for x in range(self.hand[resource]) ]
        if cards:
            card = random.choice(cards)
            self.hand[card] -= 1
            player.hand[card] += 1

    # UI interaction for deciding to trade resources, this is just the setup for exchanging resources 
    # TODO: Comment out if we decide to remove the trade option  
    def make_exchange(self, screen, board, players, resource, amt, first=True):
        def exchange():
            self.hand[resource] += amt
            if not first:
                return [], None
            buttons = [{'label': consts.ResourceMap[r], 'action':  self.make_exchange(screen, board, players, r, 1, first=False)} for r in self.hand]
            return buttons, 'Trade with: '
        return exchange

    # Check if the player has a port for a given resource
    # TODO: Comment out if we decide to eliminate ports 
    def has_port(self, ports, resource=None):
        # for port in ports:
        #     if (resource and port[0] == resource) or (resource is None and port[0] == 'any'):
        #         return True
        return False

    # UI interaction for trading resources with other players
    # TODO: Comment out if we decide to remove the trade option
    def negotiate_trade(self, screen, board, players):
        offer = {resource: 0 for resource in self.hand}
        asking = {resource: 0 for resource in self.hand}
        def end_turn():
            def make_end():
                return True
            return make_end
        def add_one(side, resource):
            def do_action():
                side[resource] += 1
                return False
            return do_action
        end = False
        while not end:
            buttons = []
            for resource in self.hand:
                if self.hand[resource] > offer[resource]:
                    buttons.append({
                        'label': consts.ResourceMap[resource],
                        'action': add_one(offer, resource)
                    })
            buttons.append({
                'label': 'Make Offer',
                'action': end_turn
            })
            offer_label = [
                    consts.ResourceMap[resource] 
                    + ' ' 
                    + str(offer[resource]) 
                    for resource in offer
            ]
            label = 'Offer: ' + ' '.join(offer_label)
            print_screen(screen, board, label, players, buttons)
            option = self.pick_option(buttons)
            end = option['action']()
        end = False
        while not end:
            buttons = []
            for resource in self.hand:
                    buttons.append({
                        'label': consts.ResourceMap[resource] + ' ' + str(asking[resource]),
                        'action': add_one(asking, resource)
                    })
            buttons.append({
                'label': 'Make Offer',
                'action': end_turn
            })
            label = 'For: '
            print_screen(screen, board, label, players, buttons)
            option = self.pick_option(buttons)
            end = option['action']()

        final_offer = {
                resource: offer[resource] - asking[resource]
                for resource in self.hand
        }
        return final_offer

    # UI interaction to show the player an offer from another player
    # TODO: Comment out if we decide to remove the trade option
    def show_offer(self, offer, screen, board, players, from_player):
        resource_labels = {consts.ResourceMap[resource] +' ' + str(offer[resource]) for resource in offer}

        label = 'Player ' + str(self.number) + ', Offer from Player: ' + str(from_player.number) + ' ' + ' '.join(resource_labels)
        buttons = [
            {
                'label': 'Accept',
                'choice': True,
            },
            {
                'label': 'Reject',
                'choice': False,
            }
        ]
        print_screen(screen, board, label, players, buttons)
        option = self.pick_option(buttons)
        return option['choice']

    # Accept a trade offer, either adding or removing resources from the player's hand
    # TODO: Comment out if we decide to remove the trade option
    def accept(self, offer, yours):
        for resource in offer:
            if yours:
                self.hand[resource] += offer[resource]
            else:
                self.hand[resource] -= offer[resource]

    # Check if the player can afford a trade offer
    # TODO: Comment out if we decide to remove the trade option
    def can_afford_trade(self, offer):
        for resource in offer:
            needed = offer[resource] * -1
            if self.hand[resource] < needed:
                return False
        return True

    # Check if the player has any resources to trade
    # TODO: Comment out if we decide to remove the trade option
    def has_trades(self):
        for resource in self.hand:
            if self.hand[resource] > 0:
                return True
        return False

    # UI interaction to show the player the available exchanges for their resources
    # TODO: Comment out if we decide to remove the trade option
    def get_exchanges(self, screen, board, players):
        exchanges = []
        settlements = [settlement for settlement in board.settlements if settlement.player == self]
        ports = [consts.Ports.get(settlement.number) for settlement in settlements if consts.Ports.get(settlement.number)]
        for resource in self.hand:
            if self.hand[resource] >= 2:
                if self.has_port(ports, resource):
                    exchanges.append({
                        'label': consts.ResourceMap[resource] + ' 2:1',
                        'action': self.make_exchange(screen, board, players, resource, -2)
                    })
                    break
            if self.hand[resource] >= 3:
                if self.has_port(ports):
                    exchanges.append({
                        'label': consts.ResourceMap[resource] + ' 3:1',
                        'action': self.make_exchange(screen, board, players, resource, -3)
                    })
                    break
            if self.hand[resource] >= 4:
                exchanges.append({
                    'label': consts.ResourceMap[resource] + ' 4:1',
                    'action': self.make_exchange(screen, board, players, resource, -4)
                })

        return exchanges

    def __eq__(self, other):
        return self.number == other.number

    def __ne__(self, other):
        return self.number != other.number

    def __hash__(self):
        return hash(self.number)

# Computer player class, inherits from Player
# Makes random decisions for placing settlements, roads, and cities
class ComputerPlayer(Player):
    def place_settlement(self, board, first, position=None):
        choices = [num for num,pos in consts.SettlementPositions.items() if self.can_place_settlement(board, num, first)]
        choice = random.choice(choices)
        settlement = Settlement(self, choice)
        board.settlements.append(settlement)
        self.settlements_left -= 1
        self.points += 1
        return settlement

    # UI interaction to place a road on the board
    def place_road(self, board, settlement=None, position=None):
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
        board.roads.append(road)
        self.roads_left -= 1
        if self.roads_left <= 15 - 5:
            board.check_longest_road(self)

    # Picks a random move to take 
    def pick_option(self, options, board=None, players=None, simulate=False):
        return random.choice(options)

    # Randomly blocks tiles when the robber is rolled 
    def pick_tile_to_block(self, board, tile=None):
        choices = []
        for num, pos in consts.TilePositions.items():
            tile = board.tiles[num]
            if tile.resource is not None and not tile.blocked:
                choices.append(tile)

        tile = random.choice(choices)
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

    # Randomly places cities 
    def place_city(self, board, settlement=None):
        choices = [settlement for settlement in board.settlements if settlement.player == self and settlement.city == False]
        settlement = random.choice(choices)
        settlement.make_city()

def is_inside(pos, box):
    if pos[0] < box[0]:
        return False
    if pos[0] > box[0] + box[2]:
        return False
    if pos[1] < box[1]:
        return False
    if pos[1] > box[1] + box[3]:
        return False
    return True

# Settlement class, represents a settlement on the board
class Settlement(object):
    def __init__(self, player, number):
        self.player = player
        self.color = player.color,
        self.number = number
        self.position = consts.SettlementPositions[number]
        self.city = False

    def make_city(self):
        self.city = True
        self.player.points += 1

# Road class, represents a road on the board
class Road(object):
    def __init__(self, player, num):
        self.number = num
        self.color = player.color
        self.spots = consts.Roads[num]
        self.player = player
        self.start = consts.SettlementPositions[self.spots[0]]
        self.end = consts.SettlementPositions[self.spots[1]]

# From https://github.com/damargulis/catan/
# Any modifications will be noted via comments and commits

import consts
import pygame
import math
from board import Board
from draw import print_screen
from dice import Dice
from player import Player, ComputerPlayer
import sys
import argparse

pygame.init()

size = consts.SCREEN_SIZE
black = consts.BLACK
screen = pygame.display.set_mode(size)

def pick_settlements(players, board):
    def draft_round(players, board, second):
        for i, player in enumerate(players):
            text = 'Player ' + str(player.number) + ': Pick a spot to settle'
            print_screen(screen, board, text, players)
            settlement = player.place_settlement(board, True)
            text = 'Player ' + str(player.number) + ': Place a road'
            print_screen(screen, board, text, players)
            player.place_road(board, settlement)
            if second:
                tiles = board.get_tiles(settlement)
                for tile in tiles:
                    resource = board.tiles[tile].resource
                    if resource is not None:
                        player.take_resource(board.tiles[tile].resource)

    draft_round(players, board, False)
    players.reverse()
    draft_round(players, board, True)
    players.reverse()

def give_resources(board, total):
    for num, tile in enumerate(board.tiles):
        if tile.resource is not None and not tile.blocked and tile.chit == total:
            for settlement_number in consts.TileSettlementMap[num]:
                for settlement in board.settlements:
                    if settlement.number == settlement_number:
                        settlement.player.take_resource(tile.resource)
                        if settlement.city:
                            settlement.player.take_resource(tile.resource)

def end_section():
    return [], None

def get_possible_purchases(player, board, players):
    can_afford = []
    for item in consts.Costs:
        if player.can_afford(item) and player.can_buy(board, item):
            def func_creator(item):
                def make_purchase():
                    player.purchase(item, board)
                    if item == 'road':
                        print_screen(screen, board, 'Place your road', players)
                        player.place_road(board)
                    elif item == 'settlement':
                        print_screen(screen, board, 'Place your settlement', players)
                        player.place_settlement(board, False)
                    elif item == 'city':
                        print_screen(screen, board, 'Pick a settlement to city', players)
                        player.place_city(board)
                    elif item == 'd_card':
                        card = player.pick_d_card(board)
                        buttons = [{'label': 'ok', 'action': end_turn}]
                        print_screen(screen, board, 'You picked a ' + card.label, players, buttons)
                        player.pick_option(buttons)
                    return [], None
                return make_purchase
            can_afford.append({
                'label': item,
                'action': func_creator(item),
            })
    can_afford.append({
        'label': 'cancel',
        'action': end_section,
    })
    return can_afford


def end_turn():
    return [], 'end'

def get_winner(players):
    for player in players:
        if player.points + len([card for card in player.d_cards if card.label == 'Point']) >= 10:
            return player

def main():
    parser = argparse.ArgumentParser(description="Catan Game")
    parser.add_argument('--disable-ports', action='store_true', help="Disable ports in the game")
    args = parser.parse_args()

    ports_enabled = not args.disable_ports

    board = Board(ports_enabled=ports_enabled)  # Pass the flag to the Board class
    dice = Dice()
    players = [ Player(1) ] + [ ComputerPlayer(i) for i in range(2,5) ]
    player_turn = 0
    pick_settlements(players, board)
    first_turn = True
    winner = None
    while winner is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        player = players[player_turn]
        player.start_turn()
        def get_buttons(total = None):
            buttons = [
                    {
                        'label': 'End Turn',
                        'action': end_turn,
                    }
            ]
            possible_purchases = get_possible_purchases(player, board, players)

            def make_purchase():
                return possible_purchases, 'Buy:'

            if len(possible_purchases) > 1:
                buttons.append({
                    'label': 'Make Purchase',
                    'action': make_purchase
                })
            d_cards = [{'label': card.label, 'action': card.make_action(screen, board, players, player)} for card in player.d_cards if card.label != 'Point'] 
            def play_d_card():
                return d_cards + [{'label': 'cancel', 'action': lambda: ([], None)}], 'Which Card: '

            exchanges = player.get_exchanges(screen, board, players)
            def exchange():
                return exchanges + [{'label': 'cancel', 'action': lambda: ([], None)}], 'Exhange: '

            if exchanges:
                buttons.append({
                    'label': 'Exchange',
                    'action': exchange,
                })

            if d_cards and not player.played_d_card:
                buttons.append({
                    'label': 'Play D Card',
                    'action': play_d_card
                })
            if total:
                return buttons, 'Player ' + str(player.number) + ', You Rolled: ' + str(total)
            else:
                return buttons, 'Player ' + str(player.number) + ': '

        def roll_dice():
            total = sum(dice.roll())
            if total == 7:
                if first_turn:
                    while total == 7:
                        total = sum(dice.roll())
                else:
                    for p in players:
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
                                options = print_screen(screen, board, 'Player ' + str(p.number) + ' Pick a resource to give away', players, buttons)
                                resource_chosen = p.pick_option(buttons)
                                p.hand[resource_chosen['resource']] -= 1

                    print_screen(screen, board, 'Player ' + str(player.number) + ' rolled a 7. Pick a settlement to Block', players)
                    players_blocked = player.pick_tile_to_block(board)
                    buttons = [
                            {
                                'label': 'Player ' + str(player_blocked.number),
                                'player': player_blocked
                            } for player_blocked in players_blocked
                    ]
                    if buttons:
                        print_screen(screen, board, 'Take a resource from:', players, buttons)
                        player_chosen = player.pick_option(buttons)
                        player_chosen['player'].give_random_to(player)

            give_resources(board, total)
            return get_buttons(total)
        buttons = [{
            'label': 'Roll Dice',
            'action': roll_dice
         }]

        label = 'Player %s\'s Turn' % player.number
        while buttons:
            print_screen(screen, board, label, players, buttons)
            option = player.pick_option(buttons)
            buttons, label = option['action']()
            if not buttons and label != 'end':
                buttons, label = get_buttons()
        player.end_turn()
        player_turn = (player_turn + 1) % 4
        if player_turn == 0:
            first_turn = False
        winner = get_winner(players)
    print_screen(screen, board, 'Player ' + str(winner.number) + ' Wins!', players)
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            sys.exit()

if __name__ == '__main__':
    main()

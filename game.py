# From https://github.com/damargulis/catan/
# Any modifications will be noted via comments and commits

from typing import List
from agent import Agent
import consts
import math
from board import Board
from draw import print_screen
from dice import Dice
from player import Player, ComputerPlayer
import sys
import argparse
from utils import give_resources, get_possible_purchases, end_turn, get_winner

# Setup command line arguments
parser = argparse.ArgumentParser(description="Catan Game")
parser.add_argument('--disable-ports', action='store_true', help="Disable ports in the game")
parser.add_argument('-hum', '--num-humans', type=int, default=1, help="Number of human players in the game")
parser.add_argument('-comp', '--num-computers', type=int, default=3, help="Number of computer players in the game")
parser.add_argument('--tui', action='store_true', help="Use TUI instead of GUI with AI agents instead of human players")
args = parser.parse_args()

use_tui = args.tui
ports_enabled = not args.disable_ports

if not use_tui:
    import pygame
    pygame.init()

    size = consts.SCREEN_SIZE
    black = consts.BLACK
    screen = pygame.display.set_mode(size)
else:
    screen = None

def pick_settlements(players: List[Player], board: Board):
    def draft_round(players: List[Player], board: Board, second: bool):
        for i, player in enumerate(players):
            # Pick settlement spot
            text = 'Player ' + str(player.number) + ': Pick a spot to settle'
            if not use_tui:
                print_screen(screen, board, text, players)
            if type(player) is not Agent:
                settlement = player.place_settlement(board, True)
                print(settlement)
            else:
                # Agent with TUI
                print(text)
                # TODO: need to figure out a better way for AI agents to pick the position (i.e. not through input)
                position = (int(input("Enter position 1: ").strip()), int(input("Enter position 2: ").strip()))
                settlement = player.place_settlement(board, True, position)
                while settlement is False:
                    print("Invalid position, try again")
                    position = (int(input("Enter position 1: ").strip()), int(input("Enter position 2: ").strip()))
                    settlement = player.place_settlement(board, True, position)

            # Pick road spot
            text = 'Player ' + str(player.number) + ': Place a road'
            if not use_tui:
                print_screen(screen, board, text, players)
            if type(player) is not Agent:
                player.place_road(board, settlement)
            else:
                print(text)
                position = int(input("Enter road number: ").strip())
                player.place_road(board, settlement, position)
            
            # Get resources
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

def main():
    board = Board(ports_enabled=ports_enabled)  # Pass the flag to the Board class
    dice = Dice()
    players = []
    num_humans = args.num_humans
    num_computers = args.num_computers
    for i in range(num_humans):
        players.append(Player(i + 1) if not use_tui else Agent(i + 1))
    for i in range(num_humans, num_humans + num_computers):
        players.append(ComputerPlayer(i + 1))
    player_turn = 0
    pick_settlements(players, board)
    first_turn = True
    winner = None
    while winner is None:
        if not use_tui:
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
            possible_purchases = get_possible_purchases(player, board, players, screen)

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
            # if total == 7:
            #     if first_turn:
            #         while total == 7:
            #             total = sum(dice.roll())
            #     else:
            #         for p in players:
            #             if sum([p.hand[resource] for resource in p.hand]) > 7:
            #                 original = sum([p.hand[resource] for resource in p.hand])
            #                 needed_left = math.ceil(original / 2)
            #                 while sum([p.hand[resource] for resource in p.hand]) > needed_left:
            #                     resources = [resource for resource in p.hand if p.hand[resource]]
            #                     resources = list(set(resources))
            #                     if not use_tui:
            #                         buttons = [{
            #                                 'resource': resource,
            #                                 'label': consts.ResourceMap[resource],
            #                         } for resource in resources]
            #                         options = print_screen(screen, board, 'Player ' + str(p.number) + ' Pick a resource to give away', players, buttons)
            #                         resource_chosen = p.pick_option(buttons)
            #                     else:
            #                         print(f"Player {p.number}, pick a resource to give away: {resources}")
            #                         resource_chosen = input("Enter resource: ").strip()
            #                     p.hand[resource_chosen['resource']] -= 1

            #         if not use_tui:
            #             print_screen(screen, board, 'Player ' + str(player.number) + ' rolled a 7. Pick a settlement to Block', players)
            #             players_blocked = player.pick_tile_to_block(board)
            #             buttons = [
            #                     {
            #                         'label': 'Player ' + str(player_blocked.number),
            #                         'player': player_blocked
            #                     } for player_blocked in players_blocked
            #             ]
            #             if buttons:
            #                 print_screen(screen, board, 'Take a resource from:', players, buttons)
            #                 player_chosen = player.pick_option(buttons)
            #                 player_chosen['player'].give_random_to(player)

            give_resources(board, total)
            return get_buttons(total)
        buttons = [{
            'label': 'Roll Dice',
            'action': roll_dice
         }]

        label = 'Player %s\'s Turn' % player.number
        while buttons:
            if not use_tui:
                print_screen(screen, board, label, players, buttons)
            else:
                print(label, buttons)
            option = player.pick_option(buttons)
            buttons, label = option['action']()
            if not buttons and label != 'end':
                buttons, label = get_buttons()
        player.end_turn()
        player_turn = (player_turn + 1) % 4
        if player_turn == 0:
            first_turn = False
        winner = get_winner(players)
    if not use_tui:
        print_screen(screen, board, 'Player ' + str(winner.number) + ' Wins!', players)
    else:
        print(f"Player {winner.number} Wins!")
    while not use_tui:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            sys.exit()

if __name__ == '__main__':
    main()

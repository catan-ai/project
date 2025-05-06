# From https://github.com/damargulis/catan/
# Any modifications will be noted via comments and commits

import consts
import pygame
import math
from board import Board
from draw import print_screen
from dice import Dice
from player import Player, ComputerPlayer
from agent import Agent
import sys
import argparse
from typing import List
from utils import get_possible_purchases, end_turn, give_resources, get_winner

from copy import deepcopy


pygame.init()

size = consts.SCREEN_SIZE
black = consts.BLACK
screen = pygame.display.set_mode(size)

def pick_settlements(players: List[Player], board: Board):
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

def main():
    parser = argparse.ArgumentParser(description="Catan Game")
    parser.add_argument('--disable-ports', action='store_true', help="Disable ports in the game")
    args = parser.parse_args()

    ports_enabled = not args.disable_ports

    board = Board(ports_enabled=ports_enabled)  # Pass the flag to the Board class
    dice = Dice()
    players = [ Agent(1) ] + [ ComputerPlayer(i) for i in range(2,5) ]
    player_turn = 0
    pick_settlements(players, board)
    first_turn = True
    winner = None
    i = 0
    while winner is None:
        print(f"turn {i}")
        i += 1
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
            possible_purchases = get_possible_purchases(player, board, deepcopy(players), screen)

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

            # if exchanges:
            #     buttons.append({
            #         'label': 'Exchange',
            #         'action': exchange,
            #     })

            if d_cards and not player.played_d_card:
                buttons.append({
                    'label': 'Play D Card',
                    'action': play_d_card
                })
            if total:
                return buttons, 'Player ' + str(player.number) + ', You Rolled: ' + str(total)
            else:
                return buttons, 'Player ' + str(player.number) + ': '

        # If agent, use the MCTS agent to pick the best action
        if player_turn == 0:
            # Roll the dice to get the resources and start the turn
            total = sum(dice.roll())
            give_resources(board, total)

            # Now, actually use the MCTS agent to play their turn
            board, players = player.play_turn(board, players, False)
            player = players[player_turn]
            label = 'Player %s\'s Turn' % player.number + ', You Rolled: ' + str(total)
            print_screen(screen, board, label, players)
        # If other type of player, do regular turn
        else:

            def roll_dice():
                total = sum(dice.roll())

                give_resources(board, total)
                return get_buttons(total)
            buttons = [{
                'label': 'Roll Dice',
                'action': roll_dice
            }]

            label = 'Player %s\'s Turn' % player.number
            while buttons:
                print_screen(screen, board, label, players, buttons)
                option = player.pick_option(buttons, board, players)
                buttons, label = option['action']()
                if not buttons and label != 'end':
                    buttons, label = get_buttons()
            player.end_turn()
        player_turn = (player_turn + 1) % 4
        if player_turn == 0:
            first_turn = False
        winner = get_winner(players)
    print_screen(screen, board, 'Player ' + str(winner.number) + ' Wins!', players)
    print('Player ' + str(winner.number) + ' Wins!')
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            sys.exit()

if __name__ == '__main__':
    main()


# From https://github.com/damargulis/catan/
# Any modifications will be noted via comments and commits

import consts
import sys
import pygame
from math import sin, cos

RESOURCE_RADUIS = consts.RESOURCE_RADIUS
PLAYER_POSITIONS = consts.PLAYER_POSITIONS

black = consts.BLACK
white = consts.WHITE

def draw_resource_tile(surface, tile):
    pi = 3.14
    n = 6
    position = tile.location
    pygame.draw.polygon(
        surface, 
        tile.color,
        [
            (
                cos(i / n * 2 * pi + pi / 2) * RESOURCE_RADUIS + position[0],
                sin(i / n * 2 * pi + pi / 2) * RESOURCE_RADUIS + position[1]
            )
            for i in range(0,n)
        ]
    )
    if tile.chit:
        print_text(surface, str(tile.chit), tile.location, black)
    if tile.blocked:
        pygame.draw.circle(
                surface,
                consts.ROBBER_COLOR,
                tile.location,
                consts.ROBBER_SIZE,
        )

def draw_settlement(surface, settlement):
    pygame.draw.circle(
            surface,
            settlement.color,
            settlement.position,
            consts.CITY_SIZE if settlement.city else consts.SETTLEMENT_SIZE
    )

def draw_road(surface, road):
    pygame.draw.line(
            surface,
            road.color,
            road.start,
            road.end,
            consts.ROAD_WIDTH
    )

def draw_port(screen, port):
    location = consts.SettlementPositions[port]
    pygame.draw.rect(
            screen,
            consts.WHITE if consts.Ports[port][0] == 'any' else consts.ResourceColors[consts.Ports[port][0]],
            (
                location[0] - consts.PORT_RADIUS,
                location[1] - consts.PORT_RADIUS,
                consts.PORT_RADIUS * 2,
                consts.PORT_RADIUS * 2,
            )
    )

def print_board(screen, board):
    for tile in board.tiles:
        draw_resource_tile(screen, tile)
    for port in consts.Ports:
        draw_port(screen, port)
    for settlement in board.settlements:
        draw_settlement(screen, settlement)
    for road in board.roads:
        draw_road(screen, road)

def print_text(screen, text, position, color=white):
    myfont = pygame.font.SysFont("monospace", consts.TEXT_SIZE)
    label = myfont.render(text, 1, color)
    screen.blit(label, position)
    return myfont.size(text)

def print_player(screen, player):
    position = PLAYER_POSITIONS[player.number - 1]
    pygame.draw.rect(screen, white, position, consts.LINE_WIDTH)
    print_text(
            screen, 
            'Player ' + str(player.number), 
            (
                position[0] + consts.LINE_WIDTH* 6, 
                position[1] + consts.LINE_WIDTH
            ),
            player.color, 
    )
    labels = [
            'Points: ' + str(player.points),
            'Brick: ' + str(player.hand[consts.Resource.BRICK]),
            'Grain: ' + str(player.hand[consts.Resource.GRAIN]),
            'Lumber: ' + str(player.hand[consts.Resource.LUMBER]),
            'Ore: ' + str(player.hand[consts.Resource.ORE]),
            'Wool: ' + str(player.hand[consts.Resource.WOOL]),
            'Dev Cards: ' + str(len(player.d_cards) + len(player.d_card_queue)),
            'Knights: ' + str(player.knights),
    ]
    def print_player_stats(screen, label, position):
        print_text(screen, label, (position[0], position[1]))
        return (position[0], position[1] + consts.TEXT_SIZE)
    position = (
            position[0] + consts.LINE_WIDTH* 2, 
            position[1] + consts.LINE_WIDTH + consts.TEXT_SIZE
    )
    for label in labels:
        position = print_player_stats(screen, label, position)

def print_screen(screen, board, text, players, buttons=[]):
    screen.fill(black)
    print_board(screen, board)
    for player in players:
        print_player(screen, player)
    print_dialog(screen, text, buttons)

def print_dialog(screen, text, buttons):
    pygame.draw.rect(
            screen, 
            white, 
            (
                0,
                consts.HEIGHT - consts.DIALOG_HEIGHT,
                consts.WIDTH,
                consts.DIALOG_HEIGHT,
            ), 
            consts.LINE_WIDTH
    )
    size = print_text(
            screen, 
            text, 
            (
                consts.LINE_WIDTH * 2,
                consts.HEIGHT - consts.DIALOG_HEIGHT + consts.LINE_WIDTH
            )
    )
    far_x = size[0] + consts.LINE_WIDTH * 2
    print_buttons(screen, buttons, far_x)
    pygame.display.flip()

def print_buttons(screen, buttons, start):
    top = consts.HEIGHT - consts.DIALOG_HEIGHT + consts.LINE_WIDTH
    for button in buttons:
        size = print_text(
                screen, 
                button['label'], 
                (start + consts.LINE_WIDTH * 4, top)
        )
        left = start + consts.LINE_WIDTH * 2
        width = size[0] + consts.LINE_WIDTH * 3
        pygame.draw.rect(
                screen, 
                white, 
                (left, top, width, consts.DIALOG_HEIGHT / 2),
                2
        )
        button['pos'] = (left, top, width, consts.TEXT_SIZE * 2)
        start += size[0] + consts.LINE_WIDTH * 5


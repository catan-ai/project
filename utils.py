import consts
from draw import print_screen

def give_resources(board, total):
    for num, tile in enumerate(board.tiles):
        if tile.resource is not None and not tile.blocked and tile.chit == total:
            for settlement_number in consts.TileSettlementMap[num]:
                for settlement in board.settlements:
                    if settlement.number == settlement_number:
                        settlement.player.take_resource(tile.resource)
                        if settlement.city:
                            settlement.player.take_resource(tile.resource)


def get_possible_purchases(player, board, players, screen):
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

def end_section():
    return [], None

def end_turn():
    return [], 'end'

def get_winner(players):
    for player in players:
        if player.points + len([card for card in player.d_cards if card.label == 'Point']) >= 10:
            return player
    
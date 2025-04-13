# From https://github.com/damargulis/catan/
# Any modifications will be noted via comments and commits

import consts
from random import shuffle
from draw import print_screen

class ResourceTile(object):
    def __init__(self, resource):
        self.resource = resource
        self.color = consts.ResourceColors[resource]
        self.blocked = False

    def set_chit(self, chit):
        self.chit = chit

    def set_location(self, location):
        self.location = consts.TilePositions[location]

class DesertTile(ResourceTile):
    def __init__(self):
        self.resource = None
        self.chit = None
        self.color = consts.ResourceColors['desert']
        self.blocked = True

    def set_chit(self, chit):
        raise NotImplementedError

class Board(object):
    def __init__(self):
        self.ports = self._get_ports()
        self.tiles = self._get_tiles()
        shuffle(self.tiles)
        for i, tile in enumerate(self.tiles):
            tile.set_location(i)
        chits = self._get_chits()
        i = 0
        for tile in self.tiles:
            try:
                tile.set_chit(chits[i])
                i += 1
            except:
                continue
        self.settlements = []
        self.roads = []
        self.d_cards = self._get_d_cards()
        shuffle(self.d_cards)

    def _get_ports(self):
        return consts.Ports

    def _get_tiles(self):
        tiles = []
        for i in range(3):
            tiles.append(ResourceTile(consts.Resource.BRICK))
        for i in range(4):
            tiles.append(ResourceTile(consts.Resource.LUMBER))
        for i in range(4):
            tiles.append(ResourceTile(consts.Resource.WOOL))
        for i in range(4):
            tiles.append(ResourceTile(consts.Resource.GRAIN))
        for i in range(3):
            tiles.append(ResourceTile(consts.Resource.ORE))
        tiles.append(DesertTile())
        return tiles

    def _get_chits(self):
        return [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]

    def _get_d_cards(self):
        return (
                [ Knight() ] * 14
                + [ Point() ] * 5
                + [ Monopoly() ] * 2
                + [ RoadBuilder() ] * 2
                + [YearOfPlenty() ] * 2
        )

    def get_tiles(self, settlement):
        return [
                tile for tile in consts.TileSettlementMap
                if settlement.number in consts.TileSettlementMap[tile]
        ]

    def make_road_sets(self, player, owned_roads):
        roads_left = [road for road in owned_roads]
        sets = []
        while len(roads_left):
            seen = set()
            road = roads_left.pop()
            seen.add(road.number)
            stack = [road.spots[0],road.spots[1]]
            while len(stack) > 0:
                settlement_num = stack.pop()
                for r in owned_roads:
                    if r in roads_left and r.number not in seen and settlement_num in r.spots:
                        seen.add(r.number)
                        roads_left.remove(r)
                        seen.add(r.number)
                        settlement_one = r.spots[0]
                        settlement_two  = r.spots[1]
                        stack += [settlement_one]
                        stack += [settlement_two]
            sets.append(seen)
        return sets

    def dfs(self, road, s, discovered, next_settlement, length, maximum):
        discovered.add(road)
        connected = [
                r for r in s
                if consts.Roads[r][0] == next_settlement
                or consts.Roads[r][1] == next_settlement
        ]
        for r in connected:
            if r not in discovered:
                discovered.add(r)
                if consts.Roads[r][0] == next_settlement:
                    n_settle = consts.Roads[r][1]
                else:
                    n_settle = consts.Roads[r][0]
                l = self.dfs(r, s, discovered, n_settle, length + 1, maximum)
                print('l:', l)
                if l > maximum:
                    maximum = l
        return max(length, maximum)
        

    def check(self, s):
        edges = []
        for road in s:
            corners = [item for r in s if r != road for item in consts.Roads[r]]
            if corners.count(consts.Roads[road][0]) > 0 and corners.count(consts.Roads[road][1]) > 0:
                continue
            else:
                edges.append(road)
        if not edges:
            edges = [road]
        scores = []
        for e in edges:
            corners = [item for r in s if r != e for item in consts.Roads[r]]
            if corners.count(consts.Roads[road][0]) > 1:
                next_settlement = consts.Roads[road][0]
            else:
                next_settlement = consts.Roads[road][1]
            score = self.dfs(e, s, set(), next_settlement, 1, 0)
            scores.append(score)
        return max(scores)

    def check_road_length(self, player):
        owned_roads = [road for road in self.roads if road.player == player]
        if len(owned_roads) < 5:
            return 0
        else:
            sets = self.make_road_sets(player, owned_roads)
            to_check = [s for s in sets if len(s) >= 5]
            if len(to_check):
                to_return = max([self.check(s) for s in to_check])
                return to_return
            else:
                return 0

    def check_longest_road(self, placing_player):
        print('checking')
        players = set([road.player for road in self.roads])
        player_scores = [self.check_road_length(player) for player in players]
        best = max(player_scores)
        if best < 5:
            return
        best_players = [player for i,player in enumerate(players) if player_scores[i] == best]
        if len(best_players) > 1:
            return
        print('best:')
        best_player = best_players[0]
        print(best_player.number)
        if best_player.longest_road:
            print('already_has')
            return
        else:
            print('switching')
            for player in players:
                if player.longest_road:
                    print('switched')
                    player.longest_road = False
                    player.points -= 2
            print('giving')
            best_player.longest_road = True
            best_player.points += 2

class Knight(object):
    label = 'Knight'

    def make_action(self, screen, board, players, player):
        def action():
            player.play_d_card(self)
            print_screen(screen, board, 'Player ' + str(player.number) + ': Pick a settlement to Block', players)
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
            player.knights += 1
            if player.knights >= 3 and not  player.largest_army:
                max_other = max([p.knights for p in players if p != player])
                if player.knights > max_other:
                    for p in players:
                        if p.largest_army:
                            p.largest_army = False
                            p.points -= 2
                    player.largest_army = True
                    player.points += 2
            return [], None
        return action

class Point(object):
    label = 'Point'

    def make_action(self, screen, board, players, player):
        raise NotImplementedError

class Monopoly(object):
    label = 'Monopoly'

    def make_action(self, screen, board, players, player):
        def action():
            player.play_d_card(self)
            buttons = [
                    {
                        'label': consts.ResourceMap[i],
                        'resource': i,
                    } for i in range(5)
            ]
            print_screen(screen, board, 'Take all of:', players, buttons)
            resource = player.pick_option(buttons)['resource']
            for p in players:
                if p != player:
                    player.hand[resource] += p.hand[resource]
                    p.hand[resource] = 0
            return [], None
        return action

class RoadBuilder(object):
    label = 'Road Builder'

    def make_action(self, screen, board, players, player):
        def action():
            player.play_d_card(self)
            for i in range(2):
                print_screen(screen, board, 'Player ' + str(player.number) + ': Place a road', players)
                player.place_road(board)
            return [], None
        return action

class YearOfPlenty(object):
    label = 'Year Of Plenty'

    def make_action(self, screen, board, players, player):
        def action():
            player.play_d_card(self)
            for i in range(2):
                buttons = [
                        {
                            'label': consts.ResourceMap[i],
                            'resource': i,
                        } for i in range(5)
                ]
                print_screen(screen, board, 'Player ' + str(player.number) + ': Pick a Resource', players, buttons)
                resource = player.pick_option(buttons)['resource']
                player.hand[resource] += 1
            return [], None
        return action

# From https://github.com/damargulis/catan/
# Any modifications will be noted via comments and commits

import consts
from random import shuffle
from draw import print_screen
import agent

# Represents a resource tile (brick, wool, etc.)
class ResourceTile(object):
    # Initialize a resource tile with resource type, color, and un-blocked flag
    def __init__(self, resource):
        self.resource = resource
        self.color = consts.ResourceColors[resource]
        self.blocked = False

    # Assign a number token to the tile
    def set_chit(self, chit):
        self.chit = chit

    # Set tile's board position from predefined constants
    def set_location(self, location):
        self.location = consts.TilePositions[location]

# Represents the special desert resource tile
class DesertTile(ResourceTile):
    # Initialize the desert tile with no resource type, no chit, color, and blocked flag
    def __init__(self):
        self.resource = None
        self.chit = None
        self.color = consts.ResourceColors['desert']
        self.blocked = True

    # Not implemented
    def set_chit(self, chit):
        raise NotImplementedError

# Main board logic
class Board(object):
    # Initialize the board
    def __init__(self, ports_enabled=True):
        # Get the ports and resource tiles
        self.ports = self._get_ports() if ports_enabled else []
        self.ports_enabled = ports_enabled
        self.tiles = self._get_tiles()

        # Set the location of each resource tile
        shuffle(self.tiles)
        for i, tile in enumerate(self.tiles):
            tile.set_location(i)

        # Set the chits of each resource tile 
        chits = self._get_chits()
        i = 0
        for tile in self.tiles:
            try:
                tile.set_chit(chits[i])
                i += 1
            except:
                continue

        # Initialize lists for settlements, roads, and development cards (shuffled)
        self.settlements = []
        self.roads = []
        self.d_cards = self._get_d_cards()
        shuffle(self.d_cards)

    # Return the static list of ports 
    def _get_ports(self):
        return consts.Ports

    # Return a list of the 19 tiles (18 resource, 1 desert)
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

    # Return a list of the 18 possible chits 
    def _get_chits(self):
        return [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]

    # Return the deck of development cards
    def _get_d_cards(self):
        return (
                [ Knight() ] * 0 # Remove knights
                + [ Point() ] * 5
                + [ Monopoly() ] * 2
                + [ RoadBuilder() ] * 2
                + [YearOfPlenty() ] * 2
        )

    # Return a of tile IDs adjacent to a given settlement
    def get_tiles(self, settlement):
        return [
                tile for tile in consts.TileSettlementMap
                if settlement.number in consts.TileSettlementMap[tile]
        ]

    # Partition player's roads into sets of connected segments
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

    # Depth-first search to find the longest contiguous road path
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
        
    # Check road set for longest path length
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

    # Return the length of the player's longest road, if they own more than 5 roads
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

    # Determine if a player qualifies for the longest road VP
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

# --- Development Card Classes ---
# Playing Knight: Moves the robber, blocking a new tile to steal from an opponent, and determines who gets VPs for Largest Army
class Knight(object):
    label = 'Knight'

    def make_action(self, screen, board, players, player):
        def action():
            # Skip if agent
            if type(player) is agent.Agent:
                return [], None
            
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
    
# Playing Point: Gives you an additional VP (never actually "played")
class Point(object):
    label = 'Point'

    def make_action(self, screen, board, players, player):
        raise NotImplementedError

# Playing Monopoly: Takes all of one resource from all other players
class Monopoly(object):
    label = 'Monopoly'

    def make_action(self, screen, board, players, player):
        def action():
            # Skip if agent
            if type(player) is agent.Agent:
                return [], None

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

# Playing RoadBuilder: Allows you to place two free roads
class RoadBuilder(object):
    label = 'Road Builder'

    def make_action(self, screen, board, players, player):
        def action():
            # Skip if agent
            if type(player) is agent.Agent:
                return [], None
            
            player.play_d_card(self)
            for i in range(2):
                print_screen(screen, board, 'Player ' + str(player.number) + ': Place a road', players)
                player.place_road(board)
            return [], None
        return action

# Playing YearOfPlenty: Allows you to draw two resource cards of your choosing from the bank
class YearOfPlenty(object):
    label = 'Year Of Plenty'

    def make_action(self, screen, board, players, player):
        def action():
            # Skip if agent
            if type(player) is agent.Agent:
                return [], None

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

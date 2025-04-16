

# PseudoCode

Based on this code, the State(object) object will need to contain the following existing classes, or they will need to be passed in as additional parameters to the getPossibleActions function:
- board
- player/ai_player (for this one it can probably be assumed that this would be self assuming we have an AIPlayer class that would contain this function)
- players (this one might be unnecessary, as the get_possible_purchases function only uses this for gui stuff i think)

V2
```
# returns a list of all possible Actions based on current state
List(Actions) getPossibleActions(State):

    # empty list to collect all possible actions
    list_of_actions = []

    # Use get_possible_purchases to get an idea of what purchases are available (road, city, settlement, dcard)
    possible_purchases = get_possible_purchases(player, board, players)

    for purchase in possible_purchases:
        if purchase['label'] == 'city':
            for boardSettlement in board.settlements:
                if boardSettlement.player == ai_player and not boardSettlement.city:
                    list_of_actions.append(action: upgrade the settlement boardSettlement to a city)
        if purchase['label'] == 'settlement':
            for settlementPos in consts.SettlementPositions:
                if ai_player.can_place_settlement(board, settlementPos, False):
                    list_of_actions.append(action: place a settlement at settlementPos)
        if purchase['label'] == 'road':

            TODO: need to figure out how to establish whether there is a spot to put a road. the get_possible_purchases call above already accounts for whether the player has the resources to build a road, but it does not account for whether there is a spot to put the road (Note: this is probably a very very rare condition where you get "boxed in" by other players roads)

            roads = [(road.start, road.end) for road in board.roads ]
            for num,pos in consts.RoadMidpoints.items():
                if pos not in roads:
                    road = Road(aiPlayer, num)
                    roads_owned = [r for r in board.roads if r.color == aiPlayer.color]
                    for test_r in roads_owned:
                        if road.start == test_r.start or test_r.end == road.end or road.start == test_r.end or road.end == test_r.start:
                            list_of_actions.append(action: place a road Road(aiPlayer, num) )
        if purchase['label'] == 'd_card' and len(board.d_cards) > 0:
            list_of_actions.append(action: buy a development card )

        list_of_actions.append(action: buy a development card )

    return list_of_actions

State getSuccessors(State, Action):


    
    return State


    
```

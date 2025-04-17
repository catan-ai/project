

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

    # Get possible development cards the player has in their hand to play
    # Note: cards in player.d_cards are valid cards to play (i.e. they were not bought on the current turn)
    # cards in player.d_cards_queue are cards that were bought this turn so they cannot be played until next turn
    # point cards cannot be played
    card_actions = [ (action: play card) for card in player.d_cards if card.label != 'Point'] 
    
    # if there are cards to play and the agent has not already played a card this round, add all possible card actions
    if len(card_actions) > 0 and not aiplayer.played_d_card:
        list_of_actions.extend(card_actions)

    # Last possible action of every "turn" is to end the turn
    list_of_actions.append(action: end turn )

    return list_of_actions


State stateActionTransition(State, Action):
    # If the Action is deterministic (building anything)
    if (Action is build road, build city, build settlement):
        # Assuming that State is a combination of player (including recources and d_cards) and board objects,
        # buildSuccessorState will take the action and update these two objects and return the resulting objects
        successor = buildSuccessorState(State, Action)
    if (Action is draw d_card)
    return State





State getSuccessors(State):
    # empty list to collect state action pair
    state_action = []

    # call get actions to get all possible actions from current state


    # get all actions 
    actions = getPossibleActions(State)

    # Loop through all actions
    for action in actions:
        successorState = stateActionTransition(State, action)
        state_action.append( (successorState, action) )

    return state_action


    
```

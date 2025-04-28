# PseudoCode

Based on this code, the State(object) object will need to contain the following existing classes, or they will need to be passed in as additional parameters to the getPossibleActions function:
- board
- player/ai_player (for this one it can probably be assumed that this would be self assuming we have an AIPlayer class that would contain this function)
- players (this one might be unnecessary, as the get_possible_purchases function only uses this for gui stuff i think)

V2
```python
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
    unique_player_dcards = set()
    for card in player.d_cards:
        if card.label != 'Point' and card not in unique_player_dcards:
            unique_player_dcards.add(card)
    
    for card in unique_player_dcards:
        if card.label = "Knight"
            for num, pos in consts.TilePositions.items():
                tile = board.tiles[num]
                if tile.resource is not None and not tile.blocked:
                    players = []
                    for settlement in board.settlements:
                        if settlement.number in settlements_blocking and not settlement.player == self:
                            players.append(settlement.player)
                    players = list(set(players))
                    players_list = sorted(players, key=lambda player: player.number)
                    for curplayer in players_list:
                        list_of_actions.append(action: block `tile` and take a resource from `curplayer`)
        # Monopoly cards let you take all resources of a certain kind from all players
        if card.label = "Monopoly"
            # possible Monopoly actions are to select one of the four resource types to take
            for resource in consts.ResourceMap
                card_actions.append(action: Monopoly card for `resource`)

        if card.label = "Road Builder"
            TODO: Possibly make this more efficient. I was lazy and did it naively
            # temporary board and aiPlayer to simulate different first road placements
            temp_board = deepcopy(board)
            temp_player = deepcopy(aiPlayer)
            # simulate placing first of two roads
            roads1 = [(road.start, road.end) for road in board.roads ]
            for num,pos in consts.RoadMidpoints.items():
                if pos not in roads1:
                    road1 = Road(aiPlayer, num)
                    roads_owned1 = [r for r in board.roads if r.color == aiPlayer.color]
                    for test_r1 in roads_owned1:
                        if road.start == test_r1.start or test_r1.end == road.end or road.start == test_r1.end or road.end == test_r1.start:
                            temp_player.place_road(temp_board)
                            
                            
                            # Now from this point simulate placing a second road
                            roads2 = [(road.start, road.end) for road in temp_board.roads ]
                            for num,pos in consts.RoadMidpoints.items():
                                if pos not in roads2:
                                    road2 = Road(temp_player, num)
                                    roads_owned2 = [r for r in board.roads if r.color == temp_player.color]
                                    for test_r2 in roads_owned2:
                                        if road.start == test_r2.start or test_r2.end == road.end or road.start == test_r2.end or road.end == test_r2.start:    
                                            list_of_actions.append(action: place road1 and then road2 )


        # Year Of Plenty card lets you get any 2 resources for free
        if card.label = "Year Of Plenty"
            # get all possible unique combos of 2 resources
            resource_combos = list(itertools.combinations_with_replacement(consts.ResourceMap, 2))
            for combo in resource_combos:
                card_actions.append(action: Year Of Plenty card to get 2 resources `combo`)




    card_actions = [ (action: play card) for card in player.d_cards if card.label != 'Point'] 
    
    # if there are cards to play and the agent has not already played a card this round, add all possible card actions
    if len(card_actions) > 0 and not aiplayer.played_d_card:
        list_of_actions.extend(card_actions)

    # Last possible action of every "turn" is to end the turn
    list_of_actions.append(action: end turn )

    return list_of_actions


State stateActionTransition(State, Action):
    # If the Action is deterministic (building anything or playing a monopoly, year of plenty, or road builder dcard)
    if (Action is build road, build city, build settlement, play monopoly, year of plenty, or road builder dcard):
        # Assuming that State is a combination of player (including recources and d_cards) and board objects,
        # buildSuccessorState will take the action and update these two objects and return the resulting objects
        successor = buildSuccessorState(State, Action)
        return successor

    if (Action is draw d_card)
        # get all cards in the dcard list for the board
        available_dcards = board.dcards
        total_dcards = len(available_dcards)

        num_cards = {
            "Knight": 0,
            "Point": 0,
            "Monopoly": 0,
            "Road Builder": 0,
            "Year Of Plenty": 0
        }

        for card in available_dcards:
            num_cards[card.label] += 1
        
        card_labels = list(num_cards.keys())
        weights = list(num_cards.values())

        sampled_card = random.choices(card_labels, weights=weights, k=1)[0]

        successor = new state from adding the sampled card to the player's hand
        return successor


    if (Action is play a knight card or place the robber)
        TODO: IMPLEMENT ROBBER STATE ACTION TRANSITION
        return successor

    if action is end turn:
        # For end turn, we have to consider the next state stochastically because of the options of other players.
        # We will handle next state by doing a "black box" sample from the environment's state transition function.
        # This means we will have a function that will take in current state, and generate a possible the next state
        # by simulating all the computer players action and stopping before our next dice roll

        # empty list that will be populated with board states to sample from 
        sample_space = []
        for i in range(1000):
            sample_space.append(stateTransition_simulation(board, player))

        # random number for sample
        random_number = random.randint(1000)

        # Return the sample
        return sample_space[random_number]


        

Note State buildSuccessorState(State, Action) will simply be a method that will update the board and all players hands based on an action taken. I am not going to write pseudocode for it, but all the functionality should already exist in the code, we just need to leverage the right functions and variables.



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

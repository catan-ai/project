## 1 State Space
- **State:**
    - **Player:**
        - Hand: Dictionary containing each card type (keys) and the associated counts (values)
    - **Board:**
        - Tiles: something about location of each tile, resource and number associated
        - Roads: location of each road


        - Robber: Location (tile) of the robber
        - VP: List of how many victory points each player has

- **Actions:**
    - Roll the dice, determining what resource cards you get
    - Optionally: 
        - Build a road 
        - Build a settlement
        - Build a city 
        - Purchase development card 

- **Transitions:**
    - Upon dice roll, update hand(s)
    - Upon updating hand(s), update possible action list  
    - Upon building, update possible locations for future development, update hand(s)
    - Upon end of turn, evaluate win/lose based on victory points

- **Observations:**
    - Board and Player states

## 2 Game Modifications & Assumptions
- **Assumptions:**
    - AI agent will be playing against 3 other players
- **Simplifications**
    - Removed trading
    - Removed ports
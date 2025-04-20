## 1 State Space
- **State:**
    - **Player:**
        - **Hand**: Dictionary containing each card type (keys) and the associated counts (values)
        - **ID and Color**: Number identifying player and RGB value 
        - **Development Cards**: Queue of *development cards* held by the player, drawn from the board's development card queue 
        - **Points**: Number of points a player has 
        - **Settlements Left, Roads Left, Cities Left**: Number of each structure that a player may still build, initialized to `5`, `15`, and `4` 
        - **Longest Road and Largest Army**: Flags set to `True` if player holds either, otherwise `False` 
        - **Knights**: How many *knight cards* (a type of development card) the player has drawn 
)
    - **Board:**
        - **Resource Tiles**: A `Tile` (class) that has a resource, and a flag for whether it is blocked by a knight (`True`/`False`)
        - **Desert Tile**: The desert `Tile` where the knight originates, has no resource 
        - **
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
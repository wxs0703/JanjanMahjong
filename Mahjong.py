import numpy as np

from Tile import Tile, TileIndex
from Game import Game, Round
from Action import DiscardAction

def main():

    # Define game type
    mode = int(input('Enter number of players: '))
    game = Game(mode=mode, doLogging=True)

    # Load players

    # Shuffle it up
    hands, hands_index, wall, wall_index, dora_indicators, doras_index, deck = shuffle(mode)
    round = Round(mode=mode, hands=hands_index, wall=wall_index, doras=doras_index, deck=deck)

def shuffle(mode):
    '''
    Shuffles tiles. 
    mode: int; 3 or 4 players
    Returns:
    hands: mode x 14 array of Tile objects with each player's hand
    hands_index: list of TileIndex objects for each player's hand
    wall: list of Tile objects that are in the wall
    wall_index: TileIndex object for the wall
    dora_indicators: 2 x 5 array of Tile objects that are doras. One row for dora, one for ura dora
    doras_index: TileIndex object for doras
    deck: TileIndex object for the remaining cards in the deck (dead cards)
    Arrays of Tile objects will be fed to graphics, lists of TileIndex will be fed to NN
    '''
    # Initialize full deck of tiles
    deck = TileIndex()
    deck.full_deck(mode)

    # Create array that contains the denominator of the probability to pick a red tile
    reds = np.array([4, 4, 4])

    # Initialize a tile picker that contains all tile IDs
    # ID of a tile will be removed if out of such tile
    picker = np.linspace(0, 33, 34)
    if mode == 3:
        picker = np.delete(picker, np.s_[1:8])

    # Initialize and pick hands and hands_index
    hands = np.ndarray((mode, ), dtype=Tile)
    hands_index = np.ndarray((mode, ), dtype=TileIndex)
    for i in range(mode):
        tiles, index, deck, picker, reds = tile_picker(13, deck, picker, reds)
        tiles = np.append(tiles, None)
        hands[i] = tiles
        hands_index[i] = index
    
    # Determine wall length, initialize and pick wall and wall_index
    wall_len = 55 if mode == 3 else 70
    wall, wall_index, deck, picker, reds = tile_picker(wall_len, deck, picker, reds)

    # Initialize and pick doras and doras_index
    dora_indicators = np.ndarray((2, ), dtype=Tile)
    doras_index = np.ndarray((2, ), dtype=TileIndex)
    for i in range(2):
        tiles, index, deck, picker, reds = tile_picker(5, deck, picker, reds)
        dora_indicators[i] = tiles
        doras_index[i] = index

    return hands, hands_index, wall, wall_index, dora_indicators, doras_index, deck

def tile_picker(n, deck, picker, reds):
    '''
    Function to automate tile picking. 
    n: int; number of times to pick
    deck: TileIndex; index for tiles available to pick
    picker: 1D array; IDs of tiles available to pick
    reds: iD array; encodes probability for red tiles
    Returns:
    tiles: numpy array of Tile objects
    index: TileIndex object for array of tiles
    deck: TileIndex for remaining tiles in deck
    picker: picker array after tile picking
    reds: reds array after tile picking
    '''
    # Initialize tiles and index
    tiles = np.array([])
    index = TileIndex()

    # Loop n times to pick tiles and add to tiles and index
    for i in range(n):
        id = int(np.random.choice(picker))
        # Check if a five was picked to decide if it's red
        if id in (4, 13, 22):
            redtype = (id - 4) // 9
            if reds[redtype] > 0:
                redprob = np.array([True if i == 0 else False for i in range(reds[redtype])])
                isRed = bool(np.random.choice(redprob))
                reds[redtype] = 0 if isRed is True else reds[redtype] - 1
            else:
                isRed = False
        else:
            isRed = False
        # Add tile to tiles and index
        tile = Tile(id, isRed)
        index.add(tile)
        tiles = np.append(tiles, tile)
        # Remove tile from deck
        deck.remove(tile)
        # Remove ID of tile from picker if that was the last of its type
        if not any(deck.index[id]):
            picker = np.delete(picker, np.where(picker == id))
    
    return tiles, index, deck, picker, reds

if __name__ == "__main__": 
    main()
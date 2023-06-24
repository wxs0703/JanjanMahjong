from dataclasses import dataclass, field
from typing import Callable
import numpy as np
'''
Define Tile and TileIndex dataclasses
Tile objects store the ID of a tile, and whether it's a red tile or not
TileIndex object store information about which tiles a certain entity has into a numpy array
'''
@dataclass
class Tile:
    '''
    Class object for a mahjong tile
    id: ID of the tile
        0-8: Manzu, 1-9 in order
        9-17: Pinzu, 1-9 in order
        18-26: Souzu, 1-9 in order
        27-30: Winds, order in Ton Nan Sha Pei
        31-33: Dragons, order in Haku Hatsu Chun
    isRed: whether or not it's a red tile
    suit: suit of tile represented by integers
        0: Manzu; 1: Pinzu; 2: Souzu; 3: Winds; 4: Dragons
    value: value of tile, winds and dragons represented by integers
        1-4 for ESWN in order; 1-3 for Haku Hatsu Chun in order
    '''
    id: int
    isRed: bool = False
    ranges: np.ndarray = field(default_factory=lambda: np.array([[0, 9], [9, 18], 
                                                                 [18, 27], [27, 31], 
                                                                 [31, 34]]), repr=False)
    suit: int = 0
    value: int = 0

    def __setattr__(self, name, value):
        if name == 'id':
            assert value in range(34), "Tile ID must be within integer values 0-33"
        if name == 'isRed':
            assert isinstance(value, bool), "Must be a boolean"
        self.__dict__[name] = value
    
    def __post_init__(self):
        for i in range(len(self.ranges)):
            a = self.ranges[i][0]
            b = self.ranges[i][1]
            if self.id in range(a, b):
                object.__setattr__(self, 'suit', i)
                object.__setattr__(self, 'value', self.id + 1 - a)

@dataclass
class TileIndex:
    '''
    A 34 x 5 numpy array used to encode all tiles in the game
    First 4 columns are for encoding the existence of all tiles
    column 5 is for encoding whether any of the possessed tiles are red
    '''
    index: np.ndarray = field(default_factory=lambda: np.full((34, 5), False, dtype=bool))
    
    def __setattr__(self, name, value):
        assert isinstance(value, (np.ndarray)), "Index must be a numpy array"
        assert value.shape == (34, 5), "Index shape must be 34 x 5"
        assert value.dtype == 'bool', "Index must be all boolean values"
        self.__dict__[name] = value

    def exist(self, tile):
        '''
        Checks if tile exists in index
        '''
        # Checks if input tile is a Tile object
        if not isinstance(tile, Tile):
            raise ValueError('tile must be a Tile object')
        
        # Initialize local variables
        id = tile.id
        isRed = tile.isRed
        toCheck = self.index[id]
        exists = False
        
        # Check conditions depending on if is searching for red tile
        if isRed is True:
            if toCheck[4]:
                exists = True
        else:
            if toCheck[4]:
                if toCheck[1]:
                    exists = True
            else:
                if toCheck[0]:
                    exists = True

        return exists
    
    def add(self, tile):
        '''
        Adds a Tile object to the index
        '''
        # Checks if input tile is a Tile object
        if not isinstance(tile, Tile):
            raise ValueError('tile must be a Tile object')

        # Initialize local variables
        id = tile.id
        isRed = tile.isRed
        toAdd = self.index[id]
        added = False

        # Checks if all 4 of input tile are already in index
        if toAdd[3]:
            raise IndexError('All 4 of such tile already in index')
        
        # Loops target row in index to add the tile
        for i, v in enumerate(toAdd[:4]):
            v = bool(v)
            # Adds tile to first 4 columns
            if v is False and added is False:
                v = not v
                added = True
            toAdd[i] = v
        # Tick True to column 5 if red tile
        if isRed is True:
            toAdd[4] = True
        
        # Replace column in index with new column
        self.index[id] = toAdd
    
    def remove(self, tile):
        '''
        Removes tile from index, if it exists
        '''
        # Check if tile exists in index
        if not self.exist(tile):
            raise IndexError('target tile does not exist in index')
        
        # Initialize local variables
        id = tile.id
        isRed = tile.isRed
        toRemove = self.index[id]

        # Loops target row in index to remove target tile 
        for i, v in enumerate(toRemove[:4]):
            v = bool(v)
            if v is False:
                toRemove[i-1] = v
            elif i == 3:
                toRemove[3] = False
        # If red, remove possesion of red tiles
        if isRed is True:
            toRemove[4] = False

        # Replace column in index with new column
        self.index[id] = toRemove
    
    def full_deck(self, mode):
        '''
        Turns index into a full deck based on game mode
        '''
        if mode not in (3, 4):
            raise ValueError('not a valid game mode')
        
        tiles = np.full((34, 4), True, dtype=bool)
        reds = np.full((34, 1), False, dtype=bool)
        reds[4] = True
        reds[13] = True
        reds[22] = True
        if mode == 3:
            tiles[1:8, :] = False
            reds[4] = False
            self.index = np.append(tiles, reds, axis=1)
        elif mode == 4:
            self.index = np.append(tiles, reds, axis=1)
    
    def clear(self):
        '''
        Clears the index to all False values
        '''
        toClear = np.full((34, 5), False, dtype=bool)
        self.index = toClear
    
    def combine_index(self, tileindex):
        '''
        Adds a TileIndex object into another
        '''
        add_reds = tileindex.index[:, 4]
        add_tiles = tileindex.index[:, :4]
        self_reds = self.index[:, 4]
        self_tiles = np.sort(self.index[:, :4])
        new_reds = self_reds + add_reds
        new_tiles = self_tiles + add_tiles
        new_tiles[:, ::-1].sort()
        new_index = np.column_stack((new_tiles, new_reds))

        return new_index
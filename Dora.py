import numpy as np
from Tile import Tile
'''
Define Dora and DoraIndex classes
'''
class Dora(Tile):
    '''
    A subclass of Tile that gets dora attributes
    '''
    pass

class DoraIndex:
    '''
    A 34 x 5 numpy array that encodes all the dora tiles, determined from the Dora objects
    '''
    def __init__(self, index=np.full((34, 5), False, dtype=bool)):
        '''
        Initializes an index. Default value is all False
        '''
        # Check if input index matches requirements
        if not isinstance(index, (np.ndarray)):
            raise ValueError('index must be a numpy array')
        if index.shape != (34, 5):
            raise ValueError('index shape must be 34 x 4')
        if index.dtype != 'bool':
            raise ValueError('index must be all boolean values')
        
        # Set instance index as input index
        self.index = index
    
    def exist(self, tile):
        '''
        Checks if tile exists in dora index
        '''
        # Checks if input tile is a Tile object
        if not isinstance(tile, Tile):
            raise ValueError('tile must be a Tile object')
        
        # Initialize local variables
        id = tile.id
        isRed = tile.isRed
        toCheck = self.index[id]
        exists = False
        
        # Check if dora exists anywhere in index
        if any(toCheck):
            exists = True

        return exists

man9 = Tile(8, False)
man9dora = Dora(man9)
print(man9dora)
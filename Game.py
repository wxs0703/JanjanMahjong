from dataclasses import dataclass, field
import yaml
import numpy as np
import pandas as pd
import h5py as h5
from pathlib import Path

from Tile import Tile, TileIndex
from Player import Player

'''
Define _GameBase private dataclass, and Game and Round public dataclasses
- game_ids in globals.yml is a dictionary that stores game type and game ID
- Games will be logged under its game ID, which will be incremented each time one is logged
- Game type can be named after the purpose or type of the game (eg. test, sanma) and will be 
  in the name of the log file before the game ID
'''

# Set script path to current directory
script_path = Path(__file__, '..').resolve()

# Open globals file and load game id list
with open(script_path.joinpath('globals.yml'), "r") as globalsfile:
    globals = yaml.safe_load(globalsfile)
game_type = globals['game_type']
game_ids = globals['game_ids']

# Private classes, meant for public classes to inherit
@dataclass
class _GameBase:
    '''
    Base class for Game and Round subclasses
    mode: number of players
    wind: round wind, represented by integers 0-3 for ESWN in order
    round: round number
    repeat: repeat number for the round
    names: list of player names
    standing: standing of players as of the current round
    isOver: whether the game/round is over
    '''
    # Init variables
    mode: int = 4
    names: list = field(default_factory=lambda: None, repr=False)

    # Post-init variables
    wind: int = field(default=0, init=False)
    round: int = field(default=1, init=False)
    repeat: int = field(default=0, init=False)
    standing: dict = field(default_factory=lambda: None, init=False)
    isOver: bool = field(default=False, init=False)

    def __post_init__(self):
        if self.names is None:
            object.__setattr__(self, 'names', [f'P{i+1}' for i in range(self.mode)])
        object.__setattr__(self, 'standing', 
                            {k: 35000 if self.mode == 3 else 25000 for k in self.names})


# Public classes
@dataclass
class Game(_GameBase):
    '''
    Class object for a game of Mahjong
    doLogging: whether to log this game, will create a log file if True
    If do logging, game_id and game_type can be edited in globals.yml
    '''
    # Init variables
    doLogging: bool = False

    # Post-init variables
    log: h5.File = field(default_factory=lambda: None, init=False, repr=False)
    game_id: int = field(default=0, init=False)
    game_type: str = field(default=None, init=False)

    def __post_init__(self):
        # Inherit __post_init__ from parent class
        super().__post_init__()
        # If doLogging, set up everything needed for log (game ID, game type, log file)
        if self.doLogging is True:
            global game_type
            global game_ids
            object.__setattr__(self, 'game_type', game_type)
            if game_type not in game_ids:
                object.__setattr__(self, 'game_id', 0)
                game_ids.update({str(self.game_type): 0})
            else:
                object.__setattr__(self, 'game_id', game_ids[self.game_type])
                game_ids[str(self.game_type)] += 1
            object.__setattr__(self, 'log', h5.File(f'{self.game_type} {self.game_id}', 'w'))
            self.log.create_dataset('Player names', (self.mode, ), data=self.names)
            self.log.create_group('East round')
            ### remember to find way to save game_ids back to globals
    
    def update():
        pass

@dataclass
class Round(_GameBase):
    '''
    Class object for a round of Mahjong
    '''
    # Init variables
    players: np.ndarray = field(default_factory=lambda: np.array([]), repr=False)
    hands: np.ndarray = field(default_factory=lambda: np.array([]), repr=False)
    wall: TileIndex = field(default_factory=lambda: TileIndex(), repr=False)
    doras: np.ndarray = field(default_factory=lambda: np.array([]), repr=False)
    deck: TileIndex = field(default_factory=lambda: TileIndex(), repr=False)

    # Post-init variables
    opens: np.ndarray = field(default_factory=lambda: None, init=False, repr=False)
    discards: np.ndarray = field(default_factory=lambda: None, init=False, repr=False)
    turn: int = field(default=0, init=False)
    last_action: str = field(default=None, init=False)
    last_discard: Tile = field(default_factory=lambda: None, init=False, repr=False)
    last_draw: Tile = field(default_factory=lambda: None, init=False, repr=False)
    step: bool = field(default=False, init=False, repr=False)
    last_step: bool = field(default=True, init= False, repr=False)
    gameboard: dict = field(init= False, repr=False)
    
    @property
    def gameboard(self):
        return self._gameboard
    
    @gameboard.setter
    def gameboard(self, gameboard):
        '''
        Set gameboard using all the TileIndexes, and make sure they're updated every turn
        '''
        gameboard = {}
        if self.names is None:
            object.__setattr__(self, 'names', [f'P{i+1}' for i in range(self.mode)])
        for i, hand in enumerate(self.hands):
            gameboard.update({f'{self.names[i]} hand': hand.index})
        if self.opens is not None:
            for i, open in enumerate(self.opens):
                gameboard.update({f'{self.names[i]} open': open.index})
        if self.discards is not None:
            for i, open in enumerate(self.discards):
                gameboard.update({f'{self.names[i]} discard': open.index})
        gameboard.update({'wall': self.wall.index})
        gameboard.update({'dora': self.doras[0].index})
        gameboard.update({'ura dora': self.doras[1].index})
        gameboard.update({'deck': self.deck.index})
        self._gameboard = gameboard
    
    def combine_index(self, index1, index2):
        '''
        Combine two TileIndexes together, same as TileIndex.combine_index()
        '''
        add_reds = index1[:, 4]
        add_tiles = index1[:, :4]
        self_reds = index2[:, 4]
        self_tiles = np.sort(index2[:, :4])
        new_reds = self_reds + add_reds
        new_tiles = self_tiles + add_tiles
        new_tiles[:, ::-1].sort()
        new_index = np.column_stack((new_tiles, new_reds))

        return new_index

    def check_action(self, in_turn, out_turn):
        '''
        Checks for possible actions (Chii, Pon, Kan, Riichi, etc.) for all players
        in_turn: str; name of player who is "in turn"
            If step is after discard (False), that player is the one next to draw
            If step is after draw (True), that player is the one that just drew
        '''
        if self.step is True:
            player_index = self.names.index(in_turn)
            player = self.players[player_index]
            if player.isTenpai is True:
                canTsumo = self.check_tsumo(in_turn, player)
            canKan, closed_id, can_open = self.check_self_kan(in_turn)
        else:
            self.check_ron(out_turn)
            self.check_chii(in_turn)
            self.check_pon_kan(out_turn)
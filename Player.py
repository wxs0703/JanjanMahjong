from dataclasses import dataclass, field
import numpy as np
from Tile import Tile, TileIndex
'''
Define Player dataclass
'''
@dataclass
class Player:
    name: str = None
    id: int = 0
    seat: int = 0
    score: int = 25000
    place: int = 1
    hand: np.ndarray = field(default_factory=lambda: np.full((14, ), None, dtype=Tile), repr=False)
    open: np.ndarray = field(default_factory=lambda: np.full((16, ), None, dtype=Tile), repr=False)
    discards: np.ndarray = field(default_factory=lambda: np.array([]), repr=False)
    waits: np.ndarray = field(default_factory=np.array([]), repr=False)
    doras: int = field(default=0, repr=False)
    canChii: bool = field(default=False, repr=False)
    canPon: bool = field(default=False, repr=False)
    canOpenKan: bool = field(default=False, repr=False)
    canClosedKan: bool = field(default=False, repr=False)
    canRiichi: bool = field(default=False, repr=False)
    canRon: bool = field(default=False, repr=False)
    canTsumo: bool = field(default=False, repr=False)
    isRiichi: bool = field(default=False, repr=False)
    isTenpai: bool = field(default=False, repr=False)
    isFuriten: bool = field(default=False, repr=False)
    isWon: bool = field(default=False, repr=False)

@dataclass
class PlayerIndex:
    pass

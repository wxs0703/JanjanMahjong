from dataclasses import dataclass, field
import yaml
import numpy as np
import pandas as pd
import h5py as h5
from Tile import Tile, TileIndex
from Player import Player
from Game import Game
from Action import DrawAction
from Tenpai import Tenpai

test = TileIndex()
hand = [0, 0, 0, 0, 14, 17, 17, 20, 20, 27, 27, 29, 29, 14]
for id in hand:
    test.add(Tile(id))

possible_chitoitsu = Tenpai.check_chitoitsu(test.index)
print(possible_chitoitsu)
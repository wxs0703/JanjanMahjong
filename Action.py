import numpy as np

from Tile import Tile, TileIndex
from Player import Player
from Game import Game, Round

class DrawAction:
    '''
    Class object that contains methods to check possible actions for a single player
    after drawing a tile
    '''
    @staticmethod
    def check_tenpai(hand, open, last_draw):
        pass                

    @staticmethod
    def check_riichi(isTenpai, score):
        if isTenpai is True and score >= 1000:
            return True
        return False
    
    @staticmethod
    def check_furiten(waits, discard):
        if any(waits) in discard:
            return True
        return False
    
    @staticmethod
    def check_tsumo(last_draw, waits):
        if last_draw in waits:
            return True
        return False
    
    @staticmethod
    def check_self_kan(hand, open, last_draw):
        '''
        Checks if the player can make a closed or open Kan with the tiles they have
        Returns separate booleans for whether a close/open Kan is possible, and a list
        of possible tile IDs to close Kan
        '''
        id = last_draw.id
        closed_kan_id = np.where(hand[:, 3] == True)[0]
        canOpenKan = True if id in np.where(open[:, 2] == True)[0] else False
        canClosedKan = True if len(closed_kan_id) != 0 else False
        
        return canClosedKan, closed_kan_id, canOpenKan
    
    @staticmethod
    def check_shuntsu(hand):
        possessed_tiles = hand[:, 0]
        full_shuntsu = []
        wait_shuntsu = []
        waits = []
        for index, value in enumerate(possessed_tiles[:7]):
            if value == True:
                oneRight = hand[index + 1]
                twoRight = hand[index + 2]
                if oneRight == True and twoRight == True:
                    full_shuntsu.append([index, index + 1, index + 2])
                if oneRight == True:
                    wait_shuntsu.append([index, index + 1])
                    if index > 0:
                        waits.append([index - 1, index + 2])
                    else:
                        waits.append([index + 2])
                if twoRight == True:
                    wait_shuntsu.append([index, index + 2])
                    waits.append([index + 1])

        return full_shuntsu, wait_shuntsu, waits
    
class DiscardAction:
    '''
    Class object that contains methods to check possible actions for a single other
    player after a tile has been discarded
    '''
    @staticmethod
    def check_ron(last_discard, waits):
        if last_discard in waits:
            return True
        return False
    
    @staticmethod
    def check_chii(hand, last_discard):
        '''
        Checks if a player can Chii with their current hand
        Returns a boolean and a list of tuples with possible Chii pairs
        '''
        # Define necessary values
        id = last_discard.id
        suit = last_discard.suit
        value = last_discard.value
        if suit >= 3:
            return False, []
        start = suit * 9
        end = start + 9
        check_range = hand[start:end, 0]
        index = value - 1

        # Check if player has the nearby tiles
        oneLeft = check_range[index - 1] if index > 0 else False
        twoLeft = check_range[index - 2] if index > 1 else False
        oneRight = check_range[index + 1] if index < 8 else False
        twoRight = check_range[index + 2] if index < 7 else False

        # Check if any of the nearby tiles are red
        red_L = bool(hand[id-1, 4])
        both_L = bool(hand[id-1, 1]) if red_L == True else False
        red_LL = bool(hand[id-2, 4])
        both_LL = bool(hand[id-2, 1]) if red_LL == True else False
        red_R = bool(hand[id+1, 4])
        both_R = bool(hand[id+1, 1]) if red_R == True else False
        red_RR = bool(hand[id+2, 4])
        both_RR = bool(hand[id+2, 1]) if red_RR == True else False

        # Find possible Chii pairs
        possible_chii = []
        canChii = False
        if oneLeft == True and twoLeft == True:
            possible_chii.append((Tile(id-2, red_LL), Tile(id-1, red_L)))
            canChii = True
            if both_LL == True or both_L == True:
                possible_chii.append((Tile(id-2, False), Tile(id-1, False)))
        if oneLeft == True and oneRight == True:
            possible_chii.append((Tile(id-1, red_L), Tile(id+1, red_R)))
            canChii = True
            if both_L == True or both_R == True:
                possible_chii.append((Tile(id-1, False), Tile(id+1, False)))
        if oneRight == True and twoRight == True:
            possible_chii.append((Tile(id+1, red_R), Tile(id+2, red_RR)))
            canChii = True
            if both_R == True or both_RR == True:
                possible_chii.append((Tile(id+1, False), Tile(id+2, False)))

        return canChii, possible_chii
    
    @staticmethod
    def check_pon_kan(hand, last_discard):
        '''
        Checks whether a player can do a Pon or Kan with the hand that they have
        Returns booleans for ability to Pon/Kan, as well as whether Pons can be made
        with/without red tile
        '''
        id = last_discard.id
        canPon = hand[id, 1]
        canKan = hand[id, 2]
        canPonRed = True if canKan is True and hand[id, 4] is True else False
        return canPon, canPonRed, canKan
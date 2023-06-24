import numpy as np

from Tile import Tile, TileIndex
'''
Module that contains the Tenpai class, which is used to calculate whether or not
a hand is tenpai
'''
class Tenpai:

    @staticmethod
    def check_tenpai(hand, open, last_draw):
        '''
        Checks for and returns all possible ways a player can discard to achieve tenpai
        Returns dict with ID of possible discards and list of ID of waits
        '''
        possible_tenpai = {}
        # If no open hand then check possibility of Chitoitsu or Kokushi
        if all(open[:, 0] is False):
            # Chitoitsu
            possible_chitoitsu = Tenpai.check_chitoitsu(hand)
            if len(possible_chitoitsu) != 0:
                return possible_chitoitsu
            # Kokushi
            possible_kokushi = Tenpai.check_kokushi(hand)
            if len(possible_kokushi) != 0:
                return possible_kokushi

        number_hand, honor_hand = Tenpai.split_hand(hand)
        
        if Tenpai.check_early_return(number_hand, honor_hand) == True:
            return None

        for hand in number_hand:
            pair_ids = np.where(hand[:, 1] == True)[0]
            ankou_ids = np.where(hand[:, 2] == True)[0]
            ankan_ids = np.where(hand[:, 3] == True)[0]
            full_shuntsu, wait_shuntsu, waits = Tenpai.check_shuntsu(hand)

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
    
    @staticmethod
    def check_chitoitsu(hand): ## TESTED ##
        '''
        Checks for possible discard: wait pairs for possible chitoitsu tenpai
        '''
        possible_chitoitsu = {}
        toitsu_ids = np.where(hand[:, 1] == True)[0]
        ankou_ids = np.where(hand[:, 2] == True)[0]
        ankan_ids = np.where(hand[:, 3] == True)[0]
        single_ids = np.where((hand[:, 0] == True) & (hand[:, 1] == False))[0]
        if len(toitsu_ids) == 6 and len(ankou_ids) < 2 and len(ankan_ids) == 0:
            possible_discards = np.append(single_ids, ankou_ids)
            for discard in possible_discards:
                wait = np.delete(single_ids, np.where(single_ids == discard))
                if len(wait) != 0:
                    possible_chitoitsu.update({discard: wait[0]})

        return possible_chitoitsu
    
    @staticmethod
    def check_kokushi(hand): ## TESTED ##
        '''
        Checks for possible discard: wait pairs for possible kokushi tenpai
        '''
        kokushi_ids = [0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33]
        kokushi_index = TileIndex()
        for id in kokushi_ids:
            kokushi_index.add(Tile(id))
        difference_index = np.subtract(hand.astype(int), kokushi_index.index.astype(int))
        waits = np.where(difference_index[:, 0] == -1)[0]
        if len(waits) == 0:
            return {np.where(difference_index[:, 0] == 1)[0][0]: kokushi_ids}
        elif len(waits) == 1:
            pair_orphans = np.intersect1d(np.where(difference_index[:, 1] == 1)[0], kokushi_ids)
            if len(pair_orphans) == 2:
                return {pair_orphans[0]: waits[0], pair_orphans[1]: waits[0]}
            elif len(pair_orphans) == 1:
                third_orphan = hand[pair_orphans[0], 2]
                discard = np.where(difference_index[:, 0] == 1)[0]
                return {discard[0] if third_orphan == False else pair_orphans[0]: waits[0]}
            
        return {}
    
    @staticmethod
    def split_hand(hand):
        '''
        Split hand into number hand and honor hand (Winds and Dragons)
        '''
        manzu_hand = hand[0:9, :]
        pinzu_hand = hand[9:18, :]
        souzu_hand = hand[18:27, :]
        honor_hand = hand[27:, :]
        number_hand = np.array([manzu_hand, pinzu_hand, souzu_hand])

        return number_hand, honor_hand

    @staticmethod
    def check_early_return(number_hand, honor_hand):
        '''
        Returns whether to return early by finding certain impossible tenpai variations
        '''
        # More than 2 isolated honor tiles or pairs
        if len(np.where((honor_hand[:, 0] == True) & (honor_hand[:, 2] == False))[0]) > 2:
            return True
        # 2 or more suits with 2 or less tiles that are not pairs
        # 2 or more 2-wide gaps of singular tiles
        isolated_suit = 0
        num_gaps = 0
        for hand in number_hand:
            if True not in hand[:, 1]:
                num_tiles = hand.count_nonzero(hand == True)
                if num_tiles < 3:
                    isolated_suit += 1
                unique_tiles = np.where(hand[:, 0] == True)[0]
                if num_tiles < 6:
                    for i, v in enumerate(unique_tiles[1:]):
                        num_gaps += 1 if v - unique_tiles[i-1] > 2 else 0
        if isolated_suit > 1 or num_gaps > 1:
            return True
        
        return False
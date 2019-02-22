'''
#CASINO RULES
    - Dealer blackjack automatically ends round, unless player has one too then a push. [Dealer either receives a hole card, or the player’s original bet only is lost if the player doubles down or splits a pair and the dealer gets a blackjack.] 
    - No Blackjack after splitting hands
    - 3 times 7 is NOT counted as a BlackJack (can be changed)
    - Blackjack pays 3 to 2 (can be changed)
    - Dealer stands on soft 17. (Can adjust: DEALER_HITS_SOFT = False)
    - You may double down on any 2 original cards.  
    - You may NOT double down after splitting a pair. (Can adjust: DOUBLE_AFTER_SPLIT = False)
    - You may split any pair. 
    - No surrender. (Can adjust: LATE_SURRENDER = False)
    - Split aces receive only one card each. (Can adjust)
    - You may resplit any pair except aces. (Can adjust)
    - Player can resplit up to 4 hands (Can adjust)
    -
    #TODO: CURRENTLY NOT IMPLEMENTED -- Need to implement these rules
    - Insurance is allowed up to one-half the player’s bet, and pays 2 to 1. 
    - DOULBE_ONLY_ON_CARD = [1:11] #9:11, 10:11 or 1:11 (any)
 
#LEGEND:
A Hand is a single hand of Blackjack, consisting of two or more cards
A Round is single round of Blackjack, in which one or more players play their hands against the dealer's hand
A Shoe consists of multiple card decks consisting of SHOE_SIZE times 52 cards
A Game is a sequence of Rounds that starts with a fresh Shoe and ends when the Shoe gets reshuffled



============================

1. Dealer stands on soft 17. 
2. You may double down on any 2 original cards. 
3. You may not double down after splitting a pair. 
4. You may split any pair. 
5. You may resplit any pair except aces. 
6. Split aces receive only one card each. 
7. No surrender. 
8. Dealer either receives a hole card, or the player’s original bet only is lost if the player doubles down or splits a pair and the dealer gets a blackjack. 
9. Insurance is allowed up to one-half the player’s bet, and pays 2 to 1. 
10. Player blackjack is paid 3 to 2.


# Decks	Advantage
1	+0.02%
2	-0.31%
3	-0.43%
4	-0.48%
5	-0.52%
6	-0.54%
7	-0.55%
8	-0.57%

Effects in Percent
Common Rules	1-Deck	2-Deck	Multi-Deck
Double on 10-11 only:	-0.26	-0.21	-0.18
Double on 9-10-11 only:	-0.13	-0.11	-0.09
Hits Soft 17:	-0.19	-0.20	-0.21
No Resplits:	-0.02	-0.03	-0.04
Double After Splits:	+0.14	+0.14	+0.14
Resplit Aces:	+0.03	+0.05	+0.07
Draw to Split Aces:	+0.14	+0.14	+0.14
Late Surrender:	+0.02	+0.05	+0.08
Late Surrender (H soft17):	+0.03	+0.06	+0.09
No Ace Splits:	-0.16	-0.17	-0.18

'''
import sys
import os
from random import shuffle
import matplotlib.pyplot as plt
import time
#import pandas as pd
#import random
#import multiprocessing
#import math

import numpy as np
import scipy.stats as stats
#import pylab as pl

#START IMPORTER
#from importer.StrategyImporter import StrategyImporter
import csv #for csv.DictReader



class StrategyImporter(object):
    """
    Importer of the startegy CSV file
    Such as BlackJack's Basic Strategy
    """
    hard_strategy = {}
    soft_strategy = {}
    pair_strategy = {}
    dealer_strategy = {}

    def __init__(self, player_file):
        self.player_file = "BasicStrategy.csv"
        #self.player_file = "NoBust.csv" #no hits above 12
        #self.player_file = "BadStrategy.csv" #AROUND -0.5 EDGE - REMOVED SOME OF THE DOUBLING/SPLITTING/SURRENDERING
        #self.player_file = "SplitTens.csv" #For testing splitting tens

    #TODO: Revalue these to match the lines in the CSV file without odd counting
    def import_player_strategy(self):
        hard = 21 #21 - 17 lines
        soft = 21 #21 - 10 lines
        pair = 20 #20 - 9 lines

        with open(self.player_file, 'r') as player_csv:
            reader = csv.DictReader(player_csv, delimiter = ';')
            for row in reader:
                if hard >= 5: #5 get to 1
                    self.hard_strategy[hard] = row
                    hard -= 1  # Subtract 1
                elif soft >= 12: #12 - Get to 1
                    self.soft_strategy[soft] = row
                    soft -= 1 #subtract 1
                elif pair >= 4: #4 #gets to one
                    self.pair_strategy[pair] = row
                    pair -= 2 #-2: Subtract 1

        return self.hard_strategy, self.soft_strategy, self.pair_strategy      
#END IMPORTER

scriptDirectory = os.path.dirname(os.path.realpath(__file__))

'''
#5mil hands takes 15minutes. Need 5m hands for proper sample. 
NUMBER OF HANDS FOR DECENT BJ SIMULATION SAMPLE: 
    To differentiate a winrate of WR from (1-f)*WR, you need 
(z*SD/WR/f)^2 hands. So for a typical blackjack game with 
WR = -0.01, SD = 1.15, z = 2 (1-sided certainty of 98%), 
and f = .1 (WR is more than 10% off), you're looking at about 5 million hands.
'''
NUM_HANDS = 1000000 #5000000 default
VAR_PRINT = False #Print all the hands
HIDE_DEALER_SECOND_CARD = False # display or hide second dealer card at first

DECK_SIZE = 52.0 #52 is the standard deck - DO NOT ADJUST

CARDS = {
    "Ace": 11, "Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6,
    "Seven": 7, "Eight": 8, "Nine": 9, "Ten": 10, "Jack": 10, "Queen": 10,
    "King": 10
    }

#COUNTING STRATEGIES
NO_STRATEGY = {
    "Ace": 0, "Two": 0, "Three": 0, "Four": 0, "Five": 0, "Six": 0, "Seven": 0,
    "Eight": 0, "Nine": 0, "Ten": 0, "Jack": 0, "Queen": 0, "King": 0
    }
HI_LO_STRATEGY = {
    "Ace": -1, "Two": 1, "Three": 1, "Four": 1, "Five": 1, "Six": 1, "Seven": 0,
    "Eight": 0, "Nine": 0, "Ten": -1, "Jack": -1, "Queen": -1, "King": -1
    }
BASIC_OMEGA_II = {
    "Ace": 0, "Two": 1, "Three": 1, "Four": 2, "Five": 2, "Six": 2, "Seven": 1,
    "Eight": 0, "Nine": -1, "Ten": -2, "Jack": -2, "Queen": -2, "King": -2
    }
#SELECT WHICH COUNTING STRATEGY (HI_LO_STRATEGY  - BASIC_OMEGA_II)
COUNTING_STRATEGY = HI_LO_STRATEGY

COUNTING_RULES = {
    #STANDARD RULES
    'SIZE_OF_BET': 100.0, #STANDARD SIZE OF BET REGARDLESS OF COUNT, can be any integer, is multiplied by bet_spread
    'SHOE_PENETRATION_REMAINING': 0.25, #reshuffle when the shoe gets to this amount -- reshuffle after 75% (minus 1.0 from the set number) of all cards are played    
    #WHETHER TO ADJUST BETS BASED ON COUNT
    'COUNTING_ADJ_BETS': False, #True/False - Adjust the bets based on counting
    #TOP VALUES (WHEN COUNT IS VERY HIGH)
    'TRUE_COUNT_TOP': 10, #Institute BET_SPREAD if true count >= this number - default was 6
    'TOP_BET_SPREAD': 20.0, #Bet n-times (if set to 20.0, 20-times) the money if the count is player-favorable
    #MID VALUES (WHEN COUNT IS HIGH)
    'TRUE_COUNT_MID': 3, #Institute BET_SPREAD if true count >= this number - default was 6
    'MID_BET_SPREAD': 10.0, #Bet n-times (if set to 20.0, 20-times) the money if the count is player-favorable   
        }

BLACKJACK_RULES = {
    'SHOE_SIZE': 6, #Default 6 -- number of decks in shoe (6 starts us at -0.54% +0.07 +0.14 == -0.33%)
    'MAX_HANDS': 3, #Default 4 -- ('2' for No resplits lowers EV -0.04% -- MAX_HANDS of 4 allows 3 resplits
    'BLACKJACK_PAYOUT': 1.5, #Default 1.5 (6:5 LOWERS PLAYERS EV -1.71, 1:1 LOWERS -2.26, and 2:1 raises +2.26) blackjack payout is 1.5 (3:2) or 1.2 (6:5)
    'triple7': False,  # Count 3x7 as a blackjack
    'DEALER_HITS_SOFT': False, #Default=False (True lowers EV -0.21% for the player) True/Hit H17 - False/Stand S17 -- if dealer should HIT soft 17, or False if dealer should STAND on soft 17
    'DOUBLE_AFTER_SPLIT': False, #Default=False (True raises EV +0.14% for the player) DAS 
    'LATE_SURRENDER': True, #Default False -- Late (True) raises player EV +0.08 -- SURRENDER RULE - Late or No Surrender #True still checks for BJ before player can surrender
    'RESPLIT_ACES': False, #Default False -- True raises EV +0.07% -- RSA - Allows Resplitting Aces
    'HIT_SPLIT_ACES': False, #Default False -- True raises EV +0.14% (forces DRAW ACES)- True Allows split aces to be hit again. 
}

##############################
# All False: -53 (expected -.54)
# H17: ~ -.6 (expected -.75)
# DAS: ~ -.4 (expected -.4)


#CALCULATE EXPECTED VALUE
Expected_Value = 0
if BLACKJACK_RULES['SHOE_SIZE'] == 1:
    Expected_Value += 0.02
elif BLACKJACK_RULES['SHOE_SIZE'] == 2:
    Expected_Value += -0.02
elif BLACKJACK_RULES['SHOE_SIZE'] == 3:
    Expected_Value += -0.43
elif BLACKJACK_RULES['SHOE_SIZE'] == 4:
    Expected_Value += -0.48
elif BLACKJACK_RULES['SHOE_SIZE'] == 5:
    Expected_Value += -0.52
elif BLACKJACK_RULES['SHOE_SIZE'] == 6:
    Expected_Value += -0.54
elif BLACKJACK_RULES['SHOE_SIZE'] == 7:
    Expected_Value += -0.55
elif BLACKJACK_RULES['SHOE_SIZE'] >= 7:
    Expected_Value += -0.57
if BLACKJACK_RULES['MAX_HANDS'] <= 2:
    Expected_Value += -0.04
#no change if 3:2 (1.5)   
if BLACKJACK_RULES['BLACKJACK_PAYOUT'] == 1: #1:1
    Expected_Value += -2.26
if BLACKJACK_RULES['BLACKJACK_PAYOUT'] == 1.2: #6:5
    Expected_Value += -1.71
if BLACKJACK_RULES['DEALER_HITS_SOFT'] == True: 
    Expected_Value += -0.21
if BLACKJACK_RULES['DOUBLE_AFTER_SPLIT'] == True: 
    Expected_Value += 0.14 #plus
if BLACKJACK_RULES['LATE_SURRENDER'] == True:
    Expected_Value += 0.08 #plus
if BLACKJACK_RULES['RESPLIT_ACES'] == True:
    Expected_Value += 0.07 #plus
if BLACKJACK_RULES['HIT_SPLIT_ACES'] == True:
    Expected_Value += 0.14 #plus


'''
#####  - ODDS -  #########
STARTING EV FOR NUMBER OF DECKS
# Decks	Advantage
1	+0.02%
2	-0.31%
3	-0.43%
4	-0.48%
5	-0.52%
6	-0.54% ###
7	-0.55%
8	-0.57%

6/4/1.5/all F: expect -0.54%
-0.553%
-0.497%
-0.546%
-0.613%
-0.516%
edge_v = [-0.553, -0.497, -0.546, -0.613, -0.516]
np.mean(edge_v)

AVERAGE = -0.545

0.58
'''

HARD_STRATEGY = {}
SOFT_STRATEGY = {}
PAIR_STRATEGY = {}

class Card(object):
    """
    Represents a playing card with name and value.
    """
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return "%s" % self.name

    @property
    def count(self):
        return COUNTING_STRATEGY[self.name]

class Shoe(object):
    """
    Represents the shoe, which consists of a number of card decks.
    """
    reshuffle = False

    def __init__(self, decks):
        self.count = 0
        self.count_history = []
        self.ideal_count = {}
        self.decks = decks
        self.cards = self.init_cards()
        self.init_count()

    def __str__(self):
        s = ""
        for c in self.cards:
            s += "%s\n" % c
        return s

    def init_cards(self):
        """
        Initialize the shoe with shuffled playing cards and set count to zero.
        """
        self.count = 0
        self.count_history.append(self.count)

        cards = []
        for d in range(self.decks):
            for c in CARDS:
                for i in range(0, 4):
                    cards.append(Card(c, CARDS[c]))
        shuffle(cards)
        return cards

    def init_count(self):
        """
        Keep track of the number of occurrences for each card in the shoe in
        the course over the game. ideal_count is a dictionary containing (card
        name - number of occurrences in shoe) pairs
        """
        for card in CARDS:
            self.ideal_count[card] = 4 * BLACKJACK_RULES['SHOE_SIZE']

    def deal(self):
        """
        Returns:    The next card off the shoe. If the shoe penetration is 
                    reached, the shoe gets reshuffled.
        """
        if self.shoe_penetration() < COUNTING_RULES['SHOE_PENETRATION_REMAINING']:
            self.reshuffle = True
        card = self.cards.pop()

        assert self.ideal_count[card.name] > 0, "Either a cheater or a bug!"
        self.ideal_count[card.name] -= 1

        self.do_count(card)
        return card

    def do_count(self, card):
        """
        Add the dealt card to current count.
        """
        self.count += COUNTING_STRATEGY[card.name]
        self.count_history.append(self.truecount())

    def truecount(self):
        """
        Returns: The current true count.
        """
        return self.count / (self.decks * self.shoe_penetration())

    def runningcount(self):
        """
        Returns: The current actual count.
        """
        return self.count

    def shoe_penetration(self):
        """
        Returns: Ratio of cards that are still in the shoe to all initial
                 cards.
        """
        return len(self.cards) / (DECK_SIZE * self.decks)

class Hand(object):
    """
    Represents a hand, either from the dealer or from the player
    """
    _value = 0
    _aces = []
    _aces_soft = 0
    splithand = False
    surrender = False
    doubled = False

    def __init__(self, cards):
        self.cards = cards

    def __str__(self):
        h = ""
        for c in self.cards:
            h += "%s[%s] " % (c, c.count)
        return h

    @property
    def value(self):
        """
        Returns: The current value of the hand (aces are either counted as 1 or
        11).
        """
        self._value = 0
        for c in self.cards:
            self._value += c.value
        
        #if busted but have an ace, revalue from 11 to 1
        if self._value > 21 and self.aces_soft > 0:
            for ace in self.aces:
                if ace.value == 11:
                    self._value -= 10
                    ace.value = 1
                    if self._value <= 21:
                        break

        return self._value

    @property
    def aces(self):
        """
        Returns: The all aces in the current hand.
        """
        self._aces = []
        for c in self.cards:
            if c.name == "Ace":
                self._aces.append(c)
        return self._aces

    @property
    def aces_soft(self):
        """
        Returns: The number of aces valued as 11
        """
        self._aces_soft = 0
        for ace in self.aces:
            if ace.value == 11:
                self._aces_soft += 1
        return self._aces_soft

    def soft(self):
        """
        Determines whether the current hand is soft (soft means that it
        consists of aces valued at 11).
        """
        if self.aces_soft > 0:
            return True
        else:
            return False

    def splitable(self):
        """
        Determines if the current hand can be split.
        """
        #Added to also check for value as just name wouldnt consider different face cards as splitable
        # In any case, it is still terrible strategy to split 10s.
        #check if length is 2, and checks to see if value is same (for TJQK) and names (for Ace 1 and 11)
        if self.length() == 2 and (self.cards[0].name == self.cards[1].name or self.cards[0].value == self.cards[1].value):
            return True
        else:
            return False

    def blackjack(self):
        """
        Check a hand for a blackjack, taking the defined BLACKJACK_RULES into
        account.
        """
        if not self.splithand and self.value == 21:
            if (all(c.value == 7 for c in self.cards) and BLACKJACK_RULES['triple7']):
                return True
            elif self.length() == 2:
                return True
            else:
                return False
        else:
            return False

    def busted(self):
        """
        Checks if the hand is busted.
        """
        if self.value > 21:
            return True
        else:
            return False

    def add_card(self, card):
        """
        Add a card to the current hand.
        """
        self.cards.append(card)

    def split(self):
        """
        Split the current hand.
        Returns: The new hand created from the split.
        """
        self.splithand = True
        c = self.cards.pop()
        new_hand = Hand([c])
        new_hand.splithand = True
        return new_hand

    def length(self):
        """
        Returns: The number of cards in the current hand.
        """
        return len(self.cards)
'''
class Log(object):
    """
    Represents a history of hands and associated actions.
    """
    def __init__(self):
        try:
            self.hands = pd.read_pickle(scriptDirectory+'/player_history')
        except FileNotFoundError:
            self.hands = None

    def __str__(self):
        print(self.hands)

    def add_hand(self, action, hand, dealer_hand, shoe):
        d = {'hand': [hand.value], 'soft': [hand.soft()],
             'splitable': [hand.splitable()],
             'dealer': [dealer_hand.cards[0].value],
             'truecount': [shoe.truecount()], 'action': [action.upper()]
             }
        if self.hands is None:
            self.hands = pd.DataFrame(data=d)
        else:
            self.hands = self.hands.append(pd.DataFrame(data=d))

    def save(self):
        self.hands.to_pickle(scriptDirectory+'/player_history')
'''

class Player(object):
    """
    Represent a player
    """
    def __init__(self, hand=None, dealer_hand=None):
        self.hands = [hand]
        self.dealer_hand = dealer_hand
        self.autoplay = True
        self.special_trigger = False
        #self.history = Log()

    def set_hands(self, new_hand, new_dealer_hand):
        self.hands = [new_hand]
        self.dealer_hand = new_dealer_hand

    def play(self, shoe):
        for hand in self.hands:
            if VAR_PRINT == True: print("PLAYING HAND: %s" % hand)
            self.play_hand(hand, shoe)

    def play_hand(self, hand, shoe):
        #if from a split hand
        if hand.length() < 2:
            #revalue aces if hand was split
            if hand.cards[0].name == "Ace":
                hand.cards[0].value = 11
            #add new card to splitted hand
            self.hit(hand, shoe)
            if VAR_PRINT == True: print("PLAYER HAND:", hand)

        #while not hand.busted() and not hand.blackjack():            
        while not hand.busted() and not hand.blackjack() and not self.dealer_hand.blackjack():          
            if self.autoplay:
                if hand.soft():
                    flag = SOFT_STRATEGY[hand.value][self.dealer_hand.cards[0].name]
                    if VAR_PRINT == True: print("SOFT STRATEGY (d:", self.dealer_hand.cards[0].name, "| p:", hand.value, ") - ", flag)
                elif hand.splitable():
                    flag = PAIR_STRATEGY[hand.value][self.dealer_hand.cards[0].name]
                    if VAR_PRINT == True: print("PAIR STRATEGY (d:", self.dealer_hand.cards[0].name, "| p:", hand.value, ") - ", flag)
                else:
                    flag = HARD_STRATEGY[hand.value][self.dealer_hand.cards[0].name]
                    if VAR_PRINT == True: print("HARD STRATEGY (d:", self.dealer_hand.cards[0].name, "| p:", hand.value, ") - ", flag)
            #Not autoplay
            else:
                print("DEALER HAND: %s (%d)" % (self.dealer_hand, self.dealer_hand.value))
                print("PLAYER HAND: %s (%d)" % (self.hands[0], self.hands[0].value))
                print("Count=%s, Penetration=%s\n" %
                      ("{0:.2f}".format(shoe.count),
                       "{0:.2f}".format(shoe.shoe_penetration())))
                flag = input("Action (H=Hit, S=Stand, D=Double, P=Split, "
                             "Sr=Surrender, Q=Quit): ")
                #if flag != 'Q':
                    #self.history.add_hand(flag, hand, self.dealer_hand, shoe)

            #DOUBLE
            if flag.upper() == 'D':
                #only two cards in hand
                if hand.length() == 2:
                    #if more than 1 hands (split) and NOT allowed
                    if len(game.player.hands) > 1 and BLACKJACK_RULES['DOUBLE_AFTER_SPLIT'] != True: #assign in casino rules at top
                        flag = 'H'
                        if VAR_PRINT == True: print("DOUBLE AFTER SPLIT IS NOT ALLOWED!")
                    else:
                        hand.doubled = True
                        self.hit(hand, shoe)
                        break
                else:
                    flag = 'H'
                if hand.doubled == True:
                    if VAR_PRINT == True: print("DOUBLE DOWN")
            
            #SURRENDER
            if flag.upper() == 'SR':
                if hand.length() == 2 and BLACKJACK_RULES['LATE_SURRENDER'] == True:
                    if VAR_PRINT == True: print("SURRENDER")
                    hand.surrender = True
                    break
                else:
                    flag = 'H'
                    if VAR_PRINT == True: print("SURRENDER FLAG, BUT HIT")


            #SPLIT (also checks for MAX_HANDS and RESPLIT_ACES)
            #USE TO BE AFTER HIT, BUT NEEDS TO BE BEFORE 
            if flag.upper() == 'P':
                #if player hands (such as 2) is greater than max hands (such as 4) then hit instead of splitting again
                if len(game.player.hands) > BLACKJACK_RULES['MAX_HANDS']:
                    flag = 'H'
                    #self.special_trigger = True
                    if VAR_PRINT == True: print("MAX SPLIT, SO HIT")
                #if already a split hand, and an ace, and the rules disallow
                elif len(game.player.hands) > 1 and BLACKJACK_RULES['RESPLIT_ACES'] != True and (game.player.hands[0].cards[0].name == 'Ace'): #shouldnt need this ace the first hand would also be ace -- or game.player.hands[1].cards[0].name == 'Ace'):
                    flag = 'H'
                    if VAR_PRINT == True: print("RESPLITTING ACES (RSA) NOT ALLOWED.")
                #TODO: can only split 9-11 valued cards
                #elif hand.cards[0].value == 10:
                else:
                    if VAR_PRINT == True: print("SPLITTING HAND")
                    self.split(hand, shoe)

            #HIT
            #TODO: DRAW ACES -- Check to see if split aces and if it is allowed to hit, then force stand.
            if flag.upper() == 'H':
                #if split hand, and ace, and NOT allowed to be hit (must draw or stand since one card already drawn from the start of the play_round function)
                if len(game.player.hands) > 1 and game.player.hands[0].cards[0].name == 'Ace' and BLACKJACK_RULES['HIT_SPLIT_ACES'] != True:
                    flag = 'S'
                    if VAR_PRINT == True: print("STANDING. ONLY ONE DRAW ALLOWED ON SPLIT ACES!")
                    break
                elif hand.doubled == True: #just in case doubled hand tries to hit again;
                    #TODO: Need to see if this function is ever meet, if not delete.
                    flag = 'S' #stand 
                else:
                    self.hit(hand, shoe)



            #STAND
            if flag.upper() == 'S':
                if VAR_PRINT == True: print("STAND")
                break
                #return

            #QUIT
            if flag.upper() == 'Q':
                exit()

    def hit(self, hand, shoe):
        c = shoe.deal()
        hand.add_card(c)
        if VAR_PRINT == True: print("PLAYER HIT: %s (%s)" % (c, hand.value))
        ##print("PLAYER HIT: %s (%s - %s)" % (c, hand, hand.value))
            

    def split(self, hand, shoe):
        self.hands.append(hand.split())
        if VAR_PRINT == True: print("SPLIT %s" % hand)
        self.play_hand(hand, shoe)

class Dealer(object):
    """
    Represent the dealer
    """
    def __init__(self, hand=None):
        self.hand = hand

    def set_hand(self, new_hand):
        self.hand = new_hand

    def play(self, shoe):
        #Rule to adjust dealer hitting soft 17 (with ace)
        if BLACKJACK_RULES['DEALER_HITS_SOFT'] == True:
            #if soft ace and over 17
            if self.hand.aces_soft > 0:
                while self.hand.aces_soft > 0 and self.hand.value <= 17:
                    if VAR_PRINT == True: print("DEALER HITTING SOFT ACE!")
                    self.hit(shoe)
            #no soft aces
            while self.hand.value < 17:
                self.hit(shoe)
        else:
            while self.hand.value < 17:
                self.hit(shoe)

    def hit(self, shoe):
        c = shoe.deal()
        self.hand.add_card(c)
        if VAR_PRINT == True: print("DEALER HIT: %s (%s)" % (c, self.hand.value))
        ##print("DEALER HIT: %s (%s - %s)" % (c, self.hand, self.hand.value))
            
'''
class Tree(object):
    """
    A tree that opens with a statistical card and changes as a new
    statistical card is added. In this context, a statistical card is a list of possible values, each with a probability.
    e.g : [2 : 0.05, 3 : 0.1, ..., 22 : 0.1]
    Any value above 21 will be truncated to 22, which means 'Busted'.
    """
    # Returns an array of 6 numbers representing the probability that the final
    # score of the dealer is
    # [17, 18, 19, 20, 21, Busted] 
    # TODO Differentiate 21 and BJ
    # TODO make an actual tree, this is false AF
    #def get_probabilities(self):
        #start_value = self.hand.value
        # We'll draw 5 cards no matter what an count how often we got 17, 18,
        # 19, 20, 21, Busted

    #TODO to test
    def __init__(self, start=[]):
        self.tree = []
        self.tree.append(start)

    def add_a_statistical_card(self, stat_card):
        # New set of leaves in the tree
        leaves = []
        for p in self.tree[-1]:
            for v in stat_card:
                new_value = v + p
                proba = self.tree[-1][p] * stat_card[v]
                if (new_value > 21):
                    # All busted values are 22
                    new_value = 22
                if (new_value in leaves):
                    leaves[new_value] = leaves[new_value] + proba
                else:
                    leaves[new_value] = proba
'''
class Game(object):
    """
    A sequence of Blackjack Rounds that keeps track of total money won or lost
    """
    def __init__(self):
        self.shoe = Shoe(BLACKJACK_RULES['SHOE_SIZE'])

        self.win = 0.0 #hand wins
        self.bet = 0.0 #total stake modified by num hands, double/split/etc.
        self.money = 0.0 #sum of wins by hand

        self.player = Player()
        self.dealer = Dealer()
        
        #new vars
        self.status = ""



    def get_hand_winnings(self, hand):
        win = 0.0
        bet = self.stake #determined in playround def
        status_info = ""
        if not hand.surrender:
            if hand.busted():
                status = "LOST"
                game_stats.append("0") #lost - player busted
            else:
                if self.dealer.hand.blackjack(): #Need to check to see if dealer has blackjack
                    if hand.blackjack():
                        game_stats.append("4") #push - Dealer & Player BJ
                        status = "PUSH"
                        status_info = "DEALER AND PLAYER BOTH HAVE BLACKJACK!"
                    else:
                        game_stats.append("3") #lost - Dealer BJ win
                        status = "LOST" #automatic lost due to dealer blackjack
                        status_info = "DEALER HAS BLACKJACK!"
                elif hand.blackjack(): #Need to check to see if player has blackjack
                    if self.dealer.hand.blackjack():
                        game_stats.append("4") #push - Dealer & Player BJ
                        status = "PUSH"
                        status_info = "DEALER AND PLAYER BOTH HAVE BLACKJACK!"
                    else:
                        game_stats.append("2") #win - Player BJ win
                        status = "WON BLACKJACK"
                        status_info = "PLAYER HAS BLACKJACK!"
                elif self.dealer.hand.busted():
                    game_stats.append("5") #win - dealer busted
                    status = "WON"
                elif self.dealer.hand.value < hand.value:
                    game_stats.append("1") #win - beat dealer
                    status = "WON"
                elif self.dealer.hand.value > hand.value:
                    game_stats.append("7") #lost - dealer won
                    status = "LOST"
                elif self.dealer.hand.value == hand.value:
                    if self.dealer.hand.blackjack():
                        game_stats.append("3") #lost - Dealer BJ win
                        status = "LOST"  # player's non-bj 21 vs dealers blackjack
                        status_info = "DEALER HAS BLACKJACK!"
                    else:
                        game_stats.append("6") #push - same non-BJ hand
                        status = "PUSH"
                else:
                    game_stats.append("9") #error - shouldn't ever get here...
                    
        else:
            game_stats.append("8") #lost - surrender
            status = "SURRENDER"


            
        if status == "LOST":
            win += -1
            win_history.append("0")
        elif status == "WON":
            win += 1
            win_history.append("1")
        elif status == "WON BLACKJACK":
            win += BLACKJACK_RULES['BLACKJACK_PAYOUT'] #variable set at start
            win_history.append("1")
        elif status == "SURRENDER":
            win += -0.5
            win_history.append("0")
   
        if hand.doubled:
            win *= 2
            bet *= 2

        win *= self.stake 
        
        if VAR_PRINT == True and status_info != "": print(status_info)
        
        return win, bet, status


    def play_round(self):
        if self.player.autoplay:
            #
            #
            # DETERMINE BET FOR THE ROUND
            #
            #
            self.stake = COUNTING_RULES['SIZE_OF_BET']
            if COUNTING_RULES['COUNTING_ADJ_BETS'] == True:
                #if counting moderately favorable - bet mid
                if self.shoe.truecount() >= COUNTING_RULES['TRUE_COUNT_MID']: 
                    self.stake = COUNTING_RULES['SIZE_OF_BET'] * COUNTING_RULES['MID_BET_SPREAD']
                #if counting very favorable - bet high
                if self.shoe.truecount() >= COUNTING_RULES['TRUE_COUNT_TOP']: 
                    self.stake = COUNTING_RULES['SIZE_OF_BET'] * COUNTING_RULES['TOP_BET_SPREAD']
        else:
            raw_stake = input("BET (%s): " % self.stake)
            if raw_stake != "":
                try:
                    self.stake = float(raw_stake)
                except ValueError:
                    print("Invalid bet, using default.")
        
        #
        #
        # DEAL CARDS
        #
        #        
        #EUROPEAN DEALING - DEALER DOES NOT HAVE HOLE CARD
        #player_hand = Hand([self.shoe.deal(), self.shoe.deal()])
        #dealer_hand = Hand([self.shoe.deal()])

        #AMERICAN DEALING - DEALER HAS HOLE CARD
        #DEALER NEEDS TWO CARDS TO CHECK FOR BLACKJACK - IMMEDIATE WIN 
        #AMERICAN BLACKJACK RULES. EUROPEAN ONLY HAS ONE AND DEALS LAST
        player_hand = Hand([self.shoe.deal()])
        dealer_hand = Hand([self.shoe.deal()])
        player_hand.add_card(self.shoe.deal())
        dealer_hand.add_card(self.shoe.deal())
        
        self.player.set_hands(player_hand, dealer_hand)
        self.dealer.set_hand(dealer_hand)
 
        #just to track the number of original ace pairs
        #if self.player.hands[0].cards[0].name == 'Ace' and self.player.hands[0].cards[1].name == 'Ace':
        #    DRAW_ACES.append("1") #ace pair
       
        if VAR_PRINT == True:
            if HIDE_DEALER_SECOND_CARD == True:
                print("DEALER HAND: %s" % (self.dealer.hand.cards[0])) #ONLY SHOW 1 DEALER CARD
            else:
                print("DEALER HAND: %s (%d)" % (self.dealer.hand, self.dealer.hand.value)) #SHOW 2 DEALER CARDS
            print("PLAYER HAND: %s (%d)" % (self.player.hands[0], self.player.hands[0].value))

        #
        #
        # PLAY
        #
        #         
        self.player.play(self.shoe)
        self.dealer.play(self.shoe)
        
        #This is to not dealer to hit if player busts, but dealers still hit...
        '''
        if not self.player.hands[0].busted():
            self.dealer.play(self.shoe)
        else:
            dealer_hand.add_card(self.shoe.deal())
        '''

        #
        #
        # DETERMINE WINNINGS
        #
        #         
        for hand in self.player.hands:
            win, bet, status = self.get_hand_winnings(hand)
            self.money += win #total won in all hands of a round
            self.bet += bet #total bet in all hands of a round
            self.stake = bet #individual hand bet
            self.win = win #individual hand winnings
            self.status = status
            
    def get_money(self):
        return self.money #total won in all hands of a round

    def get_bet(self):
        return self.bet  #total bet in all hands of a round

if __name__ == "__main__":
    start_time = time.time()
    importer = StrategyImporter(sys.argv) #fixes "IndexError: list index out of range" #importer = StrategyImporter(sys.argv[1])
    HARD_STRATEGY, SOFT_STRATEGY, PAIR_STRATEGY = (importer.import_player_strategy())
    win_history = [] #simple list of number of wins 1 or losses 0, excluding pushes
    game_stats = [] #list for all the specific features
    bankroll = [] #moneys each round
    bankroll_amt = 0 #for bankroll chart
    moneys = [] #moneys each shoe/game
    bets = []
    countings = []
    nb_hands = 0
    game_num = 0
    bet = 0
    win = 0
    special_trigger = False
    #NUM_HANDS = int(input("How many hands? "))

    #GAMES = 20000
    #for g in range(GAMES):
    while special_trigger == False and nb_hands < NUM_HANDS:
        game_num += 1
        game = Game()
        autoplay = 'y'
        #autoplay = input("Autoplay? (y/n): ")
        if autoplay == 'n':
            game.player.autoplay = False
        while not game.shoe.reshuffle and special_trigger == False and nb_hands < NUM_HANDS:
            if VAR_PRINT == True: print('%s GAME no. %d - Hand %d %s' % (20 * '#', game_num, nb_hands, 20 * '#'))
            game.play_round()
            #print("DEALER HAND: %s (%d)" % (game.dealer.hand, game.dealer.hand.value))
            special_trigger = game.player.special_trigger
            bet_hand = 0
            win_hand = 0
            if VAR_PRINT == True: print("DEALER HAND: %s (%d)" % (game.dealer.hand, game.dealer.hand.value))
            for x in range(len(game.player.hands)): #in case of split, print all the hands
                nb_hands += 1
                
                bet += game.stake
                win += game.win
                bet_hand += game.stake
                win_hand += game.win
                bankroll_amt += game.win #per hand
                #print('%s HAND - %s GAME no. %d - Hand %d %s' % (bankroll_amt, 20 * '#', game_num, nb_hands, 20 * '#'))
                bankroll.append(bankroll_amt) #per hand
                
                if VAR_PRINT == True:
                    print('Win: %s / Bet: %s / Status: %s' % game.get_hand_winnings(game.player.hands[x]))
                    print("PLAYER HAND %s: %s (%d)" % (x+1, game.player.hands[x], game.player.hands[x].value))
                    print('BET %s AND %s %s' % (game.stake, game.status, game.win))
            if VAR_PRINT == True:
                print("CURRENT BET: %s" % "{0:.2f}".format(bet_hand)) #doesn't include total from splits
                print("CURRENT WIN: %s" % "{0:.2f}".format(win_hand))
                if game.player.hands[0].doubled:
                    print("DOUBLE")
                print("GAME BANKROLL: %s" % "{0:.2f}".format(game.get_money()))
                print("GAME BETS: %s" % "{0:.2f}".format(game.get_bet()))
                print("TRUE COUNT: %s" % "{0:.2f}".format(game.shoe.truecount()))
                print("RUNNING COUNT: %s" % "{0:.2f}".format(game.shoe.runningcount()))

        #each game
        moneys.append(game.get_money()) #per game
        #print('%s GAME ----- %s Each game GAME no. %d - Hand %d %s' % (moneys[-1], 20 * '#', game_num, nb_hands, 20 * '#'))

        bets.append(game.get_bet())
        countings += game.shoe.count_history
        if VAR_PRINT == True:
            print("WIN for Game no. %d: %s (%s bet) - Hand # %s" % (game_num, "{0:.2f}".format(game.get_money()), "{0:.2f}".format(game.get_bet()), nb_hands))


    '''
    if game.player.autoplay is False:
        game.player.history.save()
    '''

    '''
    for value in moneys:
        sume += value
    for value in bets:
        total_bet += value
    '''

    def longest_seq(A, key_num):
        '''
        Returns the longest sequence of wins or losses
        'A' is list name and 'key_num' is the value to find sequence
        '''
        import itertools,operator
        r = max((list(y) for (x,y) in itertools.groupby((enumerate(A)),operator.itemgetter(1)) if x == key_num), key=len)
        longest_start_index = r[0][0] # prints 12
        longest_end_index = r[-1][0] # prints 19
        longest = longest_end_index - longest_start_index
        return longest;

    print("\n%s hands overall, %0.2f hands per game on average" % ("{0:,.0f}".format(nb_hands), (float(nb_hands) / game_num)))
    print("")
    print("Total Wins: ", win_history.count("1"), " - ", "{0:,.2f}".format(100.0 * win_history.count("1") / nb_hands), "%")
    print("Win - Player Blackjack: ", game_stats.count("2"))
    print("Win - Regular (No Bust/BJ): ", game_stats.count("1"))
    print("Win - Dealer Busted: ", game_stats.count("5"))
    print("")
    print("Total Pushes: ", (game_stats.count("4") + game_stats.count("6")), " - ", "{0:,.2f}".format(100.0 * (game_stats.count("4") + game_stats.count("6")) / nb_hands), "%")
    print("Push - Dealer & Player Blackjack: ", game_stats.count("4"))
    print("Push - Non BJ: ", game_stats.count("6"))
    print("")
    print("Total Losses: ", win_history.count("0"), " - ", "{0:,.2f}".format(100.0 * win_history.count("0") / nb_hands), "%")
    print("Lost - Dealer Blackjack: ", game_stats.count("3"))
    print("Lost - Regular (No Bust/BJ): ", game_stats.count("7"))
    print("Lost - Player Busted: ", game_stats.count("0"))
    print("Lost - Surrender: ", game_stats.count("8"))
    print("")
    print("Error: ", game_stats.count("9"))
    print("")
       
    edge = (win / bet) #Total Money/Total Bets -- sume=moneys and total_bet=bets
    print("Edge = {}% (Moneys/Bets)".format("{0:,.2f}".format(100.0 * edge)))
    print("Bets = {}".format("{0:,.3f}".format(bet)))
    hands_per_hour = 50
    hourly_winnings = game.stake * hands_per_hour * edge
    print("Hourly win/loss rate: ${} \n(Assumes: ${} Bet, {}% Edge, and {} hands/hour)".format("{0:,.2f}".format(hourly_winnings), "{0:,.2f}".format(game.stake), "{0:,.3f}".format(100*edge), "{0:,.0f}".format(hands_per_hour)))
    print("Max Bankroll: ${}".format("{0:,.2f}".format(max(bankroll))))
    print("Min Bankroll: ${}".format("{0:,.2f}".format(min(bankroll))))
    print("End Bankroll: ${}".format("{0:,.2f}".format(bankroll[-1])))
    print("Overall winnings (Moneys): ${}".format("{0:,.2f}".format(win)))
     
    
    '''
    Expected Value = Winning Odds - Losing Odds
    
    '''
    
    print("")
    print("Max Loss Run:", longest_seq(win_history, "0"))
    print("Max Win Run:", longest_seq(win_history, "1"))

    print("")
    finish_time = time.time() - start_time
    if finish_time < 1: finish_time = 1
    print('Execution time: %.2fs at %s Hands per second' % (finish_time, "{:,.2f}".format(nb_hands / finish_time)))
        
    #PRINT CHARTS
    moneys_sorted = sorted(moneys)
    fit = stats.norm.pdf(moneys_sorted, np.mean(moneys_sorted), np.std(moneys_sorted))
    plt.xlabel('dist. of each game winnings')
    plt.plot(moneys_sorted, fit, '-o')
    plt.hist(moneys_sorted, normed=True)
    plt.show()
    
    #HISTORICAL TRUE COUNT
    plt.ylabel('count')
    plt.xlabel('history (per card - approx 5.5 cards per round)')
    plt.plot(countings, label='True Count')
    plt.legend(loc='center left')
    plt.show()

    #STANDARD BANKOLL
    x = np.arange(nb_hands)
    plt.plot(bankroll)
    plt.plot(x, Expected_Value * x)
    Expected_Value_Text = ("Expected Value (%s)" % Expected_Value)
    Actual_Value_Text = ("Actual Value (%s)" % format("{0:,.2f}".format(100 * edge)))
    if edge < 0: plt.legend([Actual_Value_Text, Expected_Value_Text], loc='upper right')
    else: plt.legend([Actual_Value_Text, Expected_Value_Text], loc='lower left')
    plt.ylabel('Bankroll')
    plt.xlabel('Hands')
    plt.show()

    #STANDARD DIVIED BY n LINES, WITH AVERAGE
    #create numpy array
    bankroll_array = np.array(bankroll)
    #limit to just first million
    bankroll_array = bankroll_array[:NUM_HANDS]    # Will hold only first 10 nums
    #split numpy array 
    graph_lines = 5
    bankroll_array = np.array_split(bankroll_array, graph_lines)
    #plot actual valutes
    for z in range (0,graph_lines):
        #set to zero
        set_to_zero = bankroll_array[z][0] * -1
        bankroll_array[z] += set_to_zero
        #plot all the actual lines
        plt.plot(bankroll_array[z]) #, label=z)
    #plot actual value MEAN
    mean_foo = np.array(np.mean(bankroll_array, axis=0))
    mean_foo_Text = ("Mean Value (%s)" % format("{0:,.2f}".format(mean_foo[-1]/(NUM_HANDS/graph_lines))))
    plt.plot(mean_foo, label=mean_foo_Text,linewidth=5.0)
    #plot expected values
    nb_hands_div = nb_hands/graph_lines
    x = np.arange(nb_hands_div)
    Expected_Value_Text = ("Expected Value (%s)" % Expected_Value)
    plt.plot(x, Expected_Value * x, label=Expected_Value_Text,linewidth=5.0)
    plt.legend(loc='lower left', fancybox=True, framealpha=0.5)
    plt.ylabel('Bankroll')
    plt.xlabel('Hands')
    plt.title('Historical Bankroll with Mean and Expected')
    plt.show()


    #print(StrategyImporter.soft_strategy)
          
'''
NOTES: 


POSSIBLE BETTING STRATEGY
COUNT - BET 
-2      1x  $0
-1      1x  $25
0       1x  $50
1       1x  $100
2       2x  $100
3       2x  $150
4       2x  $200
 
    
Typical EV
Blackjack	Basic Strategy	0.50%
Blackjack	Average player	2.00%
Blackjack	Poor Player	4.00%
###############################
Sites for odds/probability info

http://www.bettingresource.com/expected-value.html
https://www.gamblingsites.org/casino/blackjack/odds-and-probability/
##############################


http://www.blackjackforumonline.com/content/Calculating_the_House_Edge_for_Any_Blackjack_Rules_Set.htm


'''

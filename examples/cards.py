from __future__ import division
from pysimu import Model

"""
We wish to compute the probability that at least two of four players
receive at least two face cards if each player is dealt seven cards
from a standard 52-card deck.

"""

model = Model("queue", debug=True)

def two_face(hand):
    return len([card for card in hand if card % 13 >= 10]) >= 2

def check_hands(model, rand):
    deck = list(xrange(0, 52))

    # Shuffle the first 4 hands of 7 cards
    for n in xrange(0, 28):
        ndx = int(rand.random() * 52)
        deck[n], deck[ndx] = deck[ndx], deck[n]

    hands = [deck[0:7], deck[7:14], deck[14:21], deck[21:28]]
    return len([True for hand in hands if two_face(hand)]) >= 2

def process_result(model, result):
    if result:
        model.successes += 1

model.trial = check_hands
model.process_result = process_result
model.ntrials = 100
model.successes = 0
model.simulate()

print model.successes / model.ntrials

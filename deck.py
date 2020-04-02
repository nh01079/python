#deck.py
import random

class Deck:
    # managing a deck of cards
    def __init__(self, shuffle = True):
        """Creates a 52 deck with shuffling (default = True).
        Shuffling is prohibited when a card game has started"""
        self.deck=[]
        self.__createDeck()
        self.Pointer = 0
        if shuffle:
            self.shuffleDeck()

    def __createDeck(self):
        "create the original deck"
        for c in range(52):
            # diamonds -> clubs -> hearts -> spades
            suit = c//13 + 1
            rank = c%13 + 1
            c= Card((rank,suit))
            self.deck.append(c)

    def shuffleDeck(self):
        "shuffle the deck"
        random.shuffle(self.deck)

    def getCard(self):
        self.Pointer += 1
        try:
            return self.deck[self.Pointer - 1]
        except IndexError:
            self.Pointer = 1
            self.shuffleDeck()
            return self.deck[self.Pointer - 1]



    def compareCards(self,c1,c2):
        """compare the value of two cards, True if c1 > c2.
        Require sepecific compareCards method for different games"""
        return c1.value > c2.value


class Card:
    # object of a single card
    def __init__(self, value):
        # (1-13,1-4) referring to Ace to Jack and suits (diamonds, clubs, hearts, spades)
        self.value = value
        self.label = self.__creatLabel()

    def __creatLabel(self):
        cardDict = {1:'Ace', 2:'Two', 3:'Three', 4:'Four', 5:'Five', 6:'Six',
                    7:'Seven', 8:'Eight', 9:'Nine', 10:'Ten', 11:'Jack', 12:'Queen', 13:'King'}
        suitDict = {1:'Diamonds', 2:'Clubs', 3:'Hearts', 4:'Spades'}
        label = '{0} of {1}'.format(cardDict[self.value[0]], suitDict[self.value[1]])
        return label

    def __str__(self):
        return self.label

def main():
    test_deck = Deck(False)
    len(test_deck.deck)
    c1 = test_deck.getCard()
    c2 = test_deck.getCard()
    flag = test_deck.compareCards(c1,c2)
    while True:
        c1 = test_deck.getCard()
    pass

if __name__ == '__main__':
    main()
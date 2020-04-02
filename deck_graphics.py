#deck_graphics.py
#   display two cards one hidden and another shown. Guess whether the card is bigger
#   or smaller than the hidden card

from graphics import *
from button import Button
from deck import Deck

class Deck_graphics:

    def __init__(self):
        "initialize the game of cards"
        win = GraphWin("Guess the card", 400,400)
        win.setCoords(0,0,6,6)
        self.win = win
        # Button objects
        self.b = []
        self.cObj = []
        # card graphics objects len == 3 cRec[2] = hidden Rect
        self.cRec = []
        # interact with Deck class
        self.gameDeck = Deck(shuffle=True)
        self.__getCards()
        self.__drawLayout()
        self.__drawCards()
        self.__drawButtons()

    def __drawLayout(self):
        "Draw the general layout"
        message = Text(Point(3,5.5),"Card Game")
        message.draw(self.win)
        self.message = message
        outerRect = Rectangle(Point(0.25,0.25),Point(5.75, 5.25))
        outerRect.setFill('lightgray')
        outerRect.draw(self.win)
        pass

    def __drawCards(self):
        "draw the location of cards, computer's card is hidden"
        coords = [(.5,1.5),(3.5,1.5)]
        for n in range(2):
            x,y = coords[n]
            Rec = Rectangle(Point(x,y),Point(x+2,y+3))
            Rec.setFill('black')
            Rec.draw(self.win)
            self.cRec.append(Rec)
            # draw the card value
            card = self.cObj[n]
            cardName = Text(Point(x+1,y+1.5),str(card))
            cardName.setSize(12)
            cardName.setTextColor('white')
            cardName.draw(self.win)
            self.cRec.append(cardName)
        # draw the hidden one
        Rec = Rec = Rectangle(Point(.5,1.5),Point(2.5,4.5))
        Rec.setFill('green')
        Rec.draw(self.win)
        self.cRec.append(Rec)

    def __drawCardsRevealed(self):
        "Reveal all cards, undraw the hidden rectangle object"
        self.cRec[4].undraw()

    def __drawButtons(self):
        "draw the button to recieve user input"
        coords = [(1.5,.5,'Play'),(4.5,.5,'Quit')]
        for x,y,label in coords:
            b = Button(self.win,Point(x,y),
                       .85,.5,label)
            b.activate()
            self.b.append(b)

    def __cardsCleanUp(self):
        "Clean up old resources"
        self.cObj = []
        for object in self.cRec[:4]:
            object.undraw()
        self.cRec = []

    def __getCards(self):
        "get two cards for the round"
        for n in range(2):
            self.cObj.append(self.gameDeck.getCard())

    def __buttonClicked(self):
        while True:
            p = self.win.getMouse()
            for button in self.b:
                if button.clicked(p):
                    return button.getLabel()
            # close the graphics
            self.win.close()

    def __winLose(self, key):
        '''Toggle between play and again? to indicate the start of a new round. Compares the values of the two cards
        and determine the result of the round'''
        if key == 'Play':
            # reveal hidden card
            self.__drawCardsRevealed()

            # win condition and set self.message text to win/lose
            c1, c2 = self.cObj
            result = self.gameDeck.compareCards(c2,c1)
            if result:
                # player has the bigger cards, i.e. c2 > c1
                self.message.setText('You Win!')
            else:
                self.message.setText('You Lose!')

            # set self.b[0] text to Again? to prompt for user input
            self.b[0].updateLabel('Again?')

        elif key == 'Again?':
            # clean up old resources
            self.__cardsCleanUp()
            # give out new cards (1 visible, 1 hidden), setbutton text = 'Play'
            self.__getCards()
            # draw one hidden one revealed
            self.__drawCards()
            # set self.b[0] text to Play to prompt for user input
            self.b[0].updateLabel('Play')

    def run(self):
        while True:
            key = self.__buttonClicked()
            if key == 'Quit':
                break
            self.__winLose(key)
        self.win.close()

def main():
    demo = Deck_graphics()
    demo.run()

if __name__ == '__main__':
    main()
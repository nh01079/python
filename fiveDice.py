#fiveDice.py
# shows five dices
# set coordinates such that each square is a 3x3 matrix
# draw five squares depicting the five dices
# add circle dot to depict a straight 1, 2, 3, 4, 5
from graphics import *

def main():
    print ("five dices")
    win = GraphWin("five dices", 1000, 500)
    win.setCoords(0, -7.5, 30, 7.5)
    #initialize first square
    shape = Rectangle(Point(0, 0), Point(2, 2))
    shape.move(4,0)
    #shape.draw(win)

    for i in range (1,6):
        #### drawing remaining 5 squares
        # Draw rectangle background
        shape1 = shape.clone()
        shape1.setFill('white')
        shape1.draw(win)
        #move to next position
        shape.move(5,0)
        # draw the dots on the dice
        c_center = shape1.getCenter()
        c = Circle(c_center, 0.2)
        c.setFill('red')
        # draw dots depending on number
        if i == 1 :
            #c = Circle(c_center, 0.3)
            #c.setFill('red')
            c.draw(win)
        if i == 3 or i == 5:
            # create a new circle instead of using c
            c0= c.clone()
            c0.draw(win)
        if i == 2 or i == 3:
            c.move(0, 0.5)
            c1 = c.clone()
            c1.draw(win)
            c.move(0, -1)
            c2 = c.clone()
            c2.draw(win)
        if i == 4 or i == 5:
            c.move(-0.5, 0.5)
            c1 = c.clone()
            c1.draw(win)
            c.move(0, -1)
            c2 = c.clone()
            c2.draw(win)
            c.move(1, 0)
            c3 = c.clone()
            c3.draw(win)
            c.move(0, 1)
            c4 = c.clone()
            c4.draw(win)



    # wait for mouse click to exit
    win.getMouse()
    win.close()

main()

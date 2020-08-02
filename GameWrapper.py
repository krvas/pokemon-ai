# events-example0.py taken from 112 website

from tkinter import *
import battleSim
import UI

####################################
# customize these functions
####################################

def init(data):
    # load data.xyz as appropriate
    data.callBattleSimulator = False
    UI.init(data)
    battleSim.init(data)

def initAfterCanvasCreated(data):
    UI.initAfterCanvasCreated(data)
    battleSim.initAfterCanvasCreated(data)

def mousePressed(event, data):
    # use event.x and event.y
    if data.callBattleSimulator:
        battleSim.mousePressed(event, data)
    else:
        UI.mousePressed(event, data)
    
def mouseReleased(event, data):
    if not data.callBattleSimulator:
        UI.mouseReleased(event, data)

def keyPressed(event, data):
    # use event.char and event.keysym
    if data.callBattleSimulator:
        battleSim.keyPressed(event, data)
    else:
        UI.keyPressed(event, data)

def timerFired(data):
    if data.callBattleSimulator:
        battleSim.timerFired(data)
    else:
        UI.timerFired(data)

def redrawAll(canvas, data):
    # draw in canvas
    if data.callBattleSimulator:
        battleSim.redrawAll(canvas, data)
    else:
        UI.redrawAll(canvas, data)

####################################
# use the run function as-is
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)
        
    def mouseReleasedWrapper(event, canvas, data):
        mouseReleased(event, data)
        redrawAll(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    root.title('Pokemon 112')
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    initAfterCanvasCreated(data)
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<ButtonRelease-1>", lambda event:
                            mouseReleasedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

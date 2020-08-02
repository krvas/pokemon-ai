# barebones taken from 112 website

'''
To do:
evaluate sleep / paralysis

ice type moves in movesList
animations
critical hits

when toxic'd, evaluate setup moves less
switches more often
speed in eval swaps

Recommended sets
Movesets
recommended moves

how to use belly drum / shell smash / close combat and stuff / venoshock / hex
return change damage value
gyro ball flail


No effect
space / enter
Protect bug
'''

from tkinter import *

from dataFormat import *
from Evaluation import *
from TeamMaker import *

from PokemonClass import *
from TeamClass import *
from MoveClass import *

import requests
from PIL import Image, ImageTk
#from io import BytesIO

import math
import copy

####################################
# customize these functions
####################################

def test():
    class Struct(object):pass
    data = Struct()
    data.height, data.width = 400, 400
    data.timerDelay = 100
    init(data)
    return data


## Model
def init(data):
    # load data.xyz as appropriate
    data.whatToDoInputs = ["Fight", "Opponent", "Pokemon", "Run"]
    data.inputs = data.whatToDoInputs
    data.arrowPos = 0
    data.inputBox = (0, data.height*7/10, data.width, data.height)
    data.inputLocations = \
    [(data.width//4 - 100, data.inputBox[1]*2/3+data.height/3),\
     (3*data.width//4 - 100, data.inputBox[1]*2/3+data.height/3), \
     (data.width//4 - 100, data.inputBox[1]/3+data.height*2/3),\
     (3*data.width//4 - 100, data.inputBox[1]/3+data.height*2/3)]
    data.gameEnded = False
    resetChoice(data)
    data.lastCode = ['Use the arrow keys and the enter button to move around!']
    data.priorityCounter = []
    data.priorityPointer = 0
    data.choiceState = False
    data.battleState = True
    data.winner = None
    setTeams(data)
    data.vibrate = 0
    
def initAfterCanvasCreated(data):
    loadBackground(data)
    
    
def loadBackground(data):
    filename = "images/scene.jpg"
    img = Image.open(filename)
    img = img.resize((int(data.width), int(data.inputBox[1])), Image.ANTIALIAS)
    data.HH = ImageTk.PhotoImage(img)
    
    
def setTeams(data):
    allMoves = getMovesFromEssentialsDB()
    
    dragonite = Pokemon(149)
    dragonite.setMoves([allMoves['DRAGONCLAW'], allMoves['DRAGONDANCE'], 
    allMoves['EXTREMESPEED'], allMoves['DRACOMETEOR']])
    
    zapdos = Pokemon(145)
    zapdos.setMoves([allMoves['THUNDERBOLT'], allMoves['CALMMIND'], \
    allMoves['HEATWAVE']])
    
    bisharp = Pokemon('bisharp')
    bisharp.setMoves([allMoves['IRONHEAD'], allMoves['SWORDSDANCE'], allMoves['AQUAJET']])
    
    clefable = Pokemon('clefable')
    clefable.setMoves([allMoves['FLAMETHROWER'], allMoves['SOFTBOILED'], \
    allMoves['PSYCHIC']])
    
    gengar = Pokemon(94)
    gengar.setMoves([allMoves['SHADOWBALL'], allMoves['TOXIC'], \
    allMoves['THUNDERBOLT'], allMoves['SING']])
    
    garchomp = Pokemon(445)
    garchomp.setMoves([allMoves['EARTHQUAKE'], allMoves['DRAGONCLAW'], \
    allMoves['SWORDSDANCE'], allMoves['FLAMECHARGE']])
    
    blissey = Pokemon('blissey')
    blissey.setMoves([allMoves['SOFTBOILED'], allMoves['TOXIC'], allMoves['SEISMICTOSS'], allMoves['PROTECT']])
    
    volcarona = Pokemon('volcarona')
    volcarona.setMoves([allMoves['ENDEAVOR'], allMoves['BUGBUZZ'], \
    allMoves['FIERYDANCE']])
    volcarona.currentHP = 100
    
    #data.playerTeam = Team([dragonite, gengar, zapdos])
    data.compTeam = readTeam('In_built_%d' % random.randint(1, 4), data.allPokemon, data.allMoves)
    #data.compTeam = Team([volcarona,garchomp, blissey, gengar.copy()])

## Control
def mousePressed(event, data):
    # use event.x and event.y
    pass

def keyPressed(event, data):
    # use event.char and event.keysym
    if event.char == 'r':
        init(data)
        data.callBattleSimulator = False
        data.thisScreen = 1
    if data.gameEnded:
        return
    if data.battleState and len(data.lastCode) > 0:
            data.lastCode.pop(0)
            if len(data.lastCode) > 0 and \
            data.lastCode[0].startswith(str(data.compTeam.currentPokemon)):
                data.playerTeam.currentPokemon.animationCounter = 0
            
    elif event.keysym == "Down":
        data.arrowPos += 2
        data.arrowPos %= 4 if data.choiceState else 6
    elif event.keysym == "Up":
        data.arrowPos -= 2
        data.arrowPos %= 4 if data.choiceState else 6
    elif event.keysym in ["Left", "Right"]:
        data.arrowPos = 2*(data.arrowPos//2) + ((data.arrowPos%2) + 1)%2
    elif event.keysym == "Return":
        execute(data)
    elif event.keysym == "BackSpace" and not data.battleState:
        lastState(data)
        
def lastState(data):
    if data.faintState:
        return
    else:
        resetChoice(data)

# gets called whenever enter is pressed
def execute(data):
    if data.swapState or data.faintState:
        swapPokemon(data)
    elif data.inputs == data.whatToDoInputs and data.choiceState:
        if data.arrowPos == 0:
            pickMoveState(data)
        elif data.arrowPos == 1:
            data.choiceState = False
            data.opponentState = True
            data.arrowPos = 0
        elif data.arrowPos == 2:
            data.arrowPos = 0
            data.swapState = True
            data.choiceState = False
        elif data.arrowPos == 3:
            init(data)
            data.callBattleSimulator = False
    elif data.inputs == data.playerTeam.currentPokemon.moves and \
    data.choiceState and data.arrowPos < len(data.inputs):
        data.playerMove = ('pAttack', data.arrowPos,\
        data.playerTeam.currentPokemon.moves[data.arrowPos].priority)
        playTurn(data)
        data.battleState = True
        data.choiceState = False
    
def swapPokemon(data):
    if data.arrowPos >= data.playerTeam.len() or \
     data.playerTeam[data.arrowPos].hasFainted() or \
     data.playerTeam[data.arrowPos] == data.playerTeam.currentPokemon:
         return
    data.playerMove = ('pSwap', data.arrowPos, 6)
    if data.swapState:
        playTurn(data)
        data.swapState = False
        data.battleState = True
    elif data.faintState:
        data.priorityCounter = [['pSwap', data.arrowPos], ['afterTurn', 1]]
        data.priorityPointer = 0
        data.faintState = False
        data.battleState = True
    
# runs a turn
# takes everything to be done, and adds it to a list of instructions
# the instructions are in order
def playTurn(data):
    playerPkmn = data.playerTeam.currentPokemon
    compPkmn = data.compTeam.currentPokemon
    compAttack = chooseMove(data.compTeam, data.playerTeam)
    
    priorityCounter = []
    for i in range(17):priorityCounter.append([])
    
    # makes sure the player and comp attacks are both added to the counter
    # in the correct order
    appended = False
    if playerPkmn.netSpeed() > compPkmn.netSpeed():
        priorityCounter[data.playerMove[2]+8].append(data.playerMove)
        appended = True
        
    elif playerPkmn.netSpeed() == compPkmn.netSpeed() \
    and random.randint(0,1) == 1:
        priorityCounter[data.playerMove[2]+8].append(data.playerMove)
        appended = True
        # speed tie
    
    if compAttack[0] == 'cAttack':
        priorityCounter[compPkmn[compAttack[1]].priority+8].append(compAttack)
    elif compAttack[0] == 'cSwap':
        priorityCounter[6+8].append(compAttack)
    
    if not appended:
        priorityCounter[data.playerMove[2]+8].append(data.playerMove)

    data.priorityCounter = flatten(priorityCounter[::-1])+\
    [['afterTurn', 0]]

def afterTurn(data, code):
    #resetChoice(data)
    if code == 0:
        handleBattleStatus(data)
        return
        
    if data.playerTeam.isUnusable():
        data.gameEnded = True
        data.choiceState = False
        data.winner = 'computer'
        return
    elif data.compTeam.isUnusable():
        data.gameEnded = True
        data.choiceState = False
        data.winner = 'player'
        return
    
    if data.playerTeam.currentPokemon.hasFainted():
        data.faintState = True
        data.choiceState = False
        data.battleState = False
        data.arrowPos = 0
        data.playerTeam.currentPokemon.removeBoosts()
    if data.compTeam.currentPokemon.hasFainted():
        data.compTeam.currentPokemon.removeBoosts()
        data.compTeam.currentPokemon = chooseNewCurrentPokemon(data)

def handleBattleStatus(data):
    statusMessage = []
    playerPkmn = data.playerTeam.currentPokemon
    compPkmn = data.compTeam.currentPokemon
    if not playerPkmn.hasFainted():
        statusMessage += [playerPkmn.handleStatusAfterTurn()]
        if playerPkmn.hasFainted():
            statusMessage += ['Your %s fainted' % playerPkmn]
    if not compPkmn.hasFainted():
        statusMessage += [compPkmn.handleStatusAfterTurn()]
        if compPkmn.hasFainted():
            statusMessage += ['Foe %s fainted' % compPkmn]
            
    statusMessage = [elt for elt in statusMessage if elt != None]
    data.lastCode += statusMessage
    
    data.playerTeam.currentPokemon.protected = False
    data.compTeam.currentPokemon.protected = False
    
    data.priorityCounter += [['afterTurn', 1]]
        
def flatten(L):
    # base case
    if not containsList(L):
        return L
    # recursive case:
    # I remove the outermost lists
    # and recurse to remove the inner ones
    else:
        newL = []
        for element in L:
            if isinstance(element, list):
                newL += element
            else:
                newL.append(element)
        return flatten(newL)
    
# first makes sure L is a list, and if it is, sees whether it contains a list
def containsList(L):
    if not isinstance(L, list):
        return False
    for element in L:
        if isinstance(element, list):
            return True
    return False
    
# technically not a state
def pickMoveState(data):
    data.inputs = data.playerTeam.currentPokemon.moves
    


# returns a line of battle code which describes what the comp should do
def chooseMove(team1, team2):
    pkmn1 = team1.currentPokemon
    pkmn2 = team2.currentPokemon
    
    swapCase = bestToSwapIn(team1, team2)
    # if evaluate returns lower than this, swap
    
    values = [[evaluate(team1, team2, i), i] for i in range(len(pkmn1.moves))]
    values.sort()
    bestMove = values[-1]
    showData(team1, values, swapCase)
    if bestMove[0] < swapCase[0]:
        return ('cSwap', swapCase[1])
    else:
        return ('cAttack', bestMove[1])
        
# a helper function made solely for debugging
# prints all the computer value information
def showData(team, moves, swaps):
    moveData = ['%s - %.2f' % (team.currentPokemon[move[1]], move[0]) \
    for move in moves]
    swapData = '%s - %.2f' % (team[int(swaps[1])], swaps[0])
    print(str(team.currentPokemon)+'\n'+'\n'.join(moveData)+'\n'+swapData+'\n')

# returns the obvious move for pkmn1 to play against pkmn2
def obviousMove(pkmn1, pkmn2):
    
    cutoff = 4
    # cutoff - how far does the 'best' move need to be, to be obvious?
    values = [(evaluate(pkmn1, pkmn2, i), i) for i in range(len(pkmn1.moves))]
    values.sort()
    
    if len(values) == 1:
        return 0
    elif values[-1][0] > values[-2][0]*cutoff:
        return values[-1][1]
    else:
        return None
    
 
# picks moves with the highest matchup
# if two moves have equal matchups, picks randomly
# pkmn1 attacks pkmn2
def bestDamagingMoveAgainst(pkmn1, pkmn2):
    damage = []
    for i in range(len(pkmn1.moves)):
        damage.append((pkmn1.damageDone(pkmn2, i), i))
    damage.sort()
    return damage[-1][1]
    
def chooseNewCurrentPokemon(data):
    swapIn = bestToSwapIn(data.compTeam, data.playerTeam)[1]
    pokemon = data.compTeam[swapIn]
    data.lastCode += ['Foe sent out %s' % pokemon]
    return pokemon

# executes one piece of code at a time
# depending on what's on the priority counter
def timerFired(data):
    data.vibrate += .5
    if data.battleState and data.lastCode == []:
        if data.priorityPointer >= len(data.priorityCounter):
            resetChoice(data)
        else:
            elt = data.priorityCounter[data.priorityPointer]
            runCode(data, elt)
    if data.battleState and data.playerTeam.currentPokemon.animationCounter>0:
        #data.playerTeam.currentPokemon.animationCounter += 1
        pass
        
# So, playing a pokemon game is kind of like running a bunch of instructions
# this just takes in one instruction and runs it
# it also edits data.lastCode, which is a message that is displayed
def runCode(data, elt):
    playerPkmn = data.playerTeam.currentPokemon
    compPkmn = data.compTeam.currentPokemon
    
    if elt[0] == 'pAttack':
        attack(data, data.playerTeam, data.compTeam, elt[1])
            
    elif elt[0] == 'cAttack':
        attack(data, data.compTeam, data.playerTeam, elt[1])
            
    elif elt[0] == 'pSwap':
        data.playerTeam.switchPokemon(elt[1])
        data.lastCode += ['You sent out %s'%data.playerTeam.currentPokemon]
    
    elif elt[0] == 'cSwap':
        data.compTeam.switchPokemon(elt[1])
        data.lastCode += ['Foe sent out '+data.compTeam.currentPokemon.name]
        
    data.priorityPointer += 1
    
    if elt[0] == 'afterTurn':
        afterTurn(data, elt[1])
    
        
def attack(data, userTeam, oppoTeam, move):
    user = userTeam.currentPokemon
    opponent = oppoTeam.currentPokemon
    
    if not user.hasFainted():
        status = user.handleStatusDuringTurn()
        if status[1]:
            data.lastCode += status[1]
        if not status[0]:
            return
    
    if opponent.protected and 'b' in user[move].flags:
        data.lastCode += ["%s protected itself against %s's %s" %\
        (opponent, user, user.moves[move])]
        return
    
    effect = user.useMove(userTeam, oppoTeam, move)
    user.animationCounter = 1
    if not user.hasFainted():
        data.lastCode += [user.name+' used '+str(user.moves[move])]
    if opponent.hasFainted():
        data.lastCode += [opponent.name+' fainted']
    elif effect:
        data.lastCode += effect # change later
            
def resetChoice(data):
    data.battleState = False
    data.swapState = False
    data.choiceState = True
    data.faintState = False
    data.opponentState = False
    data.inputs = data.whatToDoInputs
    data.arrowPos = 0
    data.priorityPointer = 0
    data.lastCode = []

## View
def redrawAll(canvas, data):
    
    if data.gameEnded:
        drawGameEndState(canvas, data)
        return
    if data.choiceState or data.battleState:
        drawGameBackground(canvas, data)
        drawOpponent(canvas, data)
        drawPlayer(canvas, data)
        drawCurrentHPBars(canvas, data)
        
    if data.choiceState:
        drawInputBox(canvas, data)
        drawArrow(canvas, data)
    elif data.swapState or data.faintState:
        data.playerTeam.drawSummary(canvas, data)
    elif data.battleState:
        drawBattleBox(canvas, data)
    elif data.opponentState:
        data.compTeam.drawSummary(canvas, data)
        
def drawGameBackground(canvas, data):
    canvas.create_image(0, 0, anchor=NW, image = data.HH)
        
def drawCurrentHPBars(canvas, data):
    barWidth = 16
    barLength = 200
    x1 = data.width*(.05)
    y1 = data.height*(.4)
    x2 = x1 + barLength
    y2 = y1 + barWidth
    data.playerTeam.currentPokemon.drawHPBar(canvas, x1, y1, x2, y2)
    
    x1 = data.width*(.5)
    y1 = data.height*(.05)
    x2 = x1 + barLength
    y2 = y1 + barWidth
    data.compTeam.currentPokemon.drawHPBar(canvas, x1, y1, x2, y2)
        
def drawGameEndState(canvas, data):
    offset = 20
    canvas.create_image(data.width//2, data.height//2, image=data.bgNoText)
    canvas.create_rectangle(data.width*.1, data.height*.05, data.width*.9,\
    data.height*.95, fill=rgbString((200, 225, 225)), outline='grey')
    canvas.create_text(data.width/2, data.height/2 - offset, text="Game Over!")
    canvas.create_text(data.width/2, data.height/2 + offset, text="Press 'r' to return")
    
    if data.winner == 'computer':
        winTeam = data.compTeam
    elif data.winner == 'player':
        winTeam = data.playerTeam
        
    if data.winner != None:
        canvas.create_text(data.width/2, data.height/2, \
        text="Winner - "+data.winner)
        
        center = [data.width//2, data.height//2]
        points = getPointsOnCircle(center, data.height//3, winTeam.len())
        
        for i in range(winTeam.len()):
            canvas.create_image(points[i], \
            image=data.frontImage[winTeam.pokemon[i].id])
    
    
# takes in c, r and finds the points on the circle
# basically to create a regular polygon
def getPointsOnCircle(center, radius, numPoints):
    points = []
    for i in range(numPoints):
        theta = math.pi/2 - 2*math.pi*i/numPoints
        point = [center[0]+radius*math.cos(theta), \
        center[1]-radius*math.sin(theta)]
        points.append(point)
    return points
    
# these next two functions draw images, which are loaded in init()
# requires BytesIO from io, PIL, requests
def drawOpponent(canvas, data):
    id = data.compTeam.currentPokemon.id
    canvas.create_image(data.width-225+\
    10*math.cos(data.compTeam.currentPokemon.animationCounter), 100,\
     image=data.frontImage[id])

def drawPlayer(canvas, data):
    id = data.playerTeam.currentPokemon.id
    canvas.create_image(100 +\
     10*math.sin(data.playerTeam.currentPokemon.animationCounter), data.inputBox[1], image=data.backImage[id], 
    anchor=S)
    

        
def drawInputBox(canvas, data):
    canvas.create_rectangle(data.inputBox, width=10)
    for i in range(len(data.inputs)):
        #arrow = '→' if i == data.arrowPos%len(data.inputs) else ''
        canvas.create_text(data.inputLocations[i], anchor='w',\
        text=str(data.inputs[i]), font = "Baumans %d" % (data.width//20))
        
def drawBattleBox(canvas, data):
    canvas.create_rectangle(data.inputBox, width=10)
    lineLength = 40
    
    try: 
        message = data.lastCode[0]
        messages = wrap(message, lineLength)
        gap = (data.height - data.inputBox[1])//(len(messages)+1)
        height = data.inputBox[1] + gap
        
        for msg in messages:
            canvas.create_text(50, height, anchor='w', \
            text=msg, font="Baumans %d" % (data.width//25))
            height += gap
            
            
    except IndexError: pass
    
# takes a message and wraps the words, according to how long the line should be
def wrap(message, lineLength):
    parts = message.split(' ')
    lines = []
    line = ''
    while len(parts) > 0:
        if len(line+parts[0]) > lineLength:
            lines += [line[1:]]
            line = ''
        else:
            line += ' '+parts.pop(0)
    return lines+[line[1:]]
    
        
def drawArrow(canvas, data):
    canvas.create_text(*data.inputLocations[data.arrowPos], text='→', \
    anchor='e', font="Baumans %d" % (data.width//20))
    
# converts rgb into hexadecimal
# taken from 112 website
def rgbString(rgb):
    return "#%02x%02x%02x" % (rgb[0], rgb[1], rgb[2])
    

## Run Function

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
    canvas = Canvas(root, width=data.width, height=data.height)
    data.entry = Entry(canvas)
    canvas.pack()
    initAfterCanvasCreated(data)
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

#run(750, 500)
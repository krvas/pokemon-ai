
from tkinter import *
from PIL import Image, ImageTk
import math
import os

from dataFormat import *
from TeamMaker import *
from PokemonClass import *
from TeamClass import *
from MoveClass import *
import battleSim
import learnsets

from EntryClass import *

'''
UI.py
This file contains the data for the user inputs / menu screen
This calls battleSim when the user asks


Most things in this file are handled by screen number
Key:
0 - Opening screen
1 - Main menu
2 - Team Builder
3 - Choose which team you want to edit
4 - Choose which team you want to battle with (similar to 3)
5 - Instructions / mechanics page

'''

def init(data):
    data.buttonsNeeded = [set(), \
    {'Battle Simulator', 'Team Builder', 'Load', 'Instructions'}, \
    {'Back', 'Save', 'Clear'}, {'Back', 'int'}, {'Back', 'int'}, {'Back'}]
    data.thisScreen = 0
    entrySize = (220, 28)
    '''
    data.entries = [MyEntry(*entrySize, (data.width//5, 100)), \
    MyEntry(*entrySize, (data.width//2, 50)), \
    MyEntry(*entrySize, (data.width//2, 80)), \
    MyEntry(*entrySize, (data.width//2, 110)), \
    MyEntry(*entrySize, (data.width//2, 140))]'''
    data.allMoves = getMovesFromEssentialsDB()
    data.allPokemon = getPokemonName('all')
    data.entries = [PokeData(data.width, 150, (data.width//2, 190+160*i), \
    data.allPokemon, data.allMoves) for i in range(6)]
    data.teamName = MyEntry(*entrySize, (3*data.width//7, 85), max=20, 
    blinkTime=600)
    
    data.screenDrawn = False
    data.timerCounter = 0
    data.dRender = -20
    data.screenRender = 0
    data.saveCounter = 0
    data.learnsets = learnsets.getLearnsetsDict()
    
    data.instructions = """\
    Controls (in game mode):
    - Use the arrow keys to move the cursor
    - Press enter to select an option
    - Press Backspace to go back
    - At any point, press 'r' to return to the home screen
    
    Controls (in home screen):
    - Press the buttons to navigate
    - Use the up/down arrow keys to scroll
    - Create a new team by pressing the 'Team Builder'
    - Edit your old teams by pressing 'Edit Teams'
    
    Mechanics:
    If you're new to Pokemon, check Bulbapedia for an 
    exhaustive list of mechanics.
    
    This is similar to Smogon University's battle simulator. 
    Except, you play an AI. The current version, does not 
    include all features of Pokemon.
    It contains all fully evolved pokemon from Gens I-V 
    
    It contains:
    Attacking moves
    Set-up moves
    Status moves
    Protect / detect
    Healing moves
    Aromatherapy / Heal Bell
    """

    
# load images after canvas made
def initAfterCanvasCreated(data):
    # pick random background with weight
    if random.uniform(0, 1) < .8:
        backgroundPicked = 0
    elif random.randint(0, 1) == 0:
        backgroundPicked = 1
    else:
        backgroundPicked = 2
    if backgroundPicked in {0, 1}:
        filename = 'images/wallpapers/%d.png' % backgroundPicked
    else:
        filename = 'images/wallpapers/%d.jpg' % backgroundPicked
    data.bgNoText = loadImage(filename, (data.width, data.height))
    data.buttons = {
    'Battle Simulator': MyButton(300, 80, [(255,255,255)], [(0,0,200)], \
                        'Battle Simulator', (data.width//4, data.height*.35)),
    'Team Builder': MyButton(300, 80, [(255,255,255)], [(0,0,200)], \
                        'Team Builder', (3*data.width//4, data.height*.35)),
    'Back': MyButton(75, 30, [(255,255,255)], [(128,128,128)], \
                        'Back', (60, 30)),
    'Save': MyButton(30, 30, [(255,255,255)], [(0,200,220)], \
                loadImage('images/floppy.png', (20, 20)), (data.width-40, 40)),
    'Load': MyButton(300, 80, [(255,255,255)], [(0,0,200)], \
                        'Edit Team', (3*data.width//4, data.height*.55)),
    'Instructions': MyButton(300, 80, [(255,255,255)], [(0,0,200)], \
                        'Instructions', (data.width//4, data.height*.55)),
    'Clear': MyButton(75, 30, [(255,255,255)], [(128,128,128)], \
                        'Clear', (140, 30))
    }
    loadTeamButtons(data)
    
    data.background = ImageTk.PhotoImage(\
    Image.open('images/wallpapers/OpeningScreen%d.png'% backgroundPicked))
    loadSprites(data)
    
def loadSprites(data):
    folder = 'images/sprites/'
    data.frontImage = {}
    for i in range(1, 650):
        try:
            data.frontImage[i] =\
             ImageTk.PhotoImage(Image.open(folder+str(i)+'.png'))
        except:
            pass
            # not all the pokemon are stored
    
def loadTeamButtons(data):
    
    teamButtons = {}
    teams = os.listdir('files/teams')
    teams = [team for team in teams if team.endswith('.txt')]
    
    height = data.height//4
    for i in range(len(teams)):
        teams[i] = teams[i][:-4] # remove '.txt'
        teamButtons[i] = MyButton(data.width*.4, data.width//25+10, 
        [(200,255,255)], [(100,100,100)], teams[i], \
        (data.width//4 if i%2 == 0 else 3*data.width//4, height))
        if i%2 == 1:
            height += data.width//25 + 20

    data.savedTeams = teams
    data.buttons.update(teamButtons)
    
    
def loadImage(filename, size=None):
    img = Image.open(filename)
    if filename.endswith('.png'):
        img = Image.composite(img, Image.new('RGB', img.size, 'white'), img)
    if size:
        img = img.resize(size, Image.ANTIALIAS)
    
    return ImageTk.PhotoImage(img)
    
# loads images after the team has been set
# loads the back for player images and front for comp
def loadBackImages(data):
    file = 'images/'
    data.sprites = {}
    
    data.backImage = loadImageHelper(data, data.playerTeam, \
     file+'sprites_back/')
    
     
    data.icons = loadImageHelper(data,\
     data.compTeam.pokemon+data.playerTeam.pokemon, file+'icons/', False)
    
# loads either front or back images, depending on the function
def loadImageHelper(data, team, folder, resize=True):
    sprites = {}
    result = {}
    for pokemon in team:
        id = pokemon.id
        img = Image.open(folder+str(id)+'.png')
        if resize:
            img = img.resize((120, 120), Image.ANTIALIAS)
        result[id] = ImageTk.PhotoImage(img)
    return result
    
def keyPressed(event, data):
    if data.thisScreen == 0:
        incrementScreen(data)

    elif data.thisScreen == 2:
        if event.keysym == 'Up' and data.entries[0].render < 0:
            for ent in data.entries:
                ent.updateRender(-data.dRender)
            data.teamName.updateRender(-data.dRender)
        elif event.keysym == 'Down' and data.entries[-1].getRect()[3] > data.height:
            for ent in data.entries:
                ent.updateRender(data.dRender)
            data.teamName.updateRender(data.dRender)
        else:
            data.teamName.takeInput(event)
            for i in range(len(data.entries)):
                e, kind = data.entries[i].onKeyPressed(event)
                data.entries[i].updateSuggestions(data.allPokemon,data.allMoves, \
                data.learnsets)
                if e != None:
                    entryGiven(e, kind, i, data)
    
    elif data.thisScreen in {5} and event.keysym in ['Down', 'Up']:
        data.screenRender +=\
        data.dRender if event.keysym == 'Down' else -data.dRender
        if data.screenRender > 0: data.screenRender = 0
        data.screenRender =max(data.screenRender,  \
        -35*len(data.instructions.splitlines())+data.height)
    elif data.thisScreen in {3, 4}:
        total = len(data.savedTeams)
        if total <= 14: return
        for i in range(total):
            data.buttons[i].onKeyPressed(event, data.dRender, -12*total)
        data.screenRender +=\
        data.dRender if event.keysym == 'Down' else -data.dRender
        if data.screenRender > 0: data.screenRender = 0
        data.screenRender =max(data.screenRender,  \
        -12*total)
    
        
# handles what happens when entries are given
def entryGiven(entry, kind, entryBox, data):
    return
    '''
    Input = entry.get()
    
    if isinstance(Input, Move) and kind == 'move':
        data.teamToEdit[entryBox].addMove(Input)
    elif isinstance(kind, Move):
        data.teamToEdit[entryBox].deleteMove(kind)
    elif isinstance(Input, str) and Input.upper() in data.allPokemon and \
    kind == 'pkmn':
        data.teamToEdit[entryBox] = Pokemon(Input)
    elif isinstance(Input, str) and Input.isdigit():
        EVs = int(Input)
        if isinstance(data.teamToEdit[entryBox], Pokemon):
            data.teamToEdit[entryBox].EV[kind] = EVs
    elif Input == '' and kind in allStats():
            data.teamToEdit[entryBox].EV[kind] = 0
    else: return
    data.teamToEdit.display()'''
        
    
    
def incrementScreen(data):
    data.thisScreen += 1
    data.screenDrawn = False
    
def setScreen(data, n):
    if data.thisScreen in {3,4,5} and n == 1:
        data.screenRender = 0
    data.thisScreen = n
    data.screenDrawn = False
    
def mousePressed(event, data):
    
    search = data.buttonsNeeded[2] if data.thisScreen==2 else data.buttons
    
    for key in search:
        if data.buttons[key].press(event) and \
        (key in data.buttonsNeeded[data.thisScreen] or \
        (isinstance(key, int) and 'int' in data.buttonsNeeded[data.thisScreen])):
            break
        
    
def buttonPressed(data, key):
    if key == 'Back' and data.thisScreen > 1:
        data.screenRender = 0
        if data.thisScreen in {3, 4}: resetButtons(data)
        setScreen(data, 1)
    elif key == 'Team Builder':
        setScreen(data, 2)
    elif key == 'Save':
        if data.teamName.get() != '':
            save(data.teamName.get(), data)
        else:
            data.errorMessage = "You didn't set a team name."
            # set screen to error screen
    elif key == 'Load':
        setScreen(data, 3)
    elif isinstance(key, int):
        clearAll(data)
        teamPicked(data, key)
    elif key == 'Battle Simulator':
        setScreen(data, 4)
    elif key == 'Instructions':
        setScreen(data, 5)
    elif key == 'Clear':
        clearAll(data)
            
def clearAll(data):
    data.teamName.delete()
    for entry in data.entries:
        for ent in entry.entries:
            ent.delete()
        
def resetButtons(data):
    total = len(data.savedTeams)
    for i in range(total):
        data.buttons[i].render = 0
    
# loads a team onto the display page
def loadTeam(data, team):
    
    for i in range(team.len()):
        pokemon = team[i]
        entry = data.entries[i]
        
        if pokemon == None: continue
        
        entry[0].message = pokemon.name
        
        for j in range(1, 5):
            if j-1 < len(pokemon.moves):
                entry[j].message = pokemon.moves[j-1]
                
        j=5
        for stat in allStats():
            if pokemon.EV[stat] != 0:
                entry[j].message = str(pokemon.EV[stat])
                j += 1
                
def teamPicked(data, index):
    team = readTeam(data.savedTeams[index], data.allPokemon, data.allMoves)
    if data.thisScreen == 3:
        data.teamName.message = data.savedTeams[index]
        loadTeam(data, team)
        setScreen(data, 2)
    elif data.thisScreen == 4:
        data.playerTeam = team
        data.callBattleSimulator = True
        loadBackImages(data)
        # calls battle simulator
        
# saves the given data to a file
def save(filename, data):
    thisTeam = Team([None])
    for entry in data.entries:
        
        if entry[0].get().upper() not in data.allPokemon:
            continue
        thisTeam.pokemon.append(Pokemon(entry[0].get()))
        
        for i in range(1, 5):
            if isinstance(entry[i].get(), Move):
                thisTeam[-1].addMove(entry[i].get())
                
        i=5
        for stat in allStats():
            if entry[i].get() != '' and entry[i].get().isdigit():
                thisTeam[-1].EV[stat] = int(entry[i].get())
            i += 1
    thisTeam.removeNone()
    if isLegalTeam(data, thisTeam):
        thisTeam.removeNone()
        writeTeam(filename, thisTeam)
        loadTeamButtons(data)
        data.saveCounter = 1500
        
# don't save a team if it's illegal
def isLegalTeam(data, team):
    if team.len() == 0: 
        print('team 0')
        return False
    for pokemon in team.pokemon:
        # check for EVs
        evSum = sum([pokemon.EV[key] for key in pokemon.EV])
        if evSum > 510:
            print('EVs over 510')
            return False
        for key in pokemon.EV:
            if pokemon.EV[key] > 252 or pokemon.EV[key] < 0:
                print('EV 252')
                return False
            
        # check for moves
        if len(pokemon.moves) == 0:
            print('%s has no moves' % pokemon)
            return False
        for move in pokemon.moves:
            if move.IntlName not in data.learnsets[str(pokemon).upper()]:
                print('moveset of %s' % pokemon)
                return False
    return True
    
def mouseReleased(event, data):
    if data.thisScreen == 2:
        for ent in data.entries:
            ent.onMouseReleased(event)
        data.teamName.checkSelected(event)
    
    search = data.buttonsNeeded[2] if data.thisScreen == 2 else data.buttons
    
    for key in search:
        if ((key in data.buttonsNeeded[data.thisScreen]) or \
        (isinstance(key, int) and 'int' in data.buttonsNeeded[data.thisScreen]))\
        and data.buttons[key].isActive():
            buttonPressed(data, key)
            break
    for key in search:
        data.buttons[key].unpress(event)
    
    
def timerFired(data):
    data.timerCounter += 1
    data.saveCounter = max(data.saveCounter - data.timerDelay, 0)
    for ent in data.entries:
        ent.onTimerFired(data.timerDelay)
    data.teamName.blink(data.timerCounter)
    
    
def redrawAll(canvas,data):
    if data.thisScreen == 0:
        drawOpeningScreen(canvas, data)
    elif data.thisScreen == 1:
        drawMainMenu(canvas, data)
    elif data.thisScreen == 2:
        drawEntries(canvas, data)
        drawTeamBuilder(canvas, data)
    elif data.thisScreen in {3, 4}:
        drawTeamOptions(canvas, data)
    elif data.thisScreen == 5:
        drawInstructions(canvas, data)
    
    drawButtons(canvas, data)
        
def drawOpeningScreen(canvas, data):
    canvas.create_image(data.width//2, data.height//2, image=data.background)
    color1 = (50, 50, 50)
    color2 = (200, 200, 200)
    color = [int(weightedAvg(color1[i], color2[i], \
    math.sin(data.timerCounter/20)**2, math.cos(data.timerCounter/20)**2)) \
    for i in range(3)]
    canvas.create_text(data.width//2, data.height//2 + 40, \
    text='Press any key to continue', font='Baumans %d' % (data.width//30), 
    fill=rgbString(color))
    
def drawButtons(canvas, data):
    for key in data.buttons:
        if key in data.buttonsNeeded[data.thisScreen] or \
        (isinstance(key, int) and 'int' in data.buttonsNeeded[data.thisScreen]):
            if key != 'Back':
                data.buttons[key].draw(canvas)
    if 'Back' in data.buttonsNeeded[data.thisScreen]:
        data.buttons['Back'].draw(canvas)
    # draw back button last
                
    
def drawMainMenu(canvas, data):
    canvas.create_image(data.width//2, data.height//2, image=data.bgNoText)
    canvas.create_text(data.width//2, 75, text='Main Menu', \
    font='Baumans %d underline' % (data.width//10), fill='white')
    
    
def drawTeamBuilder(canvas, data):
    canvas.create_image(data.width//2, data.height//2, image=data.bgNoText)
    canvas.create_text(data.width//2, 10+data.teamName.render, \
    text='Team Builder', font='Baumans %d underline' % (data.width//20),\
     anchor='n', fill='white')
    if data.saveCounter > 0:
        canvas.create_text(data.width-5, 70, text='Team Saved', anchor='e')
    
    for ent in data.entries[::-1]:
        ent.draw(canvas, data)
    
    canvas.create_text(data.teamName.x1,\
    (data.teamName.y1+data.teamName.y2)//2 + data.teamName.render,\
    anchor='e', text='Team Name: ', font = 'Baumans %d' % (data.width//30),\
    fill='white')
    
    data.teamName.draw(canvas)
    
def drawTeamOptions(canvas, data):
    canvas.create_image(data.width//2, data.height//2, image=data.bgNoText)
    canvas.create_text(data.width//2, 60+data.screenRender, \
    text='Pick Your Team', \
    font='Baumans %d underline' % (data.width//20), fill='white')
    
def drawTeamNames(canvas, data, startWidth, endWidth, teams):

    height = data.height//3+data.screenRender
    for team in teams:
        canvas.create_rectangle(startWidth, height-(data.width//50)-5, \
        endWidth, height+(data.width//50)+5, \
        fill=rgbString((100, 200, 200)), outline='grey')
        
        canvas.create_text((startWidth+endWidth)/2, height, text=team, \
        font='Baumans %d' % (data.width//30), fill='white')
        height += data.width//25 + 20
        
def drawInstructions(canvas, data):
    canvas.create_image(data.width//2, data.height//2, image=data.bgNoText)
    instructions = data.instructions
    
    canvas.create_rectangle(40, 55+data.screenRender, \
    data.width-40, 55+data.screenRender+32*len(instructions.splitlines()), 
    fill='white', outline='grey')
    canvas.create_text(data.width//2, 50+data.screenRender, text='Instructions',
    font='Baumans %d underline' % ((data.width+data.height)//40), fill='white', 
    anchor='s')
    canvas.create_text(45, 65+data.screenRender, text=instructions,
    font='Baumans %d' % ((data.width+data.height)//50), anchor='nw')
    
def drawEntries(canvas, data):
    for i in range(len(data.entries)):
        data.entries[i].draw(canvas, data)
    
    
def weightedAvg(value1, value2, weight1, weight2):
    return (value1*weight1 + value2*weight2) / (weight1+weight2)


## Run Function - edited to account for entries

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    
        data.screenDrawn = True
    
    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)
    
    def mouseReleasedWrapper(event, canvas, data):
        mouseReleased(event, data)
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
    data.timerDelay = 50 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    initAfterCanvasCreated(data)
    # set up events
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<ButtonRelease-1>", lambda event:
                            mouseReleasedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

#run(750, 500)

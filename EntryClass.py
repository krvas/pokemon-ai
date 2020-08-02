import string
from PIL import Image, ImageDraw
from dataFormat import *

# button object that can be pressed
class MyButton(object):
    
    def __init__(self, width, height, passiveColors, activeColors, msg, center):
        self.passiveColors = passiveColors
        self.activeColors = activeColors
        self.x1, self.y1 = center[0]-width//2, center[1]-height//2
        self.x2, self.y2 = center[0]+width//2, center[1]+height//2
        self.msg = msg
        self.active = False
        self.width = width
        self.height = height
        self.render = 0
        
    def __repr__(self):
        return str((str(self.msg), self.x1, self.x2, self.y1, self.y2))
    # check if pressed
    def press(self, event):
        y1 = self.y1 + self.render
        y2 = self.y2 + self.render
        self.active = event.x > self.x1 and event.x < self.x2 and \
            event.y < y2 and event.y > y1
        return self.active
        
    def onKeyPressed(self, event, dRender, minRender):
        if event.keysym == 'Up':
            self.render -= dRender
        elif event.keysym == 'Down':
            self.render += dRender
            
        if self.render > 0:
            self.render = 0
        elif self.render < minRender:
            self.render = minRender
        
    def unpress(self, event):
        self.active = False
        
    def isActive(self):
        return self.active
            
    def draw(self, canvas):
        y1 = self.y1 + self.render
        y2 = self.y2 + self.render
        canvas.create_rectangle(self.x1, y1, self.x2, y2,\
        fill=rgbString(self.activeColors[0] \
        if self.active else self.passiveColors[0]))
        if isinstance(self.msg, str):
            
            if (self.y2-self.y1)+(self.x2-self.x1) < 200:
                size = (self.x2-self.x1)//5
            elif (self.y2-self.y1)+(self.x2-self.x1) < 350:
                size = (self.x2-self.x1)//17
            else:
                size = (self.x2-self.x1)//8
            canvas.create_text((self.x1+self.x2)/2, (y1+y2)/2,\
            text=self.msg, font= "Baumans %d" % size, \
            fill="white" if self.active else "black")
        else:
            canvas.create_image((self.x1+self.x2)/2, (y1+y2)/2,\
            image=self.msg)
'''
make if you have time
class Slider(object):
    def __init__(self, valMax, valMin=0):
        self.max = valMax
        self.min = valMin
        self.value = valMin
'''
# a class that maintains the entry boxes
# I didn't use Tkinter's inbuilt entry class because it looks bad
class MyEntry(object):
    def __init__(self, width, height, center, \
    suggestions=None, max=16, blank='', blinkTime=400):
        self.width = width
        self.height = height
        self.blinkTime = blinkTime
        self.timer = 0
        self.line = True
        self.selected = False
        self.message = ''
        self.maxChar = max
        self.suggestions = suggestions
        self.blank = blank
        self.render = 0
        
        self.x1, self.y1 = center[0]-width//2, center[1]-height//2
        self.x2, self.y2 = center[0]+width//2, center[1]+height//2
    
    def draw(self, canvas):
        canvas.create_rectangle(self.x1, self.y1+self.render, \
        self.x2, self.y2+self.render,
        width=(3 if self.selected else 2),\
        outline='grey' if not self.selected else 'lightBlue', fill='white')
        
        display = '|' if self.line and self.selected and \
        len(str(self.message)) < self.maxChar else ''
        message = \
        self.blank if self.message == '' and not self.selected else self.message
        color = 'grey' if self.message == '' and not self.selected else 'black'
        
        canvas.create_text(self.x1+3, (self.y1+self.y2)//2+self.render,\
         anchor='w', \
        text=str(message)+display, fill=color)
        
    def blink(self, timerDelay): # call this on timerFired
        self.timer += timerDelay
        if self.timer > self.blinkTime:
            self.timer -= self.blinkTime
            self.line = not self.line
            
    # call this on mouse pressed / released
    def checkSelected(self, event):
        self.selected = \
            event.x > self.x1 and event.x < self.x2 and \
            event.y < self.y2+self.render and event.y > self.y1+self.render
            
    def takeInput(self, event):
        addables = \
        set('QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890 -:')
        if not self.selected:
            return 0
        returnValue = 1
        if event.keysym == 'BackSpace' and len(str(self.message))>0:
            if isinstance(self.message, Move): returnValue = self.message
            self.message = str(self.message)[:-1]
        elif event.keysym == 'Return':
            suggs = self.getSuggestions()
            if suggs != []:
                self.message = suggs[0]
        elif event.char in addables and len(str(self.message)) < self.maxChar:
            if isinstance(self.message, Move): returnValue = self.message
            self.message = str(self.message) + event.char
        else:
            returnValue = 0
        return returnValue
    
    def get(self):
        return self.message
        
    def delete(self):
        self.message = ''
        
    def updateSuggestions(self, newSuggs):
        self.suggestions = newSuggs
    # there's a drop down menu for some of the entries
    # this returns the values needed in those
    def getSuggestions(self):
        if self.suggestions == None: return []
        try:
            sugg = [self.suggestions[i] for i in self.suggestions \
            if str(i).startswith(removeSpace(self.message.upper())) and\
             len(self.message) > 1]
        except:
            sugg = [s for s in self.suggestions \
            if s.startswith(str(self.message).upper()) \
            and len(str(self.message)) > 1]
        if str(self.message).upper() in sugg or \
        capitalize(str(self.message)) in sugg: 
            return []
        return sugg
        
    def updateRender(self, dRender):
        self.render += dRender
        
# handles input from the user for pokemon as objects
class PokeData(object):
    
    def __init__(self, width, height, center, pokemonList, movesList):
        # width = data.width
        # height = center height
        # standard size 
        self.width = .8*width
        self.height = height
        self.center = center
        entrySize = (180, 27)
        smallEnt = (50, 27)
        self.type = ['pkmn', 'move', 'move', 'move', 'move', \
        'HP', 'spd', 'atk', 'def', 'spA', 'spD']
        self.render = 0
        
        num = 40
        den = 60
        
        top = center[1]-height//2
        #pokemonList = [pkmn.split()[1] for pkmn in pokemonList]
        self.entries = [\
        # pokemon
        MyEntry(*entrySize, (width//4, top+height*43//50), pokemonList), \
        # moves
        MyEntry(*entrySize, (width//2, top+13*height//50), movesList), \
        MyEntry(*entrySize, (width//2, top+23*height//50), movesList), \
        MyEntry(*entrySize, (width//2, top+33*height//50), movesList), \
        MyEntry(*entrySize, (width//2, top+43*height//50), movesList), \
        # EVs
        MyEntry(*smallEnt, (num*width//den, top+13*height//50), \
        max=3, blank='HP'), \
        MyEntry(*smallEnt, (num*width//den, top+23*height//50), \
        max=3, blank='Spe'), \
        MyEntry(*smallEnt, ((num+5)*width//den, top+13*height//50), \
        max=3, blank='Atk'), \
        MyEntry(*smallEnt, ((num+5)*width//den, top+23*height//50), \
        max=3, blank='Def'),
        MyEntry(*smallEnt, ((num+10)*width//den, top+13*height//50), \
        max=3, blank='SpA'), \
        MyEntry(*smallEnt, ((num+10)*width//den, top+23*height//50), \
        max=3, blank='SpD')]
        
    def __getitem__(self, index):
        return self.entries[index]
        
    def updateRender(self, dRender):
        self.render += dRender
        for ent in self.entries:
            ent.updateRender(dRender)
    
    # update the moves whenever the pokemon changes
    def updateSuggestions(self, allPokemon, allMoves, movesets):
        
        if self.entries[0].get().upper() in allPokemon:
            newSuggs = {key: allMoves.get(key) for key in\
             movesets[self.entries[0].get().upper()] if allMoves.get(key) != None}
             
            for key in newSuggs:
                if newSuggs[key] == None: del newSuggs[key]
            
            for ent in self.entries[1:5]:
                ent.updateSuggestions(newSuggs)
        else:
            for ent in self.entries[1:5]:
                ent.updateSuggestions(allMoves)
        
    def onMouseReleased(self, event):
        for ent in self.entries:
            ent.checkSelected(event)
            
    def onTimerFired(self, dt):
        for ent in self.entries:
            ent.blink(dt)
        
    def onKeyPressed(self, event):
        
        if event.keysym == 'Tab':
            for i in range(len(self.entries)):
                if self.entries[i].selected:
                    self.entries[i].selected = False
                    if i+1 < len(self.entries):
                        self.entries[i+1].selected = True
                    break
        
        for i in range(len(self.entries)):
            taken = self.entries[i].takeInput(event)
            if taken == 1:
                return self.entries[i], self.type[i]
            elif isinstance(taken, Move):
                return self.entries[i], taken
                
        return None, None
    
    # get bounding rectangle of the object
    def getRect(self):
        result = (int(self.center[0]-self.width//2), \
        int(self.center[1]-self.height//2+self.render),\
        int(self.center[0]+self.width//2),\
        int(self.center[1]+self.height//2+self.render))
        return result
                
    def draw(self, canvas, data):
        canvas.create_rectangle(self.getRect(), outline='grey', \
        fill=rgbString((200, 225, 225)))
        
        for ent in self.entries:
            ent.draw(canvas)
        for ent in self.entries:
            if ent.selected:
                height = ent.y2+10
                for sugg in ent.getSuggestions():
                    canvas.create_text(ent.x1+3, height+self.render,\
                     text=sugg, anchor='w')
                    height += 12
        
        if removeSpace(self.entries[0].get().upper()) in data.allPokemon:
            id = getPokedexID(self.entries[0].get())
            canvas.create_image((self.entries[0].x1+self.entries[0].x2)/2,\
             self.center[1]+self.render-5, image = data.frontImage[id])
        
        canvas.create_text(self.entries[0].x1, self.entries[0].y1-5+self.render, \
        anchor='sw', text='Pokemon')
        canvas.create_text(self.entries[1].x1, self.entries[1].y1-5+self.render, \
        anchor='sw', text='Moves')
        canvas.create_text(self.entries[5].x1, self.entries[5].y1-5+self.render, \
        anchor='sw', text='EVs (default 0)')
        
    def get(self):
        for i in range(len(self.entries)):
            if self.entries[i].selected:
                return self.entries[i].get()
                
    def getSuggestions(self):
        for ent in self.entries:
            if ent.selected:
                return ent.getSuggestions()
                

    
# converts rgb into hexadecimal
def rgbString(rgb):
    return "#%02x%02x%02x" % (rgb[0], rgb[1], rgb[2])
    

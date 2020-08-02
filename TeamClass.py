
## Helper functions
# helper for drawSummary
def darker(color):
    if isinstance(color, str) and color[-1].isdigit():
        return color[:-1]+str(int(color[-1])+1)

class Team(object):
    ## Standard methods
    
    def __init__(self, listOfPokemon):
        self.pokemon = listOfPokemon
        self.setCurrentPokemon()
        
    def __getitem__(self, index):
        return self.pokemon[index]
    
    def __setitem__(self, key, item):
        self.pokemon[key] = item
        
    ## Setter methods
        
    def setCurrentPokemon(self, pkmn=0):
        if isinstance(pkmn, int):
            pkmn = self.pokemon[pkmn]
        self.currentPokemon = pkmn
        self.currentPokeNo = self.pokemon.index(self.currentPokemon)
        
    def removeAllStatus(self):
        for pokemon in self.pokemon:
            pokemon.status = None
            pokemon.statusCounter = 0
            
    def switchPokemon(self, index):
        if not self[index].hasFainted():
            self.currentPokemon.statusCounter = 0 
            self.currentPokemon.protectCounter = 0  
            self.currentPokemon.removeBoosts()
            self.currentPokemon = self[index]
        
    def removeNone(self):
        i=0
        while i < self.len():
            if self[i] == None:
                self.pokemon.pop(i)
            else:
                i += 1
        self.currentPokemon = self[0]
        
        
    ## Getter methods
    
    def display(self):
        for i in range(len(self.pokemon)):
            if self[i] == None:
                continue
            print('%d) %s' % (i, self[i]))
            for move in self[i].moves:
                print('  %s' % move)
            print(self[i].EV)
            
    def len(self):
        return len(self.pokemon)
        
    def faintCount(self):
        count = 0
        for pokemon in self.pokemon:
            if pokemon.hasFainted():
                count += 1
        return count
    
    def isUnusable(self):
        return self.faintCount() >= self.len()
        
    ## Tkinter draw methods
    
    def drawSummary(self, canvas, data):
        xUnit = data.width/2
        yUnit = data.height/3
        coords = [(0, 0), (xUnit, 0), (0, yUnit), \
        (xUnit, yUnit), (0, 2*yUnit),(xUnit, 2*yUnit)]
        i=0
        for coord in coords:
            if i < len(self.pokemon) and self[i].hasFainted():
                color = 'khaki3'
            else:
                color = 'steelblue1'
            if i == data.arrowPos: color = darker(color)
            canvas.create_rectangle(coord, coord[0]+xUnit, \
            coord[1]+yUnit, fill=color)
            
            if i < len(self.pokemon):
                # draw summary
                newCoord = (coord[0]+xUnit, coord[1]+yUnit)
                self[i].drawSummary(canvas, coord, newCoord, \
                self.currentPokemon == self[i])
                
                # draw icon
                mult = 3 if i == data.arrowPos else 1
                exp = 2 if i == data.arrowPos and \
                self[i].currentHP > self[i].stat['HP']*.1 else 1
                if self[i].hasFainted(): mult = 0
                newCoord = (coord[0]+xUnit*.05, coord[1]+yUnit*.1 +\
                 mult*(-1)**int(data.vibrate*exp))
                canvas.create_image(newCoord, anchor='nw', \
                image=data.icons[self[i].id])
            i += 1
        
    ## Action methods
    
    def calculateSynergy(self, type):
        synergyCheck = 1
        for pokemon in self.pokemon:
            synergyCheck *= int(2*pokemon.attackMultiplier(type)+1)
        return synergyCheck
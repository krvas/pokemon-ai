from TypeClass import *
from dataFormat import *
import copy
import random

def allStats():
    return ['HP', 'atk', 'def', 'spA', 'spD', 'spd']

class Species(object):
    ## Standard methods
    def __init__(self, idOrName):
        if isinstance(idOrName, int):
            id = idOrName
        else: # expecting a string
            id = getPokedexID(capitalize(idOrName))
        self.id = id
        self.name = getPokemonName(id)
        self.typing = getPokemonTyping(id)
        self.base = convertToDict(allStats(), getPokemonBaseStats(id))
        # possible abilities, movepool, sprite
        
    def __repr__(self):
        return self.name
        
    def __eq__(self, other):
        return isinstance(other, Pokemon) and \
        self.id == other.id
        
    ## Getter methods
    def speciesData(self):
        result = 'Pokemon #'+str(self.id)+': '+self.name+'\n'
        result += str(self.typing)+'\n'
        for key in ['HP', 'atk', 'def', 'spA', 'spD', 'spd']:
            result += 'Base '+key+': '+str(self.base[key])+'\n'
        result = result[:-1]
        return result
        
    def attackMultiplier(self, otherType):
        return self.typing.attackMultiplier(otherType)
        
class Pokemon(Species):
    
    ## standard object methods
    def __init__(self, idOrName, args=None):
        
        super().__init__(idOrName)
        
        self.setLevel()
        self.setEVs()
        self.setIVs()
        
        possibleArgs = ['level', 'EV', 'IV']
        for arg in possibleArgs:
            if args and arg in args:
                self.__dict__[arg] = args[arg]
                
        self.setStats()
        self.setMoves([])
        self.status = None
        self.statusCounter = 0
        self.item = None
        
        self.multiplier = {}
        for stat in allStats():
            self.multiplier[stat] = 0
        self.protected = False
        self.protectCounter = 0
        self.seeded = False
        self.animationCounter = 0
    
    def __eq__(self, other):
        return self is other
        
    def __getitem__(self, index):
        return self.moves[index]
        
    ## static methods
    # helper function for damageDone
    # converts +1/-1 into actual multipliers
    @staticmethod
    def modifier(multiplier):
        magnitude = abs(multiplier)
        direction = 1 if magnitude == multiplier else -1
        
        return (1 + .5*magnitude) ** direction
    
    ## setter methods
    def copy(self):
        cpy = Pokemon(self.id)
        cpy.__dict__ = copy.deepcopy(self.__dict__)
        return cpy
        
    def setLevel(self, level=100):
        self.level = max(min(level, 100), 1)
        
    def setEVs(self, EVs=(0,0,0,0,0,0)):
        stat = allStats()
        self.EV = {}
        for i in range(len(stat)):
            self.EV[stat[i]] = EVs[i]
            
    def setIVs(self, IVs=(31, 31, 31, 31, 31, 31)):
        stats = allStats()
        self.IV = {}
        for i in range(len(stats)):
            self.IV[stats[i]] = IVs[i]
            
    def setStatus(self, status):
        if self.status == None and not self.isImmuneTo(status):
            self.status = status
            self.statusCounter = 0
            if status == 'asleep':
                self.sleepTurns = random.randint(0, 2)
                print(self.sleepTurns)
        else:
            return 'stat not set'
            # raise flag, so that I can handle errors if I want to
            
    def setTempStatus(self, status):
        pass
            
    # sets the stats for the pokemon
    # based on the formula in Bulbapedia
    # https://bulbapedia.bulbagarden.net/wiki/Statistic#In_Generation_III_onward
    def setStats(self): # ignores nature for the time being
        self.stat = {}
        normalStats = ['atk', 'def', 'spA', 'spD', 'spd']
        for stat in normalStats:
            intermediate = 2*self.base[stat] + self.EV[stat]//4 + self.IV[stat]
            self.stat[stat] = int(intermediate*self.level/100)+5
            
        # set HP separately, because it's different
        intermediate = 2*self.base['HP'] + self.EV['HP']//4 + self.IV['HP']
        self.stat['HP'] = int(intermediate*self.level/100)+self.level+10
        self.currentHP = self.stat['HP']
        
    def setMoves(self, moves):
        self.moves = moves
        
    def heal(self, percent):
        newHP = min(self.currentHP + self.stat['HP']*percent//100,\
         self.stat['HP'])
        self.currentHP = newHP
        
    def removeBoosts(self):
        for key in self.multiplier:
            self.multiplier[key] = 0
            
    def addMove(self, move):
        self.moves += [move]
        
    def deleteMove(self, move):
        for mov in self.moves:
            if mov == move:
                self.moves.remove(mov)
            
    ## getter methods
    
    def hasFainted(self):
        result = self.currentHP <= 0
        return result
        
    def displayMoves(self):
        for i in range(len(self.moves)):
            print('%d)' % (i+1), self.moves[i])

    def isImmuneTo(self, status):
    	if status == 'burn' and self.typing.contains(Type('fire')):
    		return True
    	elif status in {'poison', 'bad poison'} and \
    	(self.typing.contains(Type('poison')) or self.typing.contains(Type('steel'))):
    		return True
    	elif status == 'paralysed' and self.typing.contains(Type('electric')):
    		return True
    	elif status == 'frozen' and self.typing.contains(Type('ice')):
    		return True
    	else:
    		return False
        
    def damageDone(self, other, move):
        thisMove = self.moves[move]
        if other.attackMultiplier(thisMove.type) != 0:
            if thisMove.functionCode == '06D':
                return self.level
            elif thisMove.functionCode == '06C':
                return max(other.currentHP//2, 1)
            elif thisMove.functionCode == '06E':
                return other.stat['HP']-min(self.currentHP, other.currentHP)
        atkStat = 'atk' if thisMove.kind == 'Physical' else 'spA'
        defStat = 'def' if thisMove.kind == 'Physical' else 'spD'
        if thisMove.functionCode == '122': defStat = 'def'
        
        atk = self.stat[atkStat]*Pokemon.modifier(self.multiplier[atkStat])
        Def = other.stat[defStat]*Pokemon.modifier(other.multiplier[defStat])
        
        if thisMove.functionCode == '0A9': Def = min(other.stat[defStat], Def)
        
        if self.status == 'burn' and thisMove.kind == 'Physical' and\
         thisMove.functionCode != '07E':
            atk /= 2
            
        power = self.handlePowerAndFC(other, thisMove)
        STAB = 1.5 if self.typing.contains(thisMove.type) else 1
        levelModifier = 2*self.level/5
        intermediate = power*atk/Def/50
        modifier = other.attackMultiplier(thisMove.type)*STAB
        damage = int((levelModifier*intermediate + 2)*modifier)
        
        return damage
        
    def handlePowerAndFC(self, other, thisMove):
        power = thisMove.power
        if (thisMove.functionCode == '07B' and \
        other.status in {'bad poison', 'poison'}) or \
        (thisMove.functionCode == '07F' and other.status != None) or \
        (thisMove.functionCode == '07E' and self.status != None) or \
         thisMove.functionCode == '086':
            power *= 2
            
        if thisMove.functionCode == '089':
            power = 102
        elif thisMove.functionCode == '08B':
            power = max(1, self.currentHP*150//self.stat['HP'])
        elif thisMove.functionCode == '08D':
            power = min(max(1, other.netSpeed()*25//self.netSpeed()), 150)
        return power
        
        
    # calculates the number of hits needed to KO a Pokemon with a certain move
    def hitsNeeded(self, other, move=None, booster=0):
        '''
        if self.moves[move].isNonDamaging(): return None
        leastMultiplier = 0.85
        
        best = self.hitsNeededHelper(other, move, 10, booster)
        worst = self.hitsNeededHelper(other, move, int(10//leastMultiplier),\
         booster)
        
        return [best, worst]
        '''
        # Alternatively:
        maximum = 10
        if move != None:
            try:
                avgMultiplier = 0.925
                if self.moves[move].isDamaging():
                    avgMultiplier *= self.moves[move].accuracy/100
                avgDamage = self.damageDone(other, move)*avgMultiplier
                hits = max(other.currentHP/\
                (self.damageDone(other, move)*avgMultiplier), 1)
                return min(hits, maximum)
            except ZeroDivisionError:
                return maximum
        else:
            values = [self.hitsNeeded(other, i) \
            for i in range(len(self.moves)) if self.moves[i].isDamaging()]
            values.sort()
            if values == []:
                return maximum
            else:
                return values[0]
        
        
    def hitsNeededHelper(self, other, move, max, booster):
        result = max
        hp = other.currentHP
        boostedStat = None
        if self.moves[move].kind == 'Physical':
            boostedStat = 'atk'
        elif self.moves[move].kind == 'Special':
            boostedStat = 'spA'
        if boostedStat: self.multiplier[boostedStat] += booster
        
        for i in range(max):
            # if it takes more than 'max' hits, it's not worth it
            if hp < 0:
                result = i
                break
            hp -= self.damageDone(other, move)
        if boostedStat: self.multiplier[boostedStat] -= booster
        return result
            
    # returns all non damaging moves of the pokemon
    def getAllNonDamagingMoves(self):
        moves = {}
        for i in range(len(self.moves)):
            if self.moves[i].isNonDamaging():
                moves.add(i)
        return moves
        
    def getAllDamagingMoves(self):
        return set(range(len(self.moves))) - self.getAllNonDamagingMoves()
        
    def isStatused(self):
        return not self.status
            
    def canHeal(self):
        for move in self.moves:
            if move.functionCode in ['0D5', '0D6', '0D8', '0DC']:
                return True
        return False
        
    def canSetUp(self): 
        setups = {'01C', '020', '024', '025', '026', '027', '028', '029',\
        '02B', '02C', '02E', '032', '035', '036', '039', '03A'}
        for move in self.moves:
            if move.functionCode in setups:
                return True
        return False
        
    def setUpMoves(self):
        setups = {'01C', '020', '024', '025', '026', '027', '028', '029',\
        '02B', '02C', '02E', '032', '035', '036', '039', '03A'}
        moves = []
        for i in range(len(self.moves)):
            move = self.moves[i]
            if move.functionCode in setups:
                moves += [i]
        return moves
    
    def netSpeed(self):
        result = self.stat['spd']*Pokemon.modifier(self.multiplier['spd'])
        if self.status == 'paralysed':
            result //= 4
        return result
        
    ## Tkinter drawing methods
    # draws status as well
    def drawHPBar(self, canvas, x1, y1, x2, y2):
        percentHP = max(self.currentHP/self.stat['HP'], 0)
        width = x2 - x1
        midPointX = width*percentHP + x1
        color = 'green' if self.currentHP >= .5*self.stat['HP'] else 'yellow'
        if self.currentHP < .1*self.stat['HP']: color = 'red'
        canvas.create_rectangle(x1, y1, midPointX, y2, fill=color)
        canvas.create_rectangle(midPointX, y1, x2, y2, fill="Black")
        
        height = y2 - y1
        y1 += height+1
        y2 += height+1
        width *= .15
        colors = {'paralysed': 'yellow', 'magenta': 'purple', 'asleep': 'gray',\
                'bad poison':'purple', 'frozen':'cyan', 'burn':'red'}
        if self.status and not self.hasFainted():
            canvas.create_rectangle(x1, y1, x1+width, y2, \
            fill=colors.get(self.status), width=0)
            
        self.drawStatusRect(canvas, x1, y1, x2-x1, y1 + (y2-y1)*4/3)
            
    def drawStatusRect(self, canvas, x1, y1, width, y2):
        rectWidth = width//4
        x1 += width//6
        margin = 2
        y1 += margin
        y2 += margin
        
        i=0
        for key in self.multiplier:
            if self.multiplier[key] < 0:
                canvas.create_rectangle(x1+margin+i*rectWidth, y1, \
                x1+(i+1)*rectWidth, y2, \
                fill='tan1', outline='fireBrick1', width=margin)
                sign = '' # already in the value
            elif self.multiplier[key] > 0:
                canvas.create_rectangle(x1+margin+i*rectWidth, y1, \
                x1+(i+1)*rectWidth, y2, \
                fill='greenYellow', outline='limeGreen', width=margin)
                sign = '+'
            if self.multiplier[key] != 0:
                canvas.create_text(x1+(i+.5)*rectWidth, (y1+y2)/2,  \
                text=key+' '+sign+str(self.multiplier[key]))
                i += 1
        #canvas.create_text(x1, y2, anchor='nw', text=str(self.multiplier))
        
    def drawSummary(self, canvas, topLeft, bottomRight, isActive):
        left, top = topLeft
        right, bottom = bottomRight
        width, height = right-left, bottom-top
        margin = .2*width
        txt = self.name+' (active)' if isActive else self.name
        canvas.create_text((left+right)//2, top+.1*height, text=txt)
        self.drawHPBar(canvas, left+margin, top+.2*height, right-margin, \
        top+.3*height)
        i=0
        for move in self.moves:
            canvas.create_text(left+margin, top+.1*(i+5)*height, \
            text=move, anchor='w')
            i += 1
        
        i=0
        for j in allStats():
            wt1, wt2 = (2, 2) if i%2 == 0 else (1, 3)
            canvas.create_text((left*wt1+right*wt2)//4, \
            top+.1*(i//2+5)*height, \
            text=j+' - '+str(self.stat[j]), anchor='w')
            i += 1
    ## action methods
    # this code will need a lot of modification
    def attack(self, other, move):
        # keep this for now
        thisMove = self.moves[move]
        if int(thisMove.functionCode, 16) in range(int('6A', 16), int('75', 16)):
            damage = self.damageDone(other, move)
        else:
            damage = self.damageDone(other, move)*random.uniform(0.85, 1)
        other.currentHP -= damage
        
        return damage
        
        
    def useMove(self, selfTeam, otherTeam, move):
        other = otherTeam.currentPokemon
        
        if self.hasFainted(): return []
        thisMove = self.moves[move]
        # reset protect on non protect turns
        if thisMove.functionCode != '0AA':
            self.protectCounter = 0

        if thisMove.accuracy < random.randint(1,100) and thisMove.isDamaging():
            return ['The move missed']
        
        if thisMove.isDamaging():
            self.attack(other, move)
            
        if thisMove.effectChance > random.randint(1, 100) or \
         thisMove.isNonDamaging() or \
         thisMove.functionCode in Move.alwaysHappens:
            effect = thisMove.secondaryEffect(selfTeam, otherTeam)
            message = []
            if effect != 'stat not set':
                message = Move.message(thisMove.functionCode, self, other)  
                
            if effect not in {None, 'stat not set'}: message += [effect]
            return message
            
    # changes the stage( +1, -1, etc) for the pokemon's stats
    # won't go out of range of ± 6
    def changeStatMult(self, change, stats):
        for stat in stats:
            self.multiplier[stat] = \
            min(max(self.multiplier[stat]+change, -6), 6)
    
    def handleStatusAfterTurn(self):
        if self.status in ['burn', 'poison', 'bad poison']:
            if self.status == 'burn':
                self.currentHP -= self.stat['HP']//16
            elif self.status == 'poison':
                self.currentHP -= self.stat['HP']//8
            else:
                self.currentHP -= (self.stat['HP']//16) *\
                (2**(self.statusCounter))
            self.currentHP = max(0, self.currentHP)
            self.statusCounter += 1
            return '%s is hurt by %s' % (self.name, self.status)
            
        
    # returns 2 things: whether the pokemon is allowed to move this turn
    # and the message that needs to be displayed
    def handleStatusDuringTurn(self):
        if self.status not in ['asleep', 'paralysed', 'frozen']:
            return [True, None]
        result = ['%s is %s' % (self.name, self.status)]
        
        if self.status == 'asleep':
            if self.statusCounter > self.sleepTurns:
                self.status = None
                return [True, ['%s woke up' % self.name]]
            else:
                self.statusCounter += 1
                return [False, result]
                
        elif self.status == 'paralysed':
            if random.randint(1, 4) == 1:
                return [False, result+['%s couldn\'t move' % self.name]]
            else:
                return [True, result]
                
        elif self.status == 'frozen':
            if random.randint(1, 5) == 1:
                return [True, ['%s thawed out' % self.name]]
            else:
                return [False, result]

        
 
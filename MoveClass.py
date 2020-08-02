import random
from TypeClass import *

class Move(object):
    # moves who's secondary effect always happens
    alwaysHappens = {'001', '03B', '03C', '03D', '03E', '03F', '002', '0FA',\
     '0FB', '0FC', '0FD', '0FE'}
    
    def __init__(self, name, type, power, accuracy, kind, description=''):
        self.name = name
        self.type = Type(type)
        self.power = power
        self.description = description
        self.accuracy = accuracy
        self.kind = kind
        
    def __repr__(self):
        return self.name
        
    def setParameters(self, dictionary):
        self.__dict__ = dictionary
        
    def __eq__(self, other):
        return isinstance(other, Move) and self.name == other.name
        
    def __hash__(self):
        return hash((self.name, str(self.type), self.power, self.accuracy,\
        self.kind, self.functionCode))
        
    ## Getter methods
    
    def isNonDamaging(self):
        return 'kind' in self.__dict__ and self.kind == 'Status'
        
    def isDamaging(self):
        return 'kind' in self.__dict__ and self.kind in ['Physical', 'Special']
        
    ## Static methods
    @staticmethod
    def hiddenPower(IVs):
        IVmods = [elt % 2 for elt in IVs]
        typeDeterminer = 0
        step = 1
        for elt in IVmods:
            typeDeterminer += step*elt
            step *= 2
        typeDeterminer = int(typeDeterminer*15/63)
        types = ["fighting", "flying", "poison", "ground", "rock", "bug",\
                 "ghost", "steel", "fire", "water", "grass", "electric"\
                 "psychic", "ice", "dragon", "dark"]
        return types[typeDeterminer]
        
    @staticmethod
    def message(code, user, opponent):
        # fail cases
        if int(code, 16) in range(3, 14) and opponent.status:
            return []

        user = str(user)
        opponent = str(opponent)
        
        if int(code,16) in {0, 15}|set(range(106, 170)):return []
        elif code == '001': return ['Nothing happened']
        elif code in {'002', '0FA', '0FB', '0FC', '0FD', '0FE'}:
            return [name+' took recoil!']
        elif code == '003': return [opponent+' fell asleep']
        elif code == '005': return [opponent+' was poisoned']
        elif code == '006': return [opponent+' was badly poisoned']
        elif code == '007': return [opponent+' was paralyzed']
        elif code == '00A': return [opponent+' was burned']
        elif code in {'00C', '00D'}: return [opponent+' was frozen']
        elif code == '0AA': return [user+' attempted to protect itself']
        elif code == '019': return [user+' healed the status of its team']
        elif int(code,16) in range(26, 59): return [user+"'s stats were boosted"]
        elif int(code,16) in range(66, 71): return [opponent+"'s stats fell"]
        elif int(code,16) in range(59, 66): return [user+"'s stats fell"]
        elif code in {'0D5', '0D6', '0D8'}: return [user+" healed itself"]
        #elif code == '
        else: return ['It had an effect!']
        
        
    
    ## Handle secondary effects
    # redirector function
    def secondaryEffect(self, userTeam, opponentTeam):
        functionCode = int(self.functionCode, 16)
        user = userTeam.currentPokemon
        opponent = opponentTeam.currentPokemon
        if functionCode <= 2:
            self.almostNoEffect(user)
        elif functionCode <= int("01B", 16):
            return self.statusEffect(userTeam, opponent)
        elif functionCode <= int("03F", 16):
            self.statChange(user)
        elif functionCode <= int("04F", 16):
            self.statChange(opponent)
        elif functionCode <= int("05B", 16):
            self.otherStatChange(user, opponent)
        elif functionCode <= int("069", 16):
            self.changeAttribute(user, opponent)
        elif functionCode <= int("074", 16):
            self.fixedDamage(user, opponent)
        elif functionCode <= int("0A4", 16):
            self.affectAttackPower(user)
        elif functionCode <= int("0AD", 16):
            return self.hittingRelatedEffects(user, opponent)
        elif functionCode <= int("0BC", 16):
            self.almostNoEffect(user) # for now
        elif functionCode <= int("0D4", 16):
            self.almostNoEffect(user) # for now
        elif functionCode <= int("0DF", 16):
            self.heal(user, opponent)
        elif functionCode <= int("0E9", 16):
            self.involvesFaint(user, opponent)
        elif functionCode <= int("0EF", 16):
            self.switching(user, opponent)
        elif functionCode <= int("0F9", 16):
            self.itemsEffects(user, opponent)
        elif functionCode <= int("0FE", 16):
            self.recoil(user)
        elif functionCode <= int("102", 16):
            self.almostNoEffect(user) # for now
        elif functionCode <= int("105", 16):
            self.almostNoEffect(user) # for now
        elif functionCode <= int("108", 16):
            self.almostNoEffect(user) # for now
        else:
            self.handleOthers(user, opponent)
    
    # the following functions are helpers to the main wrapper function
    # they encode the effects, given a specific function code
    # some of them are empty, because they haven't been encoded yet
    def almostNoEffect(self, user):
        if self.functionCode == "002":
            user.currentHP -= .25*user.stat['HP']
            
    def statusEffect(self, userTeam, opponent):
        if self.functionCode in ['003', '004']:
            return opponent.setStatus('asleep')
        elif self.functionCode == '005':
            return opponent.setStatus('poison')
        elif self.functionCode == '006':
            return opponent.setStatus('bad poison')
        elif self.functionCode in ['007', '008', '009']:
            return opponent.setStatus('paralysed')
        elif self.functionCode in ['00A', '00B']:
            return opponent.setStatus('burn')
        elif self.functionCode in ['00C', '00D', '00E']:
            return opponent.setStatus('frozen')
        elif self.functionCode in ['00F', '010', '011', '012']:
            opponent.setTempStatus('flinch')
        elif self.functionCode in ['013', '014', '015']:
            opponent.setTempStatus('confusion')
        elif self.functionCode == '019':
            userTeam.removeAllStatus()
        
    def statChange(self, pkmnAffected):
        if self.functionCode in {'035', '036'}:
            self.variableStatChange(pkmnAffected)
            return
        elif self.functionCode in {'020', '021', '026', '02B', '02C', '01C', \
        '01D', '01E', '01F', '024', '025', '027', '028', '029', '02A', '02D'}:
            change = 1
        elif self.functionCode in {'02E', '02F', '030', '031', '032'}:
            change = 2
        elif self.functionCode in {'038', '039'}:
            change = 3
        elif self.functionCode in {'03A'}:
            change = 12
        elif self.functionCode in {'03B', '03C', '045', '046', '03D', '03E', \
        '042', '043', '044', '045', '046'}:
            change = -1
        elif self.functionCode in {'03F'}:
            change = -2
        
        stat = []
        if self.functionCode in {'026', '02E', '01C', '024', '025', '027', \
        '028', '029', '02D', '03A', '03B', '042'}:
            stat += ['atk']
        if self.functionCode in {'03C', '01D', '01E', '024', '025', '02A', \
        '02D', '02F', '038', '03B', '03D', '043'}:
            stat += ['def']
        if self.functionCode in {'020', '02B', '02C', '039', '03F', '045', \
        '027', '028', '02D', '032', '045'}:
            stat += ['spA']
        if self.functionCode in {'021', '02B', '02C', '03C', '046', '02A', \
        '02D', '033', '03D', '046'}:
            stat += ['spD']
        if self.functionCode in {'026', '02B', '01F', '02D', '030', '031', \
        '03D', '03E', '044'}:
            stat += ['spd']
            
        try:pkmnAffected.changeStatMult(change, stat)
        except:print (self.functionCode)
        
    def variableStatChange(self, pkmn):
        if self.functionCode == '035':
            pkmn.changeStatMult(2, ['atk', 'spA', 'spd'])
            pkmn.changeStatMult(-1, ['def', 'spD'])
        elif self.functionCode == '036':
            pkmn.changeStatMult(2, ['spd'])
            pkmn.changeStatMult(1, ['atk'])
            
            
    def otherStatChange(self, user, opponent):
        pass
        
    def changeAttribute(self, user, opponent):
        pass
        
    def fixedDamage(self, user, opponent):
        if self.functionCode == '06D':
            opponent.currentHP -= user.level
    
    # returns a boolean  describing whether the pokemon has been attacked
    def affectAttackPower(self, user, opponent):
        if self.functionCode == '086' and user.item == None:
            self.power *= 2
            user.attack(opponent, user.moves.find(self))
            self.power //= 2
            return True
        elif self.functionCode == '08D':
            self.power = \
            min(int((opponent.netSpeed()/user.netSpeed())*25),150)
        elif self.functionCode == '090':
            self.type = Move.hiddenPower(user.IVs)
        return False
    
    # like protect, etc.
    def hittingRelatedEffects(self, user, opponent):
        if self.functionCode == '0AA':
            failChance = 1 - 2 ** -user.protectCounter
            if failChance < random.uniform(0, 1):
                user.protected = True
                user.protectCounter += 1
            else:
                user.protectCounter = 0 # reset if failed
                return 'but it failed'
        
    def heal(self, user, opponents):
        if self.functionCode in ['0D5', '0D6', '0D8']:
            user.heal(50)
        '''# leech seed pending
        elif self.functonCode == '0DC':
            opponent.seeded = True'''
            
    def involvesFaint(self, user, opponent):
        pass
        
    def switching(self, userTeam, opponentTeam):
        if self.functionCode == '0EE':
            return 'switch'
            
    def itemsEffects(self, user, opponent):
        pass
        
    def recoil(self, user, opponent):
        if self.functionCode == '0FA':
            coil = .25
        elif self.functionCode in ['0FB', '0FD', '0FE']:
            coil = 1/3
        elif self.functionCode == '0FC':
            coil = .5
        damageDone = user.attack(opponent, user.moves.find(self))
        user.stat['HP'] -= coil*damageDone
        if user.hasFainted():
            return 'fainted'
        else:
            return True
            
    def handleOthers(self, user, opponent):
        pass
        
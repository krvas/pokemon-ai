'''

Evaluation.py
It contains methods that take in pokemon / move / data objects
And return assesments on how useful those pokemon and moves are


'''

import copy
from PokemonClass import Pokemon
from TeamClass import Team
from MoveClass import Move
import math

def debugger(f):
    def g(*args):
        result = f(*args)
        print(result)
        return result
    return g

# function decorator that edits all the evaluations based on certain criteria
def editEvaluation(f):
    
    def g(teamOrPkmn1, teamOrPkmn2, move):
        result = f(teamOrPkmn1, teamOrPkmn2, move)
        # insert editions here!
        pkmn1, team1, pkmn2, team2 = getTeamAndPkmn(teamOrPkmn1, teamOrPkmn2)
        thisMove = pkmn1[move]
        if pkmn1.status == 'asleep':
            result *= 2 ** (pkmn1.statusCounter - pkmn1.sleepTurns - 1)
        if thisMove.functionCode in {'026', '02B', '01F', '02D', '030', '031', \
        '03D', '03E'}:
            speedVal = evalSpeed(pkmn1, teamOrPkmn2, move)
            result = max(result*.8 + .4*speedVal, \
            result*.4 + .65*speedVal, .7*speedVal)
        elif thisMove.functionCode in {'020'}:
            result = \
            max(result*.65 + .65*evalSetup(pkmn1, pkmn2, thisMove), result)

        return result
    return g
    
    
# returns a value based on how useful the move would be to play
# wrapper that calls all the functions depending on what kind of move it is
@editEvaluation
def evaluate(teamOrPkmn1, teamOrPkmn2, move):
    standard = 1000
    pkmn1, team1, pkmn2, team2 = getTeamAndPkmn(teamOrPkmn1, teamOrPkmn2)
    thisMove = pkmn1.moves[move]
    
    if thisMove.isNonDamaging() and \
    int(thisMove.functionCode, 16) in range(int('1C', 16), int('3A', 16)) \
    and thisMove.functionCode != '020':
        return evalSetup(pkmn1, pkmn2, thisMove)
        
    elif thisMove.functionCode == '019' and isinstance(team1, Team) and\
     isinstance(team2, Team):
            return evalAromatherapy(team1, team2)
    elif thisMove.functionCode in {'018', '019'}:
        return evalRefresh(pkmn1, pkmn2)
        
    elif thisMove.isNonDamaging() and \
    int(thisMove.functionCode, 16) <= int("01B", 16):
        return evalStatus(pkmn1, pkmn2, thisMove)
            
    elif thisMove.isNonDamaging() and \
    int(thisMove.functionCode, 16) in range(int('D5', 16), int('E0', 16)):
        return evalHeal(pkmn1, pkmn2, move)
    
    elif thisMove.functionCode == '0AA':
        return evalProtect(pkmn1, pkmn2)
            
    elif thisMove.priority > 0 and pkmn1.hitsNeeded(pkmn2, move) == 1:
        return standard*.8 - pkmn1.hitsNeeded(pkmn2, move)/thisMove.priority
        
    elif thisMove.priority > 0 and \
    (pkmn2.hitsNeeded(pkmn1) == 1 and pkmn2.netSpeed() > pkmn1.netSpeed()):
        return evalDamaging(pkmn1, pkmn2, move)*1.2
        
    elif int(thisMove.functionCode, 16) in range(int('6A', 16), int('75', 16)):
        return evalSetDamage(pkmn1, pkmn2, move)
            
    else:
        return evalDamaging(pkmn1, pkmn2, move)
        
# format: pokemon, team, pokemon, team
def getTeamAndPkmn(teamOrPkmn1, teamOrPkmn2):
    result = []
    if isinstance(teamOrPkmn1, Team):
        result += [teamOrPkmn1.currentPokemon, teamOrPkmn1]
    else:
        result += [teamOrPkmn1, None]
    if isinstance(teamOrPkmn2, Team):
        result += [teamOrPkmn2.currentPokemon, teamOrPkmn2]
    else:
        result += [teamOrPkmn2, None]
    return result
        
def evalDamaging(pkmn1, pkmn2, move, override=None):
    standard = 1000
    if not override:
        hitsNeeded = pkmn1.hitsNeeded(pkmn2, move)
    else:
        hitsNeeded = pkmn2.currentHP/override + 1
        # add weight, because we don't want override to affect it too much
    bonus = .05*standard if hitsNeeded == 1 else 0
    return standard * (2 ** - (hitsNeeded/2)) + bonus
        
# sees how useful it is to setup on a pokemon
def evalSetup(pkmn1, pkmn2, thisMove):
    standard = 1000
    pkmn1Copy = pkmn1.copy()
    thisMove.statChange(pkmn1Copy)
    
    value = pkmn1.hitsNeeded(pkmn2)
    valueCopy = pkmn1Copy.hitsNeeded(pkmn2)
    # if the set-up and the attack take the same number of hits to KO
    # which should be preffered?
    # in the line below, change '1' to see
    # x < 1 implies set-up is preffered and vice versa
    if pkmn1.status == 'bad poison':
        exp = 2
    elif pkmn1.status:
        exp = 1.3
    else:
        exp = 1
    if value - valueCopy < 0.05:
        return 0
    else:
        bias = -0.5 # taking inspiration from ML
        return standard * (pseudosigmoid(value - valueCopy -\
        pkmn1.stat['HP']/pkmn2.hitsNeeded(pkmn1)**2/pkmn1.currentHP + bias)**exp)
        
def evalSpeed(pkmn1, teamOrPkmn2, move):
    standard = 1000 # not too useful
    thisMove = pkmn1.moves[move]
    pkmn2, team2 = getTeamAndPkmn(teamOrPkmn2, None)[:2]
    
    if not pkmn1.canSetUp():
        return standard*.05
    
    setUp = pkmn1.setUpMoves()
    value = 0
    pkmn1Copy = pkmn1.copy()
    pkmn1Copy.removeBoosts()
    for i in range(len(setUp)):
        value += evalSetup(pkmn1Copy, pkmn2, pkmn1Copy[setUp[i]])
    value /= len(setUp)
    pkmn1Copy = pkmn1.copy()
    thisMove.statChange(pkmn1Copy)
    
    if isinstance(team2, Team):
        
        outSpeed = 0
        count = sum([1 for pkmn in team2 if not pkmn.hasFainted()])
        outSpeed = getOutSpeeds(pkmn1Copy, team2) - getOutSpeeds(pkmn1, team2)
        thisMove.statChange(pkmn1Copy)
        outSpeed2 = getOutSpeeds(pkmn1Copy, team2) - getOutSpeeds(pkmn1, team2)
        outSpeed = max(outSpeed, outSpeed2)
        
        return value * (outSpeed/count) * 2
    else:
        return value + (5 if pkmn1.netSpeed() < pkmn2.netSpeed() and\
         pkmn1Copy.netSpeed() > pkmn2.netSpeed() else -value*.95)
    
def getOutSpeeds(pkmn, team):
    result = 0
    for pokemon in team.pokemon:
        if not pokemon.hasFainted() and pkmn.netSpeed() > pokemon.netSpeed():
            result += 1
    return result
    
def pseudosigmoid(x):
    base = math.e
    try:
        return 1/(1+base**(-x))
    except OverflowError:
        return 0 if x < 0 else 1
        
# how good will a particular status move be, if used on pkmn2
def evalStatus(pkmn1, pkmn2, thisMove):
    standard = 700
    if pkmn2.status != None:
        return 0
    elif thisMove.functionCode in ['00A', '00B']: # burns
        return evalBurn(pkmn1, pkmn2)
    elif thisMove.functionCode == '006': # bad poison
        return evalToxic(pkmn1, pkmn2)
    elif thisMove.functionCode == '005': #regular poison - not too useful
        return standard//6 if not pkmn2.isImmuneTo('poison') else 0
    return 0
    
def evalSleep(pkmn1, pkmn2):
    # edit if you add sleep clause
    standard = 900
    if not pkmn1.canSetUp():
        return standard*.1 # pretty useless/annoying if it can't set up
    
    risk = 1/(pkmn2.hitsNeeded(pkmn1)+.5)
    if pkmn2.stat['spd'] < pkmn1.stat['spd']: risk **= 2.2
    pkmn1Copy = pkmn1.copy()
    value = []
    for move in pkmn1.setUpMoves():
        value += evaluate(pkmn1, pkmn2, move)
    
    return max(value)*1.5*(1-risk)

def evalPara(pkmn1, pkmn2):
    minimum = 250
    maximum = 720

    if pkmn2.isImmuneTo('paralysed'): return 0
    
    if pkmn.netSpeed() < 260:
        return minimum//3
    
    ratio = (pkmn2.stat['spd']-170)/400
    ratio = 1 - (1 - ratio)**Pokemon.modifier(pkmn2.multiplier['spd'])
    
    return max(minimum, minimum + ratio*(maximum-minimum))
    
    
def evalBurn(pkmn1, pkmn2):
    standard = 700
    if pkmn2.isImmuneTo('burn'): return 0
    # the number of physical moves should not be a big factor
    # but if it's 0, it should be significantly different from nonzero
    # simply the existence of special moves should reduce the worth of burn
    # if the opponent can one-shot the pokemon, I'd prefer to burn them
    # the higher the attack multiplier of pkmn2 is, the more useful burn is
    phyCount = sum([1 for move in pkmn2.moves if move.kind == 'Physical'])
    spePower = sum([move.power for move in pkmn2.moves \
    if move.kind == 'Special' ])
    canOneShot = pkmn2.hitsNeeded(pkmn1) == 1
    investment = max(pkmn2.multiplier['atk'], 0)
    
    minimum = 150
    weight = .2
    exp = Pokemon.modifier(investment)+1
    result = standard * (1 - (1 - phyCount/4)**exp) ** (1/exp)
    result = (result + weight*minimum)/(1+weight)
    
    spCutoff = 60
    if spePower > spCutoff: result /= 3
    if canOneShot: result *= 1.4
        
    return result
    
# what if pkmn1 used toxic on pkmn2?
def evalToxic(pkmn1, pkmn2):
    standard = 600 if pkmn1.netSpeed() > pkmn2.netSpeed() else 800
    if pkmn2.isImmuneTo('bad poison'): return 0
    turns = toxicTurnsLeft(pkmn2)
    
    variables = [pkmn1.hitsNeeded(pkmn2)>1, pkmn1.canHeal(), not pkmn2.canHeal()]
    factors = 0
    for var in variables:
        if var: factors += 1
        
    result = max(math.tanh((sum(pkmn2.multiplier.values())//2 + \
    pkmn2.hitsNeeded(pkmn1) - 3)//2), 0.1)
    
    return standard * (result ** (len(variables) - factors + 1) + (turns-2)/15)
    
def evalSetDamage(pkmn1, pkmn2, move):
    thisMove = pkmn1.moves[move]
    damage = pkmn1.damageDone(pkmn2, move)
        
    return evalDamaging(pkmn1, pkmn2, move, override=damage)
    
    
def evalHeal(pkmn1, pkmn2, move):
    standard = 1000
    
    pkmn1Copy = pkmn1.copy()
    pkmn2Copy = pkmn2.copy()
    team1Copy = Team([pkmn1Copy])
    team2Copy = Team([pkmn2Copy])
    pkmn1Copy.useMove(team1Copy, team2Copy, move)
    
    HPAfterHeal = pkmn1Copy.currentHP
    pkmn1Copy.handleStatusAfterTurn()
    HPAfterHealAndStatus = pkmn1Copy.currentHP
    
    changeInHP = (HPAfterHeal + HPAfterHealAndStatus)/2 - pkmn1.currentHP
    
    statusThreshold = 3
    oddCase = pkmn1.currentHP if pkmn1.statusCounter > statusThreshold else 0
    
    result = standard * (max(changeInHP, oddCase) / pkmn1.stat['HP'])
    
    # healing won't be of much help if you'll get KOed
    if pkmn2.netSpeed() > pkmn1.netSpeed() and pkmn2.hitsNeeded(pkmn1) == 1:
        result /= 3
        
    return result
    
def evalAromatherapy(team1, team2):
    standard = 1000
    pkmn1 = team1.currentPokemon
    cumulativeValue = 0
    count = 0
    
    for pokemon in team1.pokemon:
        if pokemon.hasFainted(): continue
        if pokemon.status not in {'bad poison', 'frozen'}:
            cumulativeValue += evalRefresh(pokemon, team2.currentPokemon)
        elif pokemon.status == 'bad poison':
            urgency = toxicTurnsLeft(pokemon)
            cumulativeValue += standard*\
            (averageAdvantage(pokemon, team2)/standard)**(1/urgency)
        elif pokemon.status == 'frozen':
            cumulativeValue += averageAdvantage(pokemon, team2)*.6*standard
        count += 1
    wt = 0.3
    value = (cumulativeValue/(count*standard) + wt*ratioLossStatus(pkmn1))/(1+wt)
    # the fewer pokemon I have, the more I need to heal them
    return value*standard

def evalRefresh(pkmn1, pkmn2, standard=500):
    pkmn1Copy = pkmn1.copy()
    for move in pkmn1.moves:
        if move.functionCode in {'018', '019'}:
            pkmn1Copy.moves.remove(move)
    # in order to avoid recursion depth errors, remove refresh
    
    if pkmn1Copy.status == 'burn':
        return standard*(pkmn1Copy.stat['atk']/500)**2
    elif pkmn1Copy.status == 'bad poison':
        urgency = toxicTurnsLeft(pkmn1Copy)
        return standard*\
        (advantage(pkmn1Copy, pkmn2)/standard)**(1/urgency)
    elif pkmn1Copy.status == 'poison':
        return .1*standard
        # not too important
    elif pkmn1Copy.status == 'paralysed':
        return standard*(pkmn1Copy.stat['spd']/500)**2
    elif pkmn1Copy.status == 'frozen':
        return advantage(pkmn1Copy, pkmn2)*.6*standard
    elif pkmn1Copy.status == 'asleep':
        # sleep is mainly viable if the asleep pokemon
        # is good against the opponent's current pokemon
        urgency = pkmn1Copy.sleepTurns
        return standard*(advantage(pkmn1Copy, pkmn2)/standard)**(1/urgency)
    
    return 0
    
def toxicTurnsLeft(pkmn):
    turns = 0
    counter = pkmn.stat['HP']//16
    hp = pkmn.currentHP
    
    while hp > 0:
        hp -= counter * (2**turns)
        turns += 1
    return turns
    
# in single battles, there are only very specific instances for protect
# in other cases, it's useless
# additionally, it should be scaled by the chance that it happens
# which drops exponentially when you use it again and again
def evalProtect(pkmn1, pkmn2):
    standard = 700
    # see if the user / opponent lose HP
    pkmn1Loss = ratioLossStatus(pkmn1)
    pkmn2Loss = ratioLossStatus(pkmn2)
    pkmn2Loss = 0 if pkmn2Loss == 0 else 2*(pkmn2Loss+.1)*(pkmn2Loss-1)+1
    noFailChance = 2 ** - pkmn1.protectCounter
    pkmn2CanSetUp = 1 if pkmn2.canSetUp() else 0
    
    return standard*pkmn2Loss*noFailChance - \
    standard*.15*pkmn1Loss - standard*.15*pkmn2CanSetUp
    
# calculates how much HP is lost as a percentage of current HP
# there might be a bug here
def ratioLossStatus(pkmn):
    pkmnCopy = pkmn.copy()
    pkmnCopy.handleStatusAfterTurn()
    try:
        return (pkmn.currentHP - pkmnCopy.currentHP)/pkmn.currentHP
    except ZeroDivisionError:
        return 0
    
    
    
# returns the obvious move for pkmn1 to play against pkmn2
def obviousMove(pkmn1, pkmn2):
    
    cutoff = 1.2
    # cutoff - how far does the 'best' move need to be, to be obvious?
    values = [(evaluate(pkmn1, pkmn2, i), i) for i in range(len(pkmn1.moves))]
    values.sort()
    
    if len(values) == 1:
        return 0
    elif values[-1][0] > values[-2][0]*cutoff:
        return values[-1][1]
    else:
        return None
        
# calculates the cost incurred in swapping a pokemon in
def costToSwap(swapFrom, swapTo, opponent):
    
    inf = 10**10
    if swapFrom == swapTo: return inf
    # you can't swap in yourself
    
    # calculate the probability of the opponent using each of its moves
    probabilities = [evaluate(opponent, swapFrom, move) \
    for move in range(len(opponent.moves))]
    total = sum(probabilities)
    # normalize the probabilities
    for i in range(len(probabilities)):
        probabilities[i] /= total
    
    # calculate the cost that each move incurs, on switch in
    moveCost = [evaluate(opponent, swapTo, move) \
    for move in range(len(opponent.moves))]
    
    totalCost = sum([moveCost[i]*probabilities[i] \
    for i in range(len(opponent.moves))])
    
    return totalCost
    
# how much would it cost a pokemon if it lost all its boosts?
def costOfBoosts(pkmn, oppo):
    pkmnCopy = pkmn.copy()
    pkmnCopy.removeBoosts()
    loss = (advantage(pkmn, oppo) - advantage(pkmnCopy, oppo))*1.2
    return loss
    
# in general, how useful is this pkmn1 against pkmn2
def advantage(pkmn1, pkmn2):
    # it's no use if it can't do anything
    if pkmn1.hasFainted():
        return 0
    values = [evaluate(pkmn1, pkmn2, move) for move in range(len(pkmn1.moves))]
    result = max(values)
        
    return result
    
def averageAdvantage(pkmn1, team2):
    sum = 0
    n = 0
    for pokemon in team2.pokemon:
        if not pokemon.hasFainted():
            sum += advantage(pkmn1, pokemon)
            n += 1
    return (sum/n)
    
# best pokemon to swap into this opponent
def bestToSwapIn(team, oppoTeam):
    opponent = oppoTeam.currentPokemon
    thisPokemon = team.currentPokemon
    values = [[advantage(team[i], opponent) - .3*advantage(thisPokemon, opponent)\
    - costToSwap(thisPokemon, team[i], opponent) - \
    costOfBoosts(thisPokemon, opponent), i] for i in range(team.len())]
    values.sort()
    
    # more desperate to swap if you can be one shotted and you're valuable
    shape = opponent.hitsNeeded(team.currentPokemon)+.4
    pokemon = thisPokemon.copy()
    pokemon.removeBoosts()
    return [values[-1][0]+averageAdvantage(pokemon, oppoTeam)/shape**2,\
     values[-1][1]]
    
    
# sees how well pkmn1 can stall pkmn2
def stall(pkmn1, pkmn2):
    # OHKOs and 2HKOs cannot be stalled
    pkmn2.hitsNeeded(pkmn1) - 2
    
# how good a counter is pkmn1 for pkmn2
def evalPkmn(pkmn1, pkmn2):
    pass
    
    
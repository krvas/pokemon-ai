import random
import copy
from MoveClass import *
from TypeClass import *
## Instructions on how to use
"""
    you can make a list of §700 Species
    a Pokemon is an instance of the species
    you can build a set on that Pokemon
    
"""

## database reading functions



# read and write taken from 112 site
def readFile(filename):
    with open('files/'+filename, 'r') as file:
        return file.read()
        
def getPokemonName(id):
    s = readFile('pokemon_by_number.txt')
    lst = s.splitlines()
    listOfPokemon = {}
    for elt in lst:
        listOfPokemon[int(elt.split()[0])] = elt.split()[1]
    if id == 'all':
        return {listOfPokemon[i].upper():listOfPokemon[i]\
         for i in listOfPokemon}
    result = listOfPokemon[id]
    #result = result.replace(str(id), '')
    return result.strip()
    
def getPokemonTyping(id):
    s = readFile('stats_and_typing2.txt')
    listOfPokemon = s.splitlines()
    list2dOfPokemon = []
    for s in listOfPokemon:
        list2dOfPokemon.append(convertToIntList(s.split(',')))
    index = binarySearch2d(list2dOfPokemon, id)
    pokemonData = list2dOfPokemon[index]
    typing = pokemonData[2]
    return Typing(typing.split())
    
def getPokemonBaseStats(id):
    s = readFile('stats_and_typing2.txt')
    listOfPokemon = s.splitlines()
    list2dOfPokemon = []
    for s in listOfPokemon:
        list2dOfPokemon.append(convertToIntList(s.split(',')))
    index = binarySearch2d(list2dOfPokemon, id)
    pokemonData = list2dOfPokemon[index]
    base = pokemonData[3]
    return convertToIntList(base.split())
    
# linear searches through all the pokemon to get the pokedex number
# maybe later I could change it to binary
def getPokedexID(name):
    name = capitalize(name)
    s = readFile('pokemon_by_name.txt')
    for line in s.splitlines():
        if line.startswith(name):
            pokedexNo = line.replace(name, '').strip()
            return int(pokedexNo)
            
def getMovesFromEssentialsDB():
    movesList = getMovesHelper('movesList.txt', False)
    tags = ['ID', 'IntlName', 'name', 'functionCode', 'power', 'type',\
            'kind', 'accuracy', 'TotalPP', 'effectChance', 'target',\
            'priority', 'flags', 'description']
    types = [int, str, str, str, int, Type, str, int, int, int, int, \
             int, str, str]
    
    actualMoves = {}
    for move in movesList:
        moveDict = {}
        for i in range(len(tags)):
            moveDict[tags[i]] = types[i](move[i])
        actualMoves[moveDict['IntlName']] = complexMoveMaker(moveDict)
    return actualMoves
        
def complexMoveMaker(dictionary):
    '''
    # to correct certain things which the essentails DB handles in other ways
    codes = set()
    if dictionary['functionCode'] in codes:
        dictionary['effectChance'] = 100
    '''
    garbage = ['a', 'normal', -1,-1, 'p']
    move = Move(*garbage)
    move.setParameters(dictionary)
    return move
    
def getMoves():
    movesList = getMovesHelper('movesList.txt')
    actualMoves = {}
    for move in movesList:
        if 'n' in move: #i.e. if it's a non damaging move
            actualMoves[move[0]] = nonDamagingMove(*move)
        else:
            actualMoves[move[0]] = Move(*move)
    return actualMoves
    
def getMovesHelper(filename, convert=True):
    s = readFile(filename)
    L = s.splitlines()
    moveData = []
    for elt in L:
        if convert:
            moveData.append(convertToIntList(elt.split(',')))
        else:
            moveData.append(elt.split(','))
    return moveData
    
def getViableMoves():
    s = readFile('showdownData.txt')
    # in showdown it shows which moves are viable and which ones aren't
    brac = 0
    move = None
    viables = set()
    for line in s.splitlines():
        newLine = ''
        brac += line.count('{') - line.count('}')
        
        if line.strip() == 'isViable: true,':
            viables.add(move)
        
        for elt in line.split():
            
            if elt != '{':
                move = elt[1:-2].upper()
    return viables
    
## Helper functions

# takes a string and capitalizes all the first letters
def capitalize(s):
    newS = ''
    for word in s.split():
        newWord = word[0].upper() + word[1:].lower()
        newS += newWord
    return newS

def convertToDict(L1, L2):
    result = {}
    for i in range(len(L1)):
        result[L1[i]] = L2[i]
    return result
    
def binarySearch2d(L, elt):
    lo = 0
    hi = len(L)
    mid = None
    while lo < hi:
        lastMid = mid
        mid = (lo+hi)//2
        if lastMid == mid: break
        thisElt = L[mid]
        if thisElt[0] == elt:
            return mid
        elif thisElt[0] > elt:
            hi = mid
        else:
            lo = mid
    return None
    
def testBinarySearch2d():
    print('Testing binarySearch2d()...', end='')
    L = [[i] for i in range(100)]
    for i in range(len(L)):
        assert(binarySearch2d(L, i) == i)
    L = [[5], [8, None, True], [10, 'hello'], [34, 204], [56, 49]]
    assert(binarySearch2d(L, 3) == None)
    assert(binarySearch2d(L, 49) == None)
    assert(binarySearch2d(L, 8) == 1)
    assert(binarySearch2d(L, 56) == 4)
    print('Passed!')
        
# removes spaces from a string
def removeSpace(s):
    result = ''
    for c in s:
        if c not in {' ', '-'}:
            result += c
    return result
    
# returns the words within the first brackets
def getBracketed(s):
    bracketFound = False
    newS = ''
    for c in s:
        if c == '(':
            bracketFound = True
        elif c == ')':
            break
        elif bracketFound:
            newS += c
    return newS

def debugger(f):
    def g(*args):
        result = f(*args)
        print(result)
        return result
    return g

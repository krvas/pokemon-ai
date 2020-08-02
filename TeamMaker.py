
'''
TeamMaker.py

Manages reading .txt files to make teams
And writing .txt files when the user wants to make a team

'''

import string
from TeamClass import *
from dataFormat import *
from PokemonClass import *

# my attempt at making a file reader
# which is compatible with most formats of pokemon teams
def readTeam(name, pkmnNames, allMoves):
    team = Team([None])
    contents = readFile('teams/%s.txt' % name)
    
    for line in contents.splitlines():
        line2 = ''
        if '@' in line:
            line = line[:line.find('@')-1]
        if line.endswith(')'):
            line2 = getBracketed(line)
            line = line[:line.find('(')]
        if len(line) > 2:
            lineKey = removeSpace(line[2:]).upper()
        line = line.strip()
        
        if line.upper() in pkmnNames:
            team.pokemon.append(Pokemon(line))
        elif line2.upper() in pkmnNames:
            team.pokemon.append(Pokemon(line2))
        elif len(line) > 0 and line[0] in string.punctuation \
        and lineKey in allMoves:
            team[-1].addMove(allMoves[lineKey])
        elif line.startswith('EV'):
            try:
                line = line[line.index(':')+1:].strip()
                lineList = line.split('/')
                for EV in lineList:
                    numeral, type = EV.split()
                    if type.isdigit():
                        type, numeral = numeral, type
                    type = convertType(type)
                    team.pokemon[-1].EV[type] = int(numeral)
            except: pass
    if team[0] == None:
        team.removeNone()
    
    return team
    
def writeTeam(filename, team):
    filename = 'files/teams/%s.txt' % filename
    
    with open(filename, 'w') as file:
        for pokemon in team.pokemon:
            if pokemon == None: continue
            file.write(pokemon.name+'\n')
            
            EVLine = 'EVs: '
            for key in pokemon.EV:
                if pokemon.EV != 0:
                    EVLine += key +' '+ str(pokemon.EV[key])+'/'
            file.write(EVLine[:-1]+'\n')
            for move in pokemon.moves:
                file.write('- '+move.name+'\n')
            file.write('\n') # blank line to end the pokemon data

def convertType(s):
    # the only cases differentiated by case
    if s in ['spD','SpD', 'Spd', 'spd']:
        return s[0].lower() + s[1:]
    s = s.lower()
    if s in ['atk', 'attack']:
        return 'atk'
    elif s in ['spa', 'satk']:
        return 'spA'
    elif s in ['spe', ]:
        return 'spd'
    elif s in ['hp']:
        return 'HP'
    elif s in ['def']:
        return 'def'
    elif s in ['sdef']:
        return 'spD'
    
    return None
        
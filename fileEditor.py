# check out reinforcement learning

'''
fileEditor.py

Used for creating / editing files in a readable format
'''

from dataFormat import *
import os
import jiphy

def cutNonOU():
    filename = 'files/moves.txt'
    L = []
    wantedMoves = set()
    wantedCodes = {'000', '001', '002', '003', '005', '006', '007', '00A', \
    '00C', '00D', '01C', '01F', '024', '025', '027', '028', '029',
    '018', '019', '020', '026', '02B', '02C', '02D', '02E', '032', \
    '035', '036', '039', '03C', '03B', '03C', '03D', '03E', '06E', \
    '03F', '045', '046', '06C', '06D', '075', '076', '07B', '07F',\
    '086', '089', '08D', '0AA', '0A5' '0A9',  \
    '0D5', '0D6', '0D8', '0DD', '10A', '122', '00F', 
    '043', '07E'}
    # 0EE - maybe, but not for now
    # later add hazard related stuff: 049, 0A2, 0A3, 0BA, 0EB, 0EC, 103/4/5
    s = readFile('moves.txt')
    for line in s.splitlines():
        # logic here!
        lineList = line.split(',')
        if lineList[1] in wantedMoves or lineList[3] in wantedCodes:
            L.append(line)
    with open('files/movesList.txt', 'w') as file:
        file.write('\n'.join(L))
cutNonOU()
    
def cutFromString(s):
    L = []
    wantedMoves = set()
    wantedCodes = {'000', '002', '003', '005', '006', '007', '00A', '00F', \
    '012', '013', '019', '020', '026', '02B', '02C', '02E', '039', '03C', \
    '03F', '045', '046', '06D', '075', '076', '086', '08D', '090', '0AA', \
    '0D5', '0D6', '0D8', '0DC', '0EE', '0FA', '0FB', '0FE', }
    # later add hazard related stuff: 049, 0A2, 0A3, 0BA, 0EB, 0EC, 103/4/5
    for line in s.splitlines():
        # logic here!
        lineList = line.split(',')
        if lineList[1] in wantedMoves or lineList[3] in wantedCodes:
            L.append(lineList)
    newS = ''
    for elt in L:
        newS += ','.join(elt).replace('Pokémon', 'Pokemon') + '\n'
    
    with open('movesList.txt', 'w') as file:
        file.write(newS)
        
def getLegals(s):
    # remove NFEs
    
    newList = []
    for element in s.split('#-------------------------------'):
        if element == '': continue
        elt = element.splitlines()
        if elt[-1] == 'Evolutions=':
            newList.append(int(elt[1][1:-1]))
        
    return set(newList)
        
def editPokemon(s):
    filename = 'stats_and_typing.txt'
    data = ''
    legal = getLegals(s)
    with open(filename, 'r') as file:
        line = file.readline()
        for i in range(2000):
            try:
                if int(line.split(',')[0]) in legal:
                    data += line
                line = file.readline()
            except:
                break
    
    with open('stats_and_typing2.txt', 'w') as file:
        file.write(data)
        
def makeAllLegal():
    s = readFile('stats_and_typing2.txt')
    legals = s.splitlines()
    legalID = set()
    legalName = set()
    for i in range(len(legals)):
        legalID.add(legals[i].split(',')[0]+'.png')
        legalName.add(legals[i].split(',')[1])
    
    files = os.listdir('images/icons/')
    outFiles = []
    for file in files:
        if file not in legalID and not os.path.isdir(file):
            os.remove('images/icons/'+file)

def editMovesJS():
    s = readFile('moves.js')
    convert = False
    fn = ''
    newS = ''
    brac = 1
    
    for line in s.splitlines():
        
        if 'function' in line: 
            convert = True
            brac = 1
        
        if convert:
            brac += line.count('{') - line.count('}')
            fn += line+'\n'
        else:
            newS += line + '\n'
        if brac <= 0:
            convert = False
            newS += jiphy.to.python(fn)
            fn = ''
            
    with open('newMoves.txt', 'w') as file:
        file.write(newS)
            
            
def editMovesAgainJS():
    s = readFile('newMoves.txt')
    convert = False
    fn = ''
    newS = ''
    brac = 0
    i=0
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
    #with open('newMoves.txt', 'w') as file:
    #    file.write(newS)
        
#editMovesAgainJS()


def getLearnset():
    s = readFile('learnsets.js')
    newS = ''
    i = 0
    for line in s.splitlines():
        newLine = ''
        for word in line.split():
            if word[0].isalpha() and word[-1]==':':
                newLine += '"'+word[:-1].upper()+'": '
            else:
                newLine += word + ' '
        if i < 50:
            print(newLine)
            i += 1
        newS += newLine + '\n'
    
    with open('learnsets.py', 'w') as file:
        file.write(newS)
#getLearnset()
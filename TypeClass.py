
## Helper functions
# gets the type chart data from a file
def typeChart():
    typeChart = []
    with open('files/type_chart.txt', 'r') as file:
        contents = file.read()
        
        for line in contents.splitlines():
            if line.startswith('#ignore_rest'):
                break
            listOfNos = convertToIntList(line.split())
            typeChart.append(listOfNos)
    return typeChart

def type_id(type):
    ids = {'normal':0, 'fire':1, 'water':2, 
           'electric':3, 'grass':4, 'ice':5,
           'fighting':6, 'poison':7, 'ground':8,
           'flying':9, 'psychic':10, 'bug':11,
           'rock':12, 'ghost':13, 'dragon':14,
           'dark':15, 'steel':16, 'fairy':17}
    return ids.get(type)
    
# takes a list of strings
# and casts the elements into ints
def convertToIntList(L):
    newL = []
    for elt in L:
        if elt.isdigit():
            newL.append(int(elt))
        else:
            newL.append(elt)
    return newL

## Classes

class Type(object):
    ## Standard methods
    def __init__(self, type):
        type = type.lower()
        self.type = type
        self.id = type_id(type)
    
    def __repr__(self):
        return '<Type - '+self.type+'>'
        
    def __eq__(self, other):
        return isinstance(other, Type) and self.type == other.type
        
    ## Getter methods
    # the number which to multiply, when other attacks self
    def weaknessMultiplier(self, other):
        if isinstance(other, Type):
            other = other.type
        if not isinstance(other, str): 
            return 1
        result = typeChart()[type_id(other)][self.id]
        if result == 5: result /= 10
        return result


class Typing(object):
    ## Standard methods
    def __init__(self, types):
        self.types = []
        for type in types:
            self.types += [Type(type)]
            
    def __repr__(self):
        result = '<Typing - '+self.types[0].type
        for type in self.types[1:]:
            result += '/'+type.type
        result += '>'
        return result
        
    ## Getter methods
    def contains(self, type):
        return type in self.types
        
    # other attacks self
    def attackMultiplier(self, other):
        multiplier = 1
        for type in self.types:
            multiplier *= type.weaknessMultiplier(other)
        return multiplier
            
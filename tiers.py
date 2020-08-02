import requests
from bs4 import BeautifulSoup
import ast
from dataFormat import *

def scrape(name):
    url = 'http://www.smogon.com/dex/bw/pokemon/%s/' % name
    website = requests.get(url)
    source = website.text
    newS = ''
    for line in source.splitlines():
        
                i+=1
    #with open('files/tiers.txt', 'w') as file:
    #    file.write(newS)


def evalDict(dic, i):
    newDict = {}
    for elt in dic.split(','):
        try:newDict[elt.split(':')[0]] = elt.split(':')[1]
        except IndexError: pass
        
    try: return removeBracketsAndQuotes(newDict['"name"'])+' '+\
    replace(removeBracketsAndQuotes(newDict['"formats"']))
    except KeyError:pass
        
def removeBracketsAndQuotes(s):
    newS = ''
    for c in s:
        if c not in {'"', '[', ']', '{', '}'}:
            newS += c
    return newS
    
def replace(s):
    return s if s != '' else 'NFE'
    
print(scrape())
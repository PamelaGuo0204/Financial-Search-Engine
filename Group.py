#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import math
import numpy as np
import pickle
import json
from stemming.porter2 import stem
from xml.dom.minidom import parse
from collections import defaultdict
from scipy import sparse
#from app import tfidf,headline,onlyContent,allWordMap,headlineWordMap,contentWordMap

#Lab01 Function
def textTransformation(content):

    '''
    for i in punctuation:#Tokenization: Remove Punctuation
        if i in ['-','\'']:
            continue
        content = content.replace(i, '')
    '''
    #Tokenization: Remove Punctuation using Regular Expression
    content = re.sub("[^a-zA-Z0-9]"," ", content)
    
    #Normalization: Lowercase
    content = content.lower()
    
    #LoadMyOwnStopWords
    with open('englishST.txt') as f1:
        stopWord = f1.read()
        stopWord = stopWord.split()
    
    #String to List
    content = content.split()

    #Stopping: RemoveStopWords
    content = [word for word in content if not word in stopWord]
    
    ##Stemming
    for i in range(len(content)):
        content[i] = stem(content[i])
    
    #List to String
    content = (" ").join(content)
    
    '''If using packages
    content = remove_stopwords(content)
    #print(content)
    '''

    
    return content


#Preprocess the query in txt file into a query list
#Before: 'q9: "middle east" AND peace'
#After: ' "middle east" AND peace '
# def getBooleanQuery():
#     qlist = []
#     for line in open('./queries.boolean.txt'):
#         qlist.append(line.strip('\n'))#eat '\n'
#
#     for i in range(len(qlist)):
#         tmp = qlist[i].split(' ', 1)
#         qlist[i] = tmp[1]
#     return qlist
def getQuery(query):
    qlist = textTransformation(query)
    qlist = qlist.split(' ')
    return qlist

#Categorize the Query and return a type list
def typeQuery(qlist):
    typeList = []
    #1:Normal S, 2:Boolean S, 3:Phrase S, 
    #4:Proximity S, 5:Phr+B

    BooleanKey = ["AND", "OR", "NOT"]
    for x in qlist:
        BoolTag = 0
        if any(word in x for word in BooleanKey):
            BoolTag = 1
        if x[0] == '#':
            typeList.append(4)
        elif (BoolTag == 1 and x[0] == '"'):
            typeList.append(5)
        elif (BoolTag == 0 and x[0] == '"'):
            typeList.append(3)
        elif (BoolTag == 1):
            typeList.append(2)
        else:
            typeList.append(1)
    return typeList

#Simplest search with a word, ruturn a documentID set
def normalSearch(query, termIndex):
    query = textTransformation(query)
    doc = [x for x in list(termIndex[query].keys()) if x != 'fre']
    doc = set(doc)
    return doc

#For a simple word, return a doc set to calculate df.
def getDF(query, termIndex):#query already been preProcessed
    doc = [x for x in list(termIndex[query].keys()) if x != 'fre']
    doc = set(doc)
            
    return doc
    

#Boolean search between words and no phrases
def simpleBooleanSearch(query, termIndex):
    doc = set()
    BooleanKey = ["AND", "OR", "NOT"]
    
    #A set with all Doucument ID
    whole = set()
    for i in range(1, int(docCount)+1):
        whole.add(str(i))
    
    query = query.split(' ')
    while(len(query)):#非空就一直循环 当堆栈用
        currentSet = set()
        word = query[-1]#Search the last word in the list
        
        if word not in BooleanKey:#the word is a Boolean operator
            currentSet = normalSearch(word, termIndex)
            
            if len(query) > 1:#More than one word
                
                if query[-2] != 'NOT':#The word is positive
                    doc = doc | currentSet
                    query.pop()#Pop out the search word
                
                else:#The word is negative
                    doc = doc | (whole - currentSet)
                    query.pop()#Pop out the search word
                    query.pop()#Pop out the 'NOT' operator
        
        #the word is 'AND' operator
        elif word == 'AND':
            word = query[-2]
            currentSet = normalSearch(word, termIndex)
            doc = doc & currentSet#A交B
            query.pop()#Pop out the search word
            query.pop()#Pop out the 'AND' operator
        
        #the word is 'OR' operator
        elif word == 'OR':
            word = query[-2]
            currentSet = normalSearch(word, termIndex)
            doc = doc | currentSet#A并B
            query.pop()#Pop out the search word
            query.pop()#Pop out the 'OR' operator
            
    return doc

#Proximity Search between two words
def proximitySearch(query, termIndex):
    doc = set()
    temp = ''
    
    #eat punctuations
    query = list(query)
    for i in range(len(query)):
        if query[i] == '#':
            start = i+1
        elif query[i] == '(':
            firstStart = i+1
        elif query[i] == ',':
            comma = i-1
        elif query[i] == ')':
            secondEnd = i-1


    distance = int(temp.join(query[start : firstStart-1]))
    firstWord = temp.join(query[firstStart : comma+1])
    if(query[comma+2] == ' '):
        secondWord = temp.join(query[comma+3 : secondEnd+1])
    else:
        secondWord = temp.join(query[comma+2 : secondEnd+1])
    firstWord = textTransformation(firstWord)
    secondWord = textTransformation(secondWord)
    
    '''
    firstList = termIndex[firstWord][1:]
    secondList = termIndex[secondWord][1:]
    
    #the absolute delta should less than distance
    for x in firstList:
        for y in secondList:
            if x[0] == y[0]:
                if abs(y[1] - x[1]) <= distance:
                    doc.add(x[0])
    '''
    
    firstList = termIndex[firstWord]
    secondList = termIndex[secondWord]
    
    #the absolute delta should less than distance
    for x in firstList.keys():
        if x in secondList.keys() and x != 'fre':
            for firstPos in firstList[x]:
                for secondPos in secondList[x]:
                    if abs(secondPos - firstPos) <= distance:
                        doc.add(x)
    return doc

#Simple Phrase Search
def phraseSearch(query, termIndex):
    doc = set()
    
    #Process the query
    query = textTransformation(query)
    query = query.replace('"', '')
    terms = query.split()
    
    
    #Find all documents with any one of the terms.
    dictList = []
    for word in terms:
        dictList.append(termIndex[word])
     
    #Bug to be fix: 三元词组只满足前两词也会被计算在内     
    #筛选出符合条件的文档放入Set
    for i in range(0,len(terms)-1):
        for firstDocid in dictList[i].keys():#词组的每个词的位置都在后一词的前面1位, x is docID
            if firstDocid in dictList[i+1].keys() and firstDocid != 'fre':
                
                for xpos in dictList[i][firstDocid]:
                    for ypos in dictList[i+1][firstDocid]:
                        if xpos - ypos == -1:
                            doc.add(firstDocid)
                
                '''
                if x[1] - y[1] == -1:
                    doc.add(x[0])'''
                    
                    #Bug to be fix: 三元词组只满足前两词也会被计算在内    
                    #else:
                     #   if x[0] in doc:
                      #      doc.remove(x[0])
    return doc

#Boolean Search with phrases and words
def phraseBooleanSearch(query, termIndex):
    doc = set()
    operation = None
    
    for word in re.split(" +(AND|OR) +",query):
        opposite = 0#Will be 1 if ’NOT‘ appears
        
        if word in ['AND','OR']:
            operation=word
            continue
        
        if word.find('NOT ') == 0:
            if operation == 'OR':
                print("Error Query!")#Illegal query.
            
            opposite = 1
            realWord = word[4:]
        else:
            realWord = word
            
        #Phrase search or normal search
        if realWord[0] == '"':
            currentDoc = phraseSearch(word, termIndex)
        else:
            currentDoc = normalSearch(word, termIndex)
        
        #Find the document set
        if operation != None:
        # now we need to match the key and the filenames it contains:
            
            if operation == 'AND':
                if opposite == 1:
                    doc -= currentDoc#A交B
                else:
                    doc &= currentDoc#A
            elif operation == 'OR':
                doc |= currentDoc#A并B
        
        else:
            doc |= currentDoc
        operation=None
        
    
    return doc

def Search(query,typ):
    
    
    if typ == 1:#Normal Search
        doc = normalSearch(query,termIndex)
    elif typ == 2:#Boolean Search
        doc = simpleBooleanSearch(query, termIndex)
    elif typ == 3:#Phrase Search
        doc = phraseSearch(query, termIndex)
    elif typ == 4:#Proximity Search
        doc = proximitySearch(query, termIndex)
    elif typ == 5:#Phrase + Boolean Search
        doc = phraseBooleanSearch(query, termIndex)
    
    return doc#doc is a documentID set


# def getTFIDFQuery():
#     qlist = []
#     for line in open('./queries.ranked.txt'):
#         qlist.append(line.strip('\n'))#eat '\n'
#
#     for i in range(len(qlist)):
#         qlist[i] = textTransformation(qlist[i][2:])#eat query index and space
#     return qlist

#get the query from the web
#input: a query from the web
#output: preprocessed query
def getTFIDFQuery(query):
    qlist = textTransformation(query)
    return qlist


def getTFIDFvalue(term, DocID, currentIndex, df, docCount):
    score = 0
    #del currentIndex['fre']
    
    count = 0#'tf(t,d)':how many times in this document
    if DocID in currentIndex:
        count = len(currentIndex[DocID])
    if count:
        score =  1 + math.log10(count)
        score *= math.log10(docCount/df)
        
    return score
'''
def TFIDFSearch(query, termIndex,docCount):
    termList = query.split()
    scoreDict = {}
    #对每个term求值，用np矩阵
    docSet = set()
    for x in termList:
        docSet |= normalSearch(x, termIndex)
        
    for ID in docSet:
        scoreDict[ID] = 0
        for term in termList:
            currentIndex = termIndex[term]
            
            df = termIndex[term]['fre']
            scoreDict[ID] += getTFIDFvalue(term, ID, currentIndex, df, docCount)
    
    ansList = sorted(scoreDict.items(), key=lambda v: v[1], reverse = True) 
    ansList.sort(key = lambda x: (-x[1], int(x[0])))
    return ansList
''' 
#!!!!!!!!TermID范围为1~311648，实际为311648词，但tfidf矩阵第一行全0，实际不用操作
def getExistDoc(termID, tfidfDict):
    doc = set()
    for (x,y) in tfidfDict.keys():
        if x == termID:
            doc.add(y)
    return doc
    
    
def TFIDFSearch(query, tfidf, docCount, searchType):
    if searchType == 0:
        wordMap = allWordMap
    elif searchType == 1:
        wordMap = headlineWordMap
    elif searchType == 2:
        wordMap = contentWordMap
    termList = query.split()
    termIDList = [wordMap[word] for word in termList]#Term id list
    scoreDict = {}
    #对每个term求值，用np矩阵
    
    docSet = set()
    for termID in termIDList:
        docSet |= getExistDoc(termID, tfidf)
        
    for ID in docSet:
        scoreDict[ID] = 0
        for termID in termIDList:
            scoreDict[ID] += tfidf[(termID,ID)]
    
    ansList = sorted(scoreDict.items(), key=lambda v: v[1], reverse = True) 
    ansList.sort(key = lambda x: (-x[1], int(x[0])))
    return ansList
    
#output the tfidf search result
#input:a query on the web
#output: a list of docids
def output(query):
    result = []
    docCount = 447310
    '''
    with open('./index.json', 'r') as load_f:
        termIndex = json.load(load_f)
    '''

    query = getTFIDFQuery(query)#规范化
    
    ansList = TFIDFSearch(query, tfidf, docCount, 0)#是一个tuple list (DocID, score)
    
    #输出result
    count = 0
    for item in ansList:
        result.append(str(item[0]))
        count = count + 1
        if count > 150:
            break
            
    print("sucessfully search!")
    # print(result)
    return result

def outputHeadline(query):
    result = []
    docCount = 447310
    '''
    with open('./index.json', 'r') as load_f:
        termIndex = json.load(load_f)
    '''

    query = getTFIDFQuery(query)#规范化
    
    ansList = TFIDFSearch(query, headline, docCount, 1)#是一个tuple list (DocID, score)
    
    #输出result
    count = 0
    for item in ansList:
        result.append(str(item[0]))
        count = count + 1
        if count > 150:
            break
            
    print("sucessfully search!")
    # print(result)
    return result

def outputContent(query):
    result = []
    docCount = 447310
    '''
    with open('./index.json', 'r') as load_f:
        termIndex = json.load(load_f)
    '''

    query = getTFIDFQuery(query)#规范化
    
    ansList = TFIDFSearch(query, onlyContent, docCount, 2)#是一个tuple list (DocID, score)
    
    #输出result
    count = 0
    for item in ansList:
        result.append(str(item[0]))
        count = count + 1
        if count > 150:
            break
            
    print("sucessfully search!")
    # print(result)
    return result

# 以下代码在程序初始化时载入内存
'''
tfidf = sparse.load_npz('CompressedTFIDFMatrix.npz').toarray()
headline = sparse.load_npz('CompressedHeadlineMatrix.npz').toarray()
onlyContent = sparse.load_npz('CompressedContentMatrix.npz').toarray()
'''
f = open("tfidfDict.pkl", "rb")
tfidf = pickle.load(f)
print("tfidf successfully")
f = open("headlineDict.pkl", "rb")
headline = pickle.load(f)
print("headline successfully")
f = open("contentDict.pkl", "rb")
onlyContent = pickle.load(f)
print("content successfully")

f = open("allWordMap.pkl", "rb")
allWordMap = pickle.load(f)
f = open("headlineWordMap.pkl", "rb")
headlineWordMap = pickle.load(f)
f = open("contentWordMap.pkl", "rb")
contentWordMap = pickle.load(f)

#output("bank")
# outputHeadline("bank")
# outputContent("bank")

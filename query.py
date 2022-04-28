from os import listdir, path
from bs4 import BeautifulSoup
from collections import defaultdict
from math import log10, sqrt
import heapq
import re
import sys
import bisect

def getTop10TermsPerDoc(numDoc):
    TOP10_FILE = "top_tfidf.txt"
    with open(TOP10_FILE, "r") as best10File:
        allLines = best10File.readlines()
        curLine = allLines[numDoc-1].split()
        print("Top 10 tf*idf terms in document " + str(numDoc) + ".html: ")
        for i in range(0,len(curLine),2):
            print(curLine[i] + " " + str(curLine[i+1]))
        print()

def calcWithWeight(queryWords):
    #print(queryWords)
    STOP_FILE = "stopWords.txt"
    POSTING_FILE = "postingFile.txt"

    stopTbl = {}
    filtered_words = []
    postingLists = defaultdict(list)
    NUMDOC = 503
    
    #get all stop words:
    with open(STOP_FILE, "r") as stopFile:
        all_stop_words = stopFile.readlines()
        for word in all_stop_words:
            newStr = word.rstrip()
            stopTbl[newStr] = 0
    
    #Downcase and remove stop words from query 
    for word in queryWords:
        curWord = word.lower()
        if curWord not in stopTbl:
            filtered_words.append(curWord)
    #print(filtered_words)
    #Load posting list from disk (after indexing) into main memory. Each word would contain a list of
    #(file number, tf*idf in that file)
    with open(POSTING_FILE, "r") as postingFile:
        allLines = postingFile.readlines()
        for line in allLines:

            arr = line.split()
            for i in range(1,len(arr),2):
                postingLists[arr[0]].append((arr[i],float(arr[i+1])))

    #Modify for weighted query
    wordsToWeight = {}
    sumSqrtQuery = 0
    for i in range(0,len(filtered_words),2):
        curWeight = float(filtered_words[i])
        wordsToWeight[filtered_words[i+1]] = curWeight
        sumSqrtQuery += curWeight ** 2

    #print(wordsToWeight)
    sumSqrtQuery = sqrt(sumSqrtQuery)

    #Term-at-a-time method
    numerator = [0] * (NUMDOC + 1)  
    denominator = [0] * (NUMDOC + 1)
    similarity = []
    
    for word in filtered_words:
        if word in postingLists:
            for fileNum, tfidf in postingLists[word]:
    #            print(fileNum, tfidf)
                numerator[int(fileNum)] += wordsToWeight[word] * tfidf
                denominator[int(fileNum)] += tfidf ** 2
    
    for fileNum in range(len(denominator)):
        denominator[fileNum] = sqrt(denominator[fileNum])*sumSqrtQuery
    #print(numerator)
    #Put all file along with their tfidf into a heap. Then keep popping until get 10 docs or 0 similarity, 
    #whichever comes first
    for fileNum in range(len(numerator)):
        if numerator[fileNum] == 0 or denominator[fileNum] == 0:
            continue
        #Put negative value of similarity into the heap to simulate a max heap
        similarity.append((-float(numerator[fileNum] / denominator[fileNum]), fileNum))
    
    heapq.heapify(similarity)
    #Print out result
    countFiles = 0
    res = []
    while similarity and countFiles < 10:
        cur = heapq.heappop(similarity)
        res.append((cur[1], round(-cur[0],8)))
        countFiles += 1
    
    return res

def calcWithoutWeight(queryWords):
    STOP_FILE = "stopWords.txt"
    POSTING_FILE = "postingFile.txt"
    stopTbl = {}
    filtered_words = []
    postingLists = defaultdict(list)
    NUMDOC = 503
    
    #get all stop words:
    with open(STOP_FILE, "r") as stopFile:
        all_stop_words = stopFile.readlines()
        for word in all_stop_words:
            newStr = word.rstrip()
            stopTbl[newStr] = 0
    
    #Downcase and remove stop words from query 
    for word in queryWords:
        curWord = word.lower()
        if curWord not in stopTbl:
            filtered_words.append(curWord)
    
    #Load posting list from disk (after indexing) into main memory. Each word would contain a list of
    #(file number, tf*idf in that file)
    with open(POSTING_FILE, "r") as postingFile:
        allLines = postingFile.readlines()
        for line in allLines:

            arr = line.split()
            for i in range(1,len(arr),2):
                postingLists[arr[0]].append((arr[i],float(arr[i+1])))

    sumSqrtQuery = 0
    for word in filtered_words:
        #TODO: modify weight later
        sumSqrtQuery += 1 * 1
    #    print(postingLists[word])
    sumSqrtQuery = sqrt(sumSqrtQuery)

    #Term-at-a-time method
    numerator = [0] * (NUMDOC + 1)  
    denominator = [0] * (NUMDOC + 1)
    similarity = []
    
    for word in filtered_words:
        if word in postingLists:
            for fileNum, tfidf in postingLists[word]:
                #print(fileNum, tfidf)
                numerator[int(fileNum)] += 1 * tfidf
                denominator[int(fileNum)] += 1 * tfidf ** 2
    
    for fileNum in range(len(denominator)):
        denominator[fileNum] = sqrt(denominator[fileNum])*sumSqrtQuery
    #Put all file along with their tfidf into a heap. Then keep popping until get 10 docs or 0 similarity, 
    #whichever comes first
    for fileNum in range(len(numerator)):
        if numerator[fileNum] == 0 or denominator[fileNum] == 0:
            continue
        #Put negative value of similarity into the heap to simulate a max heap
        similarity.append((-float(numerator[fileNum] / denominator[fileNum]), fileNum))
    
    heapq.heapify(similarity)
    #Print out result
    countFiles = 0
    res = []
    
    while similarity and countFiles < 10:
        cur = heapq.heappop(similarity)
    #    print("Cur is: " + str(cur))
        res.append((cur[1], round(-cur[0],8)))
        countFiles += 1
    
    return res

if __name__ == "__main__":
    res = []
    if sys.argv[1] == "Wt":
        print('Calc with weight')
        res = calcWithWeight(sys.argv[2:])
    else:
        print('Calc without weight')
        res = calcWithoutWeight(sys.argv) 
    print("Done processing query!")

    #print(res)
    if res:
        for fileNum, valSim in res:
            print(str(fileNum) + ".html " + str(valSim) + "\n")
        
        for fileNum, valSim in res:
            #Print top 10 tf*idf
            getTop10TermsPerDoc(fileNum)
    else:
        print("No document matches the given query")
from os import listdir, path
from bs4 import BeautifulSoup
from collections import defaultdict
from math import log10
import re
import sys
import time
import heapq

def main(input_dir: str, output_dir: str, numDocs):
    #t2_start = time.perf_counter_ns()
    # cummulative_time1 = [0]
    # cummulative_time2 = [0]
    start_elapsed = time.process_time_ns()
    start_CPU = time.perf_counter_ns()

    INPUT_DIR = input_dir
    OUTPUT_DIR = output_dir
    OUTPUT_FILE1 = "finalResults.txt"
    STOP_FILE = "stopWords.txt"
    NUM_DOCS_INDEX = numDocs

    #Hash table to count total occurrences of a word in the entire corpus
    countTbl = defaultdict(int)
    #Hash table that contains stop words
    stopTbl = {}
    #Hash table to count number of documents a word is in
    numDocsIn = defaultdict(int)
    #Hash table with inverted index
    mainTbl = defaultdict(dict)

    #get all stop words:
    with open(STOP_FILE, "r") as stopFile:
        all_stop_words = stopFile.readlines()
        for word in all_stop_words:
            newStr = word.rstrip()
            stopTbl[newStr] = 0

    #Get all input files
    input_files = listdir(INPUT_DIR)
    output_files = [str(i+1) + ".txt" for i in range(NUM_DOCS_INDEX)]
    for i in range(NUM_DOCS_INDEX):
        # t1_start = time.process_time_ns()
        # t2_start = time.perf_counter_ns()
        #For each input document, count each word's occurrences along with total number of words
        curDocCount = defaultdict(int)
        total_words = 0

        cur_path = path.join(INPUT_DIR, input_files[i])
        output_path = path.join(OUTPUT_DIR, output_files[i])
        #print(cur_path)
        with open(cur_path, 'rb') as htmlFile:
            soup = BeautifulSoup(htmlFile, features="html.parser")
            res_str = soup.get_text()
            res_arr = re.findall(r'[^\W\d_]+',res_str)

            for word in res_arr:
                lowWord = word.lower()
                #Make sure word is not a stop word and word's length is > 1
                if lowWord not in stopTbl:
                    curDocCount[lowWord] += 1
                    total_words += 1
                    countTbl[lowWord] += 1
                    
            #Keep track of number of docs a word is in:
            for word in curDocCount:
                numDocsIn[word] += 1
                #add Term Frequency (TF) to Inverted Index Table
                mainTbl[word][i+1] = curDocCount[word] / total_words
            #    outFile.write(word + " " + str(curDocCount[word] / total_words) + '\n')
            with open(output_path, "w") as outFile:
                outFile.write("Total number of words: " + str(total_words) + "\n")

        # t1_end = time.process_time_ns()
        # cummulative_time1.append(t1_end - t1_start + cummulative_time1[-1])

    numDocs = len(input_files)
    for doc in range(1,NUM_DOCS_INDEX+1):
        # t1_start = time.process_time_ns()

        output_path = path.join(OUTPUT_DIR, output_files[doc-1])
        with open(output_path, "a") as outFile:
            for word in mainTbl:
                #Ignore words that occur only once in the entire corpus
                if countTbl[word] == 1:
                    continue
                if doc in mainTbl[word]:
                    #TODO
                    #cur_idf = log10(numDocs/numDocsIn[word])
                    cur_idf = numDocs/numDocsIn[word]
                    #Calculate TF-IDF of every word in Inverted Index Table 
                    mainTbl[word][doc] *= cur_idf
                    #write tokens and their weights to according files
                    outFile.write(word + " " + str(round(mainTbl[word][doc],5)))
                    outFile.write("\n")

        # t1_end = time.process_time_ns()
        # cummulative_time2.append(t1_end - t1_start + cummulative_time2[-1])
    
    #Add-ons from Phase 4: Calculate top 10 tf*idf terms per document
    with open("top_tfidf.txt", "a") as best10File:
        for doc in range(1,NUM_DOCS_INDEX+1):
            output_path = path.join(OUTPUT_DIR, output_files[doc-1])
            heap = []
            with open(output_path, "r") as outFile:
                allLines = outFile.readlines()
                for i in range(1,len(allLines)):
                    w, weight = allLines[i].split()
                    heap.append((-float(weight),w))
            
            heapq.heapify(heap)
            countEle = 0
            while heap and countEle < 10:
                weight, w = heapq.heappop(heap)
                best10File.write(str(w) + " " + str(-weight) + " ")
                countEle += 1
            best10File.write("\n")

    #Phase 3: Build Dictionary and Posting File
    DICTIONARY_FILE = "dictionaryRecords.txt"
    POSTING_FILE = "postingFile.txt"
    with open(DICTIONARY_FILE, "w") as dictFile:
        for word in mainTbl:
            if countTbl[word] == 1:
                continue
            firstDoc = next(iter(mainTbl[word]))
            dictFile.write(word + " " + str(numDocsIn[word]) + " " + str(firstDoc) + "\n")

    #Modify this one a little bit to get tf-idf better
    with open(POSTING_FILE, "w") as postFile:
        for word in mainTbl:
            if countTbl[word] == 1:
                continue
            postFile.write(word + " ")
            for entry in mainTbl[word]:
                postFile.write(str(entry) + " " + str(round(mainTbl[word][entry],8)) + " ")
            postFile.write("\n")

    end_elapsed = time.process_time_ns()
    end_CPU = time.perf_counter_ns()
    return [end_elapsed - start_elapsed, end_CPU - start_CPU]
if __name__ == "__main__":
    # for i in range(20,503,20):
        # elapse_time, cpu_time = main(sys.argv[1], sys.argv[2], i)  
        # print("Num docs: " + str(i))
        # print("Elapsed Time: " + str(elapse_time))
        # print("CPU Time: " + str(cpu_time))
    elapse_time, cpu_time = main(sys.argv[1], sys.argv[2], 503) 
    print("Elapsed Time: " + str(elapse_time))
    print("CPU Time: " + str(cpu_time))
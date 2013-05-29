# This program tokenizes a file into sentences using an abbreviation list and a rule-based approach
# Customized for the Isaac Newton corpus which contains a mixture of English, Latin, and Frech, many non-English abbreviations, and a number of irregularities

import sys, re

detect_abbr = re.compile(r"((( |^)((([^\s]+\.|etc)( |$)+){2,}|([Pp](ag)?|[Cc]h|[Tt]h|[Vv](ol)?|ib|et|in)\.?( |$)+)+([0-9]+\.?,? *)*)+|i\. +e\.)") # any sequence of 2 or more words ending in a period or one of a short list of section abbreviaions (e.g. page, chapter, etc.) optionally followed by a number  

# load a file and strip off return characters from the end of each line
def load_file(filename):
    ifile = open(filename,'r')
    currentfile = ifile.readlines()
    for i,line in enumerate(currentfile):
        currentfile[i] = line.strip()
    ifile.close()

    return currentfile

# check a word against a list of abbreviations
def check_abbr(abbrlist,word):
    if word in abbrlist:
        return True
    else:
        return False

# recursive search for sequences of abbreviations splitting the line each time one is found 
def revise_line(newline,line):
    current = detect_abbr.search(line)
    if current: #sequence is found
        if current.start() > 0:
            temp = line[:current.start()].split()
            for word in temp:
                newline.append(word.strip())
        currentseq = re.sub("\s+"," ",current.group())+ "###" #regularize whitespace and add end of phrase marker '###'
        newline.append(currentseq.strip())
        revise_line(newline,line[current.end():]) #if sequence is found at the begining of the line, split and check the rest of the line
    else: # termination condition, sequence is not found, append the line
        if len(line) > 0:
            temp = line.split()
            for word in temp:
                newline.append(word.strip())    
    return newline


# segment the file into sentences using the abbreviation list
def segment_sent(essay):
    currentline = []
    sentences = []
    abbrlist = load_file("abbr_list.txt")
    for line in essay:
        newline = []
        line = re.sub(" +\.",".",line)
        revisedline = revise_line(newline,line)
        if len(revisedline) > 0:
            for word in revisedline:
                word = word.strip()
                if re.search("###$",word):
                   if re.search("p(ag)?\.? +([0-9]+,? *)+\. *###",word): # look for page numbers and remove marker
                       word = word[:-3].strip()
                       currentline.append(word)
                   else: #other sequences of abbreviations
                       currentline.append(word[:-3].strip())
                else: 
                    currentline.append(word)
                if re.search("\.$",word):
                    if not (check_abbr(abbrlist,word) or check_abbr(abbrlist,word[:-1])): # the word is not in the abbreviation list with or without a final period
                        if re.search("^[0-9]*\.?$", currentline[-1]) and len(currentline) > 1 and not re.search("(,$|^p(ag)?$)", currentline[-2]) and not (currentline[-1][:-1].isdigit() and currentline[-2].isdigit() and not (int(currentline[-1][:-1]) - int(currentline[-2]) > 1)):
                            sentences.append(currentline[:-1]) #fix this
                            currentline = currentline[-1]
                        else:
                            sentences.append(currentline)
                            currentline = []
    return sentences

def second_pass(sentences):
    new_sentences = []
    count = 0
    for sentence in sentences:
        if not sentence[0].islower() or count == 0:
            new_sentences.append(sentence)
            count += 1
        else:
            if count > 0:
                new_sentences[count-1] + sentence

    return new_sentences

def print_doc(filename,sentences):
    basefilename = filename.split(".")[0]
    ofile = open(basefilename + ".out",'w')

    for sent in sentences:
         for i,word in enumerate(sent):
            ofile.write(word)
            if i < len(sent):
                ofile.write(" ")
         ofile.write("\n\n")

def main():
    essay = load_file(sys.argv[1])
    segmenteddoc = segment_sent(essay)
    segmenteddoc = second_pass(segmenteddoc)
    print_doc(sys.argv[1],segmenteddoc)

if __name__ == "__main__":
    main()

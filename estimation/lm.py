from math import log, exp
from collections import defaultdict, Counter
from zipfile import ZipFile
import re
import random

kNEG_INF = -1e6

kSTART = "<s>"
kEND = "</s>"

kWORDS = re.compile("[a-z]{1,}")
kREP = set(["Bush", "GWBush", "Eisenhower", "Ford", "Nixon", "Reagan"])
kDEM = set(["Carter", "Clinton", "Truman", "Johnson", "Kennedy"])

kNOTOBAMA= set(["Bush", "GWBush", "Eisenhower", "Ford", "Nixon", "Reagan","Carter", "Clinton", "Truman", "Johnson", "Kennedy"])

class OutOfVocab(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)

def sentences_from_zipfile(zip_file, filter_presidents):
    """
    Given a zip file, yield an iterator over the lines in each file in the
    zip file.
    """
    with ZipFile(zip_file) as z:
        for ii in z.namelist():
            try:
                pres = ii.replace(".txt", "").replace("state_union/", "").split("-")[1]
            except IndexError:
                continue

            if pres in filter_presidents:
                for jj in z.read(ii).decode(errors='replace').split("\n")[3:]:
                    yield jj.lower()

def tokenize(sentence):
    """
    Given a sentence, return a list of all the words in the sentence.
    """
    
    return kWORDS.findall(sentence.lower())

def bigrams(sentence):
    """
    Given a sentence, generate all bigrams in the sentence.
    """
    
    for ii, ww in enumerate(sentence[:-1]):
        yield ww, sentence[ii + 1]




class BigramLanguageModel:

    def __init__(self):
        self._vocab = set([kSTART, kEND])
        
        # Add your code here!
        # Bigram counts
        
        self.contextCounts = {}
        
        self._vocab_final = False

    def train_seen(self, word):
        """
        Tells the language model that a word has been seen.  This
        will be used to build the final vocabulary.
        """
        assert not self._vocab_final, \
            "Trying to add new words to finalized vocab"

        self._vocab.add(word)

    def generate(self, context):
        """
        Given the previous word of a context, generate a next word from its
        conditional language model probability.  
        """

        # Add your code here.  Make sure to the account for the case
        # of a context you haven't seen before and Don't forget the
        # smoothing "+1" term while sampling.
        '''
        prob = -1
        wordReturn = ""
        for word in self.contextCounts[context]:
            probTmp = exp(self.laplace(context, word))
            if(probTmp > prob):
                prob = probTmp
                wordReturn = word
        '''
        #Use a random number to select the next work in the sentence
        wordList = []
        
        prob = 0
        for word in self._vocab:
            prob += exp(self.laplace(context, word))
            
            wordList.append((word,prob))
        
        choice = random.uniform(0,1)
        for word,probability in wordList:
            if(choice <= probability):
                return word
        
            
    def sample(self, sample_size):
        """
        Generate an English-like string from a language model of a specified
        length (plus start and end tags).
        """

        # You should not need to modify this function
        yield kSTART
        next = kSTART
        for ii in range(sample_size):
            next = self.generate(next)
            if next == kEND:
                break
            else:
                yield next
        yield kEND
            
    def finalize(self):
        """
        Fixes the vocabulary as static, prevents keeping additional vocab from
        being added
        """
        
        # you should not need to modify this function
        
        self._vocab_final = True

    def tokenize_and_censor(self, sentence):
        """
        Given a sentence, yields a sentence suitable for training or testing.
        Prefix the sentence with <s>, generate the words in the
        sentence, and end the sentence with </s>.
        """

        # you should not need to modify this function
        
        yield kSTART
        for ii in tokenize(sentence):
            if ii not in self._vocab:
                raise OutOfVocab(ii)
            yield ii
        yield kEND

    def vocab(self):
        """
        Returns the language model's vocabulary
        """

        assert self._vocab_final, "Vocab not finalized"
        return list(sorted(self._vocab))
        
    def laplace(self, context, word):
        """
        Return the log probability (base e) of a word given its context
        """
		
        assert context in self._vocab, "%s not in vocab" % context
        assert word in self._vocab, "%s not in vocab" % word
        
        #calculate prob of next word using the bigram dictionary
        if word not in self.contextCounts[context]:
            wordOccurence = 1
        else:
            wordOccurence = self.contextCounts[context][word] + 1 
        
        total=sum(self.contextCounts[context].values()) + len(self._vocab)
        
        prob = log(wordOccurence/total)
       
        return prob

    def add_train(self, sentence):
        """
        Add the counts associated with a sentence.
        """

        # You'll need to complete this function, but here's a line of code that
        # will hopefully get you started.
		
		#populate nested dictionary with bigram counts
        for context, word in bigrams(list(self.tokenize_and_censor(sentence))):
            None
            # ---------------------------------------
            assert word in self._vocab, "%s not in vocab" % word
            
            if(context not in self.contextCounts):
                self.contextCounts[context] = {}
                self.contextCounts[context][word] = 1
            else:
                if(word not in self.contextCounts[context]):
                    self.contextCounts[context][word] = 1
                else:
                    self.contextCounts[context][word] += 1
                
        
    def log_likelihood(self, sentence):
        """
        Compute the log likelihood of a sentence, divided by the number of
        tokens in the sentence.
        """
        #Compute probability by taking the product of every bigram in the sentence
        prob = 1
        for context, word in bigrams(list(self.tokenize_and_censor(sentence))):
            prob *= exp(self.laplace(context,word))
        
        return log(prob)


if __name__ == "__main__":
    dem_lm = BigramLanguageModel()
    rep_lm = BigramLanguageModel()
    
    
    #code below identifies words only obama said
    '''
    obamaSet = set()
    notObamaSet = set()
    with open("../data/2016-obama.txt") as f:
        for sent in f:
            for ww in tokenize(sent):
                obamaSet.add(ww)
    
    for target, pres, name in [(dem_lm, kNOTOBAMA, "D")]:
        for sent in sentences_from_zipfile("../data/state_union.zip", pres):
            for ww in tokenize(sent):
                notObamaSet.add(ww)
    
    
    for word in obamaSet:
        if word not in notObamaSet:
            print(word)
    '''
  
    for target, pres, name in [(dem_lm, kDEM, "D"),(rep_lm,kREP, "R")]:
        for sent in sentences_from_zipfile("../data/state_union.zip", pres):
            for ww in tokenize(sent):
                target.train_seen(ww)
       
        print("Done looking at %s words, finalizing vocabulary" % name)
        target.finalize()
        
        for sent in sentences_from_zipfile("../data/state_union.zip", pres):
            target.add_train(sent)
    
        print("Trained language model for %s" % name)

    with open("../data/2016-obama.txt") as infile:
        print("REP\t\tDEM\t\tSentence\n" + "=" * 80)
        for ii in infile:
            if len(ii) < 15: # Ignore short sentences
                continue
            try:
                dem_score = dem_lm.log_likelihood(ii)
                rep_score = rep_lm.log_likelihood(ii)

                print("%f\t%f\t%s" % (dem_score, rep_score, ii.strip()))
            except OutOfVocab:
                None  
    #The code below prints a random sentence
    #randomSentence = " ".join(rep_lm.sample(8))
    #print(randomSentence)
	

# Further refine the relationship results by removing repeatitions
import traceback
import os.path
import sys
import nltk
import itertools

from DependencyGraph import *
from nltk.corpus import stopwords
from nltk import pos_tag
from nltk.corpus import wordnet

class RelationshipSegregator:
    def __init__(self):

        lemmatizer = nltk.WordNetLemmatizer()
        
        stopwrds = set(stopwords.words('english'))
        
        with open('NonsenseWords.txt','r') as n:
            nonsensewords = n.read()
            nonsensewords = nonsensewords.split('\n')
        
        def lemmatization_stemming(word):
            # getting stems and lemmatizing it
            wordtag = get_wordnet_pos(pos_tag([word])[0][1])
            return lemmatizer.lemmatize(word, pos=wordtag)

        def get_wordnet_pos(word_tag):
            if word_tag.startswith('J'):
                return wordnet.ADJ
            elif word_tag.startswith('V'):
                return wordnet.VERB
            elif word_tag.startswith('N'):
                return wordnet.NOUN
            elif word_tag.startswith('R'):
                return wordnet.ADV
            else:
                return ''
        
        def IsValidPart(phrase):
            if phrase == '':
                return False
            words = phrase.split(' ') 
            if any(word in nonsensewords for word in words):
                return False
            for word in words:
                if len(pos_tag([word.strip()])) >= 1 and len(pos_tag([word.strip()])[0]) == 2 and (pos_tag([word.strip()])[0][1] == 'DT' or pos_tag([word.strip()])[0][1] == 'CC' or pos_tag([word.strip()])[0][1] == 'CD' or pos_tag([word.strip()])[0][1] == 'PRP$' or pos_tag([word.strip()])[0][0] in ['my','mine','our','ours','your','yours','their','theirs','its','his','her','hers','e.g','one','=','i.e']):
                    return False   
            return True
        
        def RemovePlurals(wordphrase):
            phrase = []
            if wordphrase != '':
                ws = wordphrase.split(' ')
                for w in ws:
                    if w.endswith('s'):
                        if lemmatization_stemming(w) != w:
                            phrase.append(lemmatization_stemming(w))
                    else:
                        phrase.append(w)
                if len(phrase) > 0:
                    return ' '.join(phrase)
            else:
                return wordphrase
        
        def NotAlreadyPartOfAPhrase(wordphrase, phrases):    
            for p in phrases:
                if isSubSequence(wordphrase, p, len(wordphrase), len(p)) or isSubSequence(p, wordphrase, len(p), len(wordphrase)):
                    return False
            return True
        
        def GetSubSequenceProps(phrase, sequence):
            for seq in sequence:
                if isSubSequence(phrase, seq, len(phrase), len(seq)):
                    return (0)
                if isSubSequence(seq, phrase, len(seq), len(phrase)):
                    return (1, sequence.index(seq))
        
        def TrimmedPart(phrase):
            words = phrase.split(' ')
            phraseWords = [w for w in words if pos_tag([w])[0][1] != 'DT' and pos_tag([w])[0][0].lower() != 'the' and pos_tag([w])[0][1] != 'CC' and pos_tag([w])[0][1] != 'PRP$' and w not in stopwrds]
            return ' '.join(phraseWords)
        
        def isSubSequence(string1, string2, m, n):
            # Base Cases
            if m == 0:    return True
            if n == 0:    return False
         
            # If last characters of two strings are matching
            if string1[m - 1] == string2[n - 1]:
                return isSubSequence(string1, string2, m - 1, n - 1)
         
            # If last characters are not matching
            return isSubSequence(string1, string2, m, n - 1)
        
        for i in range(1, 5):
            index = str(i)
            if os.path.exists('Refined-R'+index+'-FeatureRelations.txt'):
                os.remove('Refined-R'+index+'-FeatureRelations.txt')
        
            with open('R'+index+'.txt','r') as f:
                R1relations = f.read()    
        
            AllRelations = []
            
            R1relations = R1relations.replace('\n','')
        
            R1RelSegments = R1relations.split('->X')
            for segment in R1RelSegments:    
                parts = segment.split('->')    
                segmentList = []
                for part in parts:
                    part = part.strip().lower()
                    if IsValidPart(part):
                        part = TrimmedPart(part)
                        part = RemovePlurals(part)
                        if part not in segmentList and not(part is None) and part != '':
                           if NotAlreadyPartOfAPhrase(part, segmentList):
                                segmentList.append(part.strip())
                           else:
                                # Find the position of the subsequence and replace
                                props = GetSubSequenceProps(part, segmentList)
                                if props != (0):
                                    segmentList.insert(props[1], part.strip())                        
                                    segmentList.remove(segmentList[props[1]+1])
            
                if len(segmentList) > 1:
                    AllRelations.append(segmentList)
          
            AllRelations.sort()
            AllRelations = list(AllRelations for AllRelations,_ in itertools.groupby(AllRelations))
            AllRelations = [x for x in AllRelations if x]
            for rels in AllRelations:
                with open('Refined-R'+index+'-FeatureRelations.txt', "a") as f:
                    for item in list(rels):
                        f.write(str(item) + '->')
                    f.write('\n')
        
        dependencygraph()

            

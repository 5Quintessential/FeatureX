import traceback
import os.path
import sys
import nltk
import itertools

from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk import pos_tag

class RelashionshipMiner:
    def __init__(self):

        features = []
        featureTerms = []
        positions = []
        R1 = []
        R2 = []
        R3 = []
        R4 = []
        
        if os.path.exists('MinedRelationships.txt'):
            os.remove('MinedRelationships.txt')
        if os.path.exists('R1.txt'):
            os.remove('R1.txt')
        if os.path.exists('R2.txt'):
            os.remove('R2.txt')
        if os.path.exists('R3.txt'):
            os.remove('R3.txt')
        if os.path.exists('R4.txt'):
            os.remove('R4.txt')
        
        def remove_all_unwanted_terms(allFeatures):
            filteredFeatures = []
            good = False
            nonsensewords = [word.strip() for word in open("NonsenseWords.txt", "r")]
            for phrase in allFeatures:
                for word in word_tokenize(phrase):
                    postaggedword = pos_tag([word])
                    if(postaggedword[0][0].lower() not in nonsensewords):
                        if(postaggedword[0][1] not in ['VBN', 'VB', 'JJ','JJS','JJR']):
                            good = True
                        else:
                            if len(str(phrase).split(' ')) > 1:
                                good = True
                            else:
                                good = False
                                break
                    else:
                        good = False
                        break

                if (good):
                    filteredFeatures.append(phrase)
            return filteredFeatures

        # Read the corpus and tokenize
        with open("processedtext.txt","r") as ct:
            try: # read the test specification text
                corpus = ct.read()
                sentences = sent_tokenize(corpus)
                featureterms = []
                # Read all the candidate feature terms
                with open("CandidateTerms.txt","r") as cterms:
                    try:
                        features = cterms.readlines()
                        features = [x.strip() for x in features] 
                        features = features[0].replace('\'','')
                        featureterms = features.split(',')
                        features = [f.lstrip() for f in featureterms if f != ' ']
                        # Remove plurals,nonsense words, single adjectives, palindromes and standalone verbs from candidate features
                        features = remove_all_unwanted_terms(features)
                    except Exception: 
                        traceback.print_exc()
                        pass
                for sentence in sentences:
                    featureTerms = []
                    words = word_tokenize(sentence)
                    tokens = pos_tag(words)
                    # Decide whether or not we should select the sentence for further
                    # processing
                    verbMarker = [w[0] for w in tokens if w[1] in ('MD')]
                    pre_participle = [w[0] for w in tokens if w[1] == 'VBG']
                    pas_participle = [w[0] for w in tokens if w[1] == 'VBN']
                    conditionalVerb = [w[0] for w in tokens if w[0].lower() in ('if','then','else')]
                    adverbs = [w[0] for w in tokens if w[0].lower() in ('often','never','always','frequently','normally','usually','generally','regularly','occasionally','sometimes','hardly','rarely')]
                    predeterminers = [w[0] for w in tokens if w[0].lower() in ('all','every','each','any','some')]
        
                    if(verbMarker or conditionalVerb or adverbs or predeterminers or (pre_participle and pas_participle)):
                        # Find the feature terms present in this sentence
                        for f in features:
                            k = f.split()
                            if set(k).issubset(set(words)):
                                featureTerms.append(f)  
                        
                        # Match with the defined ontological patterns
                        if(verbMarker):
                            verbPos = [words.index(v) for v in verbMarker]
                        else:
                            verbPos = [-1]
                        if(pre_participle and pas_participle):
                            partPos = [words.index(v) for v in pas_participle]
                        else:
                            partPos = [-1]
                        if(conditionalVerb):
                            condPos = [words.index(v) for v in conditionalVerb]
                        else:
                            condPos = [-1]
                        if(adverbs):
                            advPos = [words.index(v) for v in adverbs]
                        else:
                            advPos = [-1]
                        if(predeterminers):
                            prePos = [words.index(v) for v in predeterminers]
                        else:
                            prePos = [-1]
                        if featureTerms.count >= 2:   
                            positions = []                 
                            for f in featureTerms:
                                firstword = f.split()[0]
                                f_pos = words.index(firstword)
                                positions.append(f_pos)
                            positions.sort()
                            pairs = list(itertools.combinations(list(set(positions)),2))
                            pairsset = set(pairs)
                            # Pattern R1: f->MD->f'
                            for v in verbPos:
                                if any(lower < v < upper for (lower, upper) in pairsset):
                                    foundPair = [(lower, upper) for (lower, upper) in pairsset if lower < v < upper]
                                    uniquePos = set(itertools.chain.from_iterable(foundPair))
                                    if uniquePos:
                                        t1 = max(filter(lambda x: x < v,uniquePos))
                                        t2 = max(filter(lambda x: x > v,uniquePos))
                                        allPhrases = [f for f in featureTerms if words[t1] in f or words[t2] in f]
                                        R1.append(allPhrases)
        
                            # Pattern R2: f->adv->f' OR f->det->f'
                            for a in advPos:
                                if any(lower < a < upper for (lower, upper) in pairsset):
                                    adv = [(lower, upper) for (lower, upper) in pairsset if lower < a < upper]
                                    uniquePos = set(itertools.chain.from_iterable(adv))
                                    if uniquePos:
                                        t1 = max(filter(lambda x: x < a,uniquePos))
                                        t2 = max(filter(lambda x: x > a,uniquePos))
                                        allPhrases = [f for f in featureTerms if words[t1] in f or words[t2] in f]
                                        R2.append(allPhrases)
                            for  p in prePos:
                                if any(lower < p < upper for (lower, upper) in pairsset):
                                    det = [(lower, upper) for (lower, upper) in pairsset if lower < p < upper]
                                    uniquePos = set(itertools.chain.from_iterable(det))
                                    if uniquePos:
                                        t1 = max(filter(lambda x: x < p,uniquePos))
                                        t2 = max(filter(lambda x: x > p,uniquePos))
                                        allPhrases = [f for f in featureTerms if words[t1] in f or words[t2] in f]
                                        R2.append(allPhrases)
        
                            # Pattern R3: f->VBN->VBG-> f'
                            for vb in partPos:
                                if any(lower < vb < upper for (lower, upper) in pairsset):
                                    foundTerms = [(lower, upper) for (lower, upper) in pairsset if lower < vb < upper]
                                    uniquePos = set(itertools.chain.from_iterable(foundTerms))
                                    if uniquePos:
                                        t1 = max(filter(lambda x: x < vb,uniquePos))
                                        t2 = max(filter(lambda x: x > vb,uniquePos))
                                        allPhrases = [f for f in featureTerms if words[t1] in f or words[t2] in f]
                                        R3.append(allPhrases)
        
                            # Pattern R4: if->f->then-> f'
                            for cn in condPos:
                                if not -1 in condPos and any(cn < lower < upper for (lower, upper) in pairsset):
                                    foundTerms = [(lower, upper) for (lower, upper) in pairsset if lower < cn < upper]
                                    uniquePos = set(itertools.chain.from_iterable(foundTerms))
                                    if uniquePos:
                                        t1 = max(filter(lambda x: x < cn,uniquePos))
                                        t2 = max(filter(lambda x: x > cn,uniquePos))
                                        allPhrases = [f for f in featureTerms if words[t1] in f or words[t2] in f]
                                        R4.append(allPhrases)
                
                            f = open('R1.txt', 'a')    
                            for item in list(R1):
                                for i in item:
                                    f.write(str(i) + '->') 
                                f.write('X \n')
                            f.close()
                            R1 = []
        
                            f = open('R2.txt', 'a')    
                            for item in list(R2):
                                for i in item:
                                    f.write(str(i) + '->') 
                                f.write('X \n')
                            f.close()
                            R2 = []
        
                            f = open('R3.txt', 'a')    
                            for item in list(R3):
                                for i in item:
                                    f.write(str(i) + '->') 
                                f.write('X \n')
                            f.close()
                            R3 = []
        
                            f = open('R4.txt', 'a')    
                            for item in list(R4):
                                for i in item:
                                    f.write(str(i) + '->') 
                                f.write('X \n')                        
                            f.close()
                            R4 = []
            except Exception: 
                traceback.print_exc()
                pass 
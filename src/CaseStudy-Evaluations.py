# CASE STUDY - Cryptocurrency products
import FeatureX
import time

from FeatureX import *
from RelMiner import RelashionshipMiner
from MLRel import MachineLearnRelations

start_time = time.time()

## ***************** READ ME *****************************
## In this example we are evaluating 3 documents related to
## cryptocurrency and saving the output file (.dot file
## which has all the features and relationships without 
## indicating the relationship types) to a date-time-folder 
## in the current directory.
## Please copy the input PDF files from the examples folder
## to the path of this python files folder from where you
## start execution. After you run the below code you will
## see 3 folders created in the same directory and from each
## folder copy the grid.dot file to the executing directory
## as FM1.dot, FM2.dot and FM3.dot.

## After this follow the instructions on 'DotFileComparer.py'
## ********************************************************

fx = featurex('CryptoCurrency1.pdf','2-14') ## input file 1
fx.pre_process()
fx.extract_candidates()
RelashionshipMiner()
RelationshipSegregator()

## Move all results
fx.clean_workspace()

fx = featurex('CryptoCurrency2.pdf','3-35') ## input file 2
fx.pre_process()
fx.extract_candidates()
RelashionshipMiner()
RelationshipSegregator()

## Move all results
fx.clean_workspace()

fx = featurex('CryptoCurrency3.pdf','1-14') ## input file 3
fx.pre_process()
fx.extract_candidates()
RelashionshipMiner()
RelationshipSegregator()

# Move all results
fx.clean_workspace()

print "--- %s seconds ---" % (time.time() - start_time)

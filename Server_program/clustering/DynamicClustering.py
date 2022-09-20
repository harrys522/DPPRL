from sklearn.neighbors import NearestNeighbors
import os, sys
parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)
from data_structures.Utilities import *
from data_structures.ClusterList import *

class DynamicClusterer:
    def findBestClusterForRow(blockingTurnedOn,row,operation, indexer,clusterAggregations):
        """
        - the idea of taking 2 best clusters is so we can somewhat judge uncertainty of clustering
        by checking how close the 2nd cluster comes to the first
        """
        if(blockingTurnedOn):
            if(indexer.indexingHasNotBeenDoneYet()):
                indexer.initialIndexBuild()
            indexingKey = indexer.getIndexingKey()
        
        knn_classifier = NearestNeighbors(n_neighbors=2, metric="cosine")

        if (not blockingTurnedOn):
            knn_classifier.fit(clusterAggregations) # fit the model based on the whole data
        else: # else if indexing is enabled
            assert indexer.indexingHasNotBeenDoneYet(), "indexing not done"
            indexedClusterAggregations = indexer.indexingDictionary[indexingKey]
            knn_classifier.fit(indexedClusterAggregations) #fit the model based on subset of data

        distance_mat, neighbours_vec = knn_classifier.kneighbors([row.rowListRepresentation])
        
        clusterIdxBest1= neighbours_vec[0][0] # gets us index of cluster that we want to modify
        
        cosSimBst1 = 1 - distance_mat[0][0]
        cosSimBst2 = 1 - distance_mat[0][1]

        certaintyScore = None
        
        if operation == Operation.INSERT:
            certaintyScore = DynamicClusterer.getInsertionCertainty(cosSimBst1,cosSimBst2)
        else: # most be considering delete or modification
            certaintyScore = cosSimBst1 # the certainty for modification and delete is just the similarity for best match

        #print("cos sim: "+str(cosineSimilarity) + " & reccomended neighbout is at idx: " + str(clusterIdx))
        return clusterIdxBest1,certaintyScore

    
    def getInsertionCertainty(cosSimBst1,cosSimBst2):
        # returns certainty that row belong to particular cluster for the purpose of insertion 
        # 
        # behaviour this certainty score exhibits: 
        # - certainty is in [0,1]
        # - when simDiff (difference in similarity scores between best 2 matches) is low (close to 0), certainty is lower since we are torn between 2 best picks
        # - when cosSimBst1 is high (close to 1) certainty should be high since we found good matching cluster

        if (cosSimBst1>cosSimBst2 and cosSimBst1>0):
            diffScore = abs(cosSimBst1-cosSimBst2)/2
            certainty = (cosSimBst1*diffScore+1)/2 #mapping it onto [0,1]
        else:
            certainty = 0

        return certainty
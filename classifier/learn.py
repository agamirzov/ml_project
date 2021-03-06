#!/usr/bin/python3

import os
import numpy as np
import neurolab as nl
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import random

def main():
    
    PATH_TO_TRAINING_SET = os.path.dirname(os.path.realpath(__file__)) + "/../data/training/training_set.csv"

    seasons = ['2007_2008', '2008_2009', '2009_2010', '2010_2011',\
               '2011_2012', '2012_2013', '2013_2014', '2014_2015']

    NUM_TEAMS = 20
    NUM_SEASONS = len(seasons)
    SEASONS_TO_CONSIDER = 2
    MDS_PER_SEASON = 38
    MATCHES_PER_MD = 10
    MATCHES_PER_SEASON = MDS_PER_SEASON * MATCHES_PER_MD
    LAST_MD = 25

    TOTAL_VALID_MATCHES = ((NUM_SEASONS - SEASONS_TO_CONSIDER) - 1) * MATCHES_PER_SEASON + \
                    LAST_MD * MATCHES_PER_MD

    def read_data():
        #Read the training examples from the csv file (except the header)
        my_data = np.genfromtxt(PATH_TO_TRAINING_SET, delimiter=',', skip_header=1)

        #Remove the first column (which contains indices)
        my_data = np.delete(my_data, 0, 1)

        #Only keep the training examples for matches which have already occurred
        my_data = my_data[:TOTAL_VALID_MATCHES, :]

        #Remove NaNs
        my_data = my_data[~np.isnan(my_data).any(axis=1)]

        #Remove different columns from the training set for testing


        return my_data


    def normalize(array):
        maximals = np.amax(array, axis=0)
        # Target values don't have to be normalized
        maximals[0] = 1.
        
        return np.divide(array, maximals)

 
    def classify(training_set, training_target, validation_set, classifier, probability=False):

        # Train the classifyer
        classifier.fit(training_set, training_target)
        
        # Predict new outcomes
        prediction = classifier.predict(validation_set)
        
        if probability:
            predicition_probability = classifier.predict_proba(validation_set)

        return [prediction, predicition_probability] if probability else prediction


    def cross_validation(data, k, classifier):
        """Computes average efficiency of the algorithm using cross validation
        
        Arguments:
            data - (matrix of doubles) initial trainig set
            k - (int) number of folds
            classifier - classifier object which has fit() and predict() functions
        
        Returns:
            total_efficiency - (double) average efficiency for all possible combinations of trainig and validation sets
        """

        # Compute intervals
        interval = int(len(data) / k)
        remainder = len(data) % k
        
        # Compute offsets
        offsets = np.zeros(k + 1)
        for i in range(k):
            offsets[i] = i * interval
        offsets[k] = k * interval + remainder

        # Init counter and efficiency
        counter = 0
        total_efficiency = 0
        prediction = 0
        prediction_prob = 0

        # Iterate over the  
        for i in offsets[0:k]:
            # Compute size of the validation set
            validation_size = offsets[counter + 1] - offsets[counter]

            # Set up the validation set and it's outcomes
            validation_set = data[i:(i + validation_size), 1:]
            validation_outcomes = data[i:(i + validation_size), 0]
        
            # Set up the remaining data as the trainig set and it's outcomes
            training_set = np.concatenate((data[0:i, 1:], data[(i + validation_size):, 1:]), axis=0)
            training_target = np.concatenate((data[0:i, 0], data[(i + validation_size):, 0]), axis=0)

            # Classify with the specified algorithm
            prediction = classify(training_set, training_target, validation_set, classifier)

            # prediction = manual_prediction(prediction_prob,0.07)
            # Compare predicted outcomes with known outcomes
            num_predictions = len(validation_outcomes)
            correct = np.count_nonzero(prediction == validation_outcomes)
        
            # Compute how many predicted values matching the known outcomes (%)
            efficiency = correct/num_predictions

            # Accumulate efficiency for all possible combinations
            total_efficiency += efficiency
            
            # Increasing counter
            counter += 1

        # print(prediction)
        # print(prediction_prob)

        # Return average efficiency
        return total_efficiency / counter


    def find_best_SVM(gammas=[0.001, 0.002, 0.003, 0.004, 0.005],
            cs=[20, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200, 300, 500,1000],
            rs=[0., 1., 2., 5., 10., 20., 50.], ds=[1., 2., 3.]):
        """ Computes the best combination parameters for SVM        

        Arguments:
            gammas - (array of doubles) array of the possible gammas
            cs - (array of ints) array of possible C's
        
        Returns:
            [best_gamma, best_c] - (double) best gamma, (int) best C
        """
        
        print("RBF")
        efficiency = 0
        old_efficiency = 0
        best_gamma = 0
        best_c = 0
        for ga in gammas:
            for c in cs:
                old_efficiency = cross_validation(my_data, 10, svm.SVC(gamma=ga, C=c, kernel='rbf'))
                if(efficiency < old_efficiency):
                    efficiency = old_efficiency
                    best_gamma = ga
                    best_c = c
                print("%f \t %d \t %f" % (ga, c, old_efficiency))
        print("Best Gamma = %f Best C = %d Efficiency = %f" % (best_gamma, best_c, efficiency))

        print("POLY")
        efficiency = 0
        old_efficiency = 0
        best_r = 0
        best_d = 0
        for d in ds:
            for r in rs:
                old_efficiency = cross_validation(my_data, 10, svm.SVC(kernel='poly', coef0=r, degree=d))
                if(efficiency < old_efficiency):
                    efficiency = old_efficiency
                    best_r = r
                    best_d = d
                print("%d \t %d \t %f" % (r, d, old_efficiency))
        print("Best R = %d Best d = %d Efficiency = %f" % (best_r, best_d, efficiency))


    def find_best_KNN(neighbors):
        """ Computes the best combination parameters for KNN        

        Arguments:
            neighbors - (array of ints) array of possible neighbors
        
        Returns:
            best_neighbors - (int) the best number of neighbors
        """
        efficiency = 0
        old_efficiency = 0
        best_neighbors = 0
        for nn in neighbors:
            old_efficiency = cross_validation(my_data, 10, KNeighborsClassifier(n_neighbors=nn, weights='distance'))
            if(efficiency < old_efficiency):
                efficiency = old_efficiency
                best_neighbors = nn
            print("%d\t %f" % (nn, old_efficiency))
        print("Best neighbors = %d Efficiency = %f" % (best_neighbors, efficiency))
        return best_neighbors


    class FFNetwork:
        """A wrapper for the neurolab.net.newff()"""

        def __init__(self, input_dim, minmax=[[-20, 20]], layers=[10, 1]):
            self.network = nl.net.newff(minmax * input_dim, layers)

        def fit(self, training_set, training_target):
            length = training_target.shape[0]
            training_target = training_target.reshape([length, 1])
            error = self.network.train(training_set, training_target)

        def predict(self, test_set):
            pred = self.network.sim(test_set)[:, 0]
            return pred

    """Main"""

    # Read .csv file
    my_data = read_data()
    print("Data loaded successfully")

    # Normalization
    my_data = normalize(my_data)
    print("Data normalized successfully")

    #Neural network
    print("Neural network accuracy = %f" % cross_validation(\
                my_data, 10, FFNetwork(16))) 
    #kNN
    print("kNN accuracy = %f" % cross_validation(\
                my_data, 10, KNeighborsClassifier(n_neighbors=221, weights='distance')))
    #SVM
    print("SVM accuracy = %f" % cross_validation(\
                my_data, 10, svm.SVC(kernel='rbf', gamma=0.005, C=30)))
    #Logistic regression
    print("Logistic regression accuracy = %f" % cross_validation(\
                my_data, 10, LogisticRegression(C=0.36, penalty='L1')))
    #Random forest
    print("Random forest best accuracy = %f" % cross_validation(\
                my_data, 10, RandomForestClassifier(n_estimators=500, criterion='gini')))


if __name__ == "__main__":
    main()


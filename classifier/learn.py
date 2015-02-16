import numpy as np
import pandas as pd
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import BernoulliNB

def main():
    
    PATH_TO_TRAINING_SET = "../data/training/training_set.csv"

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

        return my_data

    def classify(training_set, training_target, validation_set, classifier, probability=False):

        # Train the classifyer
        classifier.fit(training_set, training_target)
        
        # Predict new outcomes
        prediction = classifier.predict(validation_set)
        
        if probability:
            predicition_probability = classifier.predict_proba(validation_set)

        return [prediction, predicition_probability] if probability else prediction

    def compute_efficiency(data, k, classifier):
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

            # Compare predicted outcomes with known outcomes
            num_predictions = len(validation_outcomes)
            correct = np.count_nonzero(prediction == validation_outcomes)
        
            # Compute how many predicted values matching the known outcomes (%)
            efficiency = correct/num_predictions

            # Accumulate efficiency for all possible combinations
            total_efficiency += efficiency
            
            # Increasing counter
            counter += 1

        # Return average efficiency
        return total_efficiency / counter

    """ Start program """
    
    # Read .csv file
    my_data = read_data()

    # Apply cross validation on the data set
    efficiency = compute_efficiency(my_data, 10, svm.SVC(gamma=0.001, C=100.))
    print("Efficiency: %.2f" % efficiency)

if __name__ == "__main__":
    main()






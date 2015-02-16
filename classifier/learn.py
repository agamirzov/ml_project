import numpy as np
import pandas as pd
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier

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

    def classify(training_set, training_outcomes, validation_set, classifyer_type):

        # Assign the type of the classifyer
        if classifyer_type == "SVM":
            classifier = svm.SVC(gamma=0.001, C=100.)
        elif classifyer_type == "KNN":
            classifier = KNeighborsClassifier(n_neighbors=10)
        else:
            print("Wrong classifyer type!")

        # Train the classifyer
        classifier.fit(training_set, training_outcomes)
        
        # Predict new outcomes
        prediction = classifier.predict(validation_set)

        return prediction

    def compute_efficiency(data, validation_size, validation_step, classifyer_type):
        """Computes average efficiency of the algorithm using cross validation
        
        Arguments:
            data - (matrix of doubles) initial trainig set
            validation_size - (int) length of the validation set (number of input vectors)
            validation_step - (int) intervals between different validation sets
        
        Returns:
            total_efficiency - (double) average efficiency for all possible combinations of trainig and validation sets
        """

        # Init total efficiency, the combination counter and the range
        total_efficiency = 0;                            
        combination_counter = 0
        validations_range = len(data) - validation_size

        # Iterate over different combinations of trainig/validation sets
        for i in range(0, validations_range, validation_step):

            # Increment the validation counter
            combination_counter += 1
            
            # Set up the validation set and it's outcomes
            validation_set = data[i:(i + validation_size), 1:]
            validation_outcomes = data[i:(i + validation_size), 0]
        
            # Set up the remaining data as the trainig set and it's outcomes
            training_set = np.concatenate((data[0:i, 1:], data[(i + validation_size):, 1:]), axis=0)
            training_outcomes = np.concatenate((data[0:i, 0], data[(i + validation_size):, 0]), axis=0)

            # Classify with the specified algorithm
            prediction = classify(training_set, training_outcomes, validation_set, classifyer_type)

            # Compare predicted outcomes with known outcomes
            num_predictions = len(validation_outcomes)
            correct = np.count_nonzero(prediction == validation_outcomes)
        
            # Compute how many predicted values matching the known outcomes (%)
            efficiency = correct/num_predictions
            print("Validation step %d is computed. Efficiency: %f" % (combination_counter, efficiency))

            # Accumulate efficiency for all possible combinations
            total_efficiency += efficiency

        # Compute average efficiency
        total_efficiency = total_efficiency/combination_counter

        return total_efficiency

    """ Start program """
    
    # Read .csv file
    my_data = read_data()

    # Length of the validation set (number of input vectors)
    validation_set_size = 300

    # Intervals between different validation sets
    validation_step_size = 300

    # Apply cross validation on the data set
    efficiency = compute_efficiency(my_data, validation_set_size, validation_step_size, "SVM")
    
    # Print cross validation results
    print("Total Efficiency: %s" % (efficiency))

if __name__ == "__main__":
    main()






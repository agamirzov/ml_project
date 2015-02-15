import numpy as np
import pandas as pd
from sklearn import svm

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

    my_data = read_data()


    #Define the target vector and the data points

    threshold = 1700
    training_set = my_data[:threshold, 1:]
    target_points = my_data[:threshold, 0]

    testing_set = my_data[threshold: threshold + 200, 1:]
    testing_target = my_data[threshold: threshold + 200, 0]


    def classify():
        classifier = svm.SVC(gamma=0.001, C=100.)
        print(classifier.fit(training_set, target_points))
        prediction = classifier.predict(testing_set)

        total = 200.
        correct = np.count_nonzero(prediction == testing_target)
        print(correct/total)


    classify()

if __name__ == "__main__":
    main()






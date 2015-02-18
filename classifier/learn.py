import numpy as np
import pandas as pd
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import GaussianNB
import random

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
        my_data = np.delete(my_data, 8, 1)
        my_data = np.delete(my_data, 15, 1)

        #Only keep the training examples for matches which have already occurred
        my_data = my_data[:TOTAL_VALID_MATCHES, :]

        #Remove NaNs
        my_data = my_data[~np.isnan(my_data).any(axis=1)]

        #print(my_data[0,:])

        return my_data


    def classify(training_set, training_target, validation_set, classifier, probability=True):

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
            p, prediction_prob = classify(training_set, training_target, validation_set, classifier)

            prediction = manual_prediction(prediction_prob,0.07)
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

    def manual_prediction(probabilities, epsilon):
        prediction = []
        cnt = 0
        for probs in probabilities:
            if (abs(probs[1] - probs[2]) < epsilon):
                prediction.append((np.where(probs == random.choice(probs)))[0][0])
                cnt += 1
            else:
                prediction.append((np.where(probs == max(probs)))[0][0])
        print("Number of random predictions %d" % cnt)

        return prediction


    def find_best_SVM(gamas, cs):
        """ Computes the best combination parameters for SVM        

        Arguments:
            gamas - (array of doubles) array of the possible gammas
            cs - (array of ints) array of possible C's
        
        Returns:
            [best_gamma, best_c] - (double) best gamma, (int) best C
        """
        efficiency = 0
        old_efficiency = 0
        best_gamma = 0
        best_c = 0
        for ga in gamas:
            for c in cs:
                old_efficiency = compute_efficiency(my_data, 10, svm.SVC(gamma=ga, C=c,probability=True))
                if(efficiency < old_efficiency):
                    efficiency = old_efficiency
                    best_gamma = ga
                    best_c = c
                print("Current gamma = %f Current C = %d Efficiency = %f" % (ga, c, old_efficiency))
        print("Best Gamma = %f Best C = %d Efficiency = %f" % (best_gamma, best_c, efficiency))
        return best_gamma, best_c


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
            old_efficiency = compute_efficiency(my_data, 10, KNeighborsClassifier(n_neighbors=nn))
            if(efficiency < old_efficiency):
                efficiency = old_efficiency
                best_neighbors = nn
            print("Current neighbors = %d Efficiency = %f" % (nn, old_efficiency))
        print("Best neighbors = %d Efficiency = %f" % (best_neighbors, efficiency))
        return best_neighbors


    def find_best_RandomForest(estimators):
        """ Computes the best combination parameters for KNN        

        Arguments:
            estimators - (array of ints) array of possible estimators
        
        Returns:
            best_estimators - (int) the best number of estimators
        """
        efficiency = 0
        old_efficiency = 0
        best_estimators = 0
        for ne in estimators:
            old_efficiency = compute_efficiency(my_data, 10, RandomForestClassifier(n_estimators=ne))
            if(efficiency < old_efficiency):
                efficiency = old_efficiency
                best_estimators = ne
            print("Current estimators = %d Efficiency = %f" % (ne, old_efficiency))
        print("Best estimators = %d Efficiency = %f" % (best_estimators, efficiency))
        return best_estimators


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

    # find_best_SVM([0.001,0.007], [90,100,300, 1000, 1100, 1150, 1200])
    # find_best_RandomForest([10, 15, 20, 25, 30, 35, 40, 45, 50,100])
    find_best_KNN([5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60 ,70 ,80, 90, 100,180])
    # print(compute_efficiency(my_data, 10, svm.SVC(gamma=0.007, C=100, probability=True)))

if __name__ == "__main__":
    main()






import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn import svm

iris = datasets.load_iris()

clf = svm.SVC(gamma=0.001, C=100.)
print(clf.fit(iris.data[:-5], iris.target[:-5]))
print(clf.predict(iris.data[-5:]))
print(iris.target[-5:])
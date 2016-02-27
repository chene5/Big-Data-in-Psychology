# -*- coding: utf-8 -*-
"""3_svm.py
Example code for SVM classification of irises.

@author: Eric Chen
"""
from sklearn import datasets
from sklearn.cross_validation import train_test_split
from sklearn.svm import LinearSVC
from sklearn import metrics


# Load the Iris dataset.
iris = datasets.load_iris()

# Split the data into a training set and a test set.
train_x, test_x, train_y, test_y = train_test_split(
    iris.data, iris.target, test_size=0.10, random_state=20)

# These are the training features.
# Only use Petal length and Petal width features
train_x = train_x[:, :2]
test_x = test_x[:, :2]

# Generate the classifier model. Fit the data.
lin_svc = LinearSVC().fit(train_x, train_y)

# Get the model's predictions for the test data.
predictions = lin_svc.predict(test_x)

# Evaluate the accuracy of the predictions.
score = metrics.accuracy_score(test_y, predictions)
print "accuracy:  %0.3f" % score

# Generate a more detailed classification report.
print metrics.classification_report(test_y,
                                    predictions,
                                    target_names=iris.target_names)

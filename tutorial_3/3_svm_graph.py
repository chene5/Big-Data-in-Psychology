# -*- coding: utf-8 -*-
"""3_svm_graph.py
Example code for SVM classification of irises.

@author: Eric Chen
"""
from sklearn import datasets
from sklearn.svm import LinearSVC
import matplotlib.pyplot as plt
import numpy as np


# Import the Iris dataset.
iris = datasets.load_iris()
# Only use Petal length and Petal width features
# These are the training features.
X = iris.data[:, :2]
# These are the labeled outcomes, the species of iris.
# Iris setosa, Iris versicolour, and Iris virginica
y = iris.target

# we create an instance of SVM and fit out data. We do not scale our
# data since we want to plot the support vectors
C = 1.0 # SVM regularization parameter
lin_svc = LinearSVC(C=C).fit(X, y)

# Set up data to be amenable to plotting.
# Create a mesh to plot in
h = .02 # step size in the mesh
x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                     np.arange(y_min, y_max, h))

# Get prediction from SVM.
prediction = lin_svc.predict(np.c_[xx.ravel(), yy.ravel()])

# Title for the plot
title = 'LinearSVC (linear kernel)'
# Labels for the plot
xlabel = 'Petal length'
ylabel = 'Petal width'

"""Generate a plot for the classifier prediction."""
# Plot the decision boundary. For that, we will assign a color to each
# point in the mesh [x_min, m_max]x[y_min, y_max].
# Put the result into a color plot
prediction = prediction.reshape(xx.shape)
plt.contourf(xx, yy, prediction, cmap=plt.cm.Paired, alpha=0.8)
# Plot also the training points
for i, point in enumerate(y):
    if point == 0:
        # setosa
        seto = plt.scatter(X[:, 0][i], X[:, 1][i], c='k', s=100, marker='x')
    elif point == 1:
        # versicolor
        vers = plt.scatter(X[:, 0][i], X[:, 1][i], c='b', s=100, marker='o')
    else:
        # virginica
        virg = plt.scatter(X[:, 0][i], X[:, 1][i], c='r', s=100, marker='^')

plt.legend((seto, vers, virg),
           ('Iris setosa', 'Iris versicolor', 'Iris virginica'),
           scatterpoints=1,
           loc='lower left',
           ncol=3,
           fontsize=22)
plt.xlabel(xlabel, fontsize=24)
plt.ylabel(ylabel, fontsize=24)
plt.xlim(xx.min(), xx.max())
plt.ylim(yy.min(), yy.max())
plt.xticks(())
plt.yticks(())
plt.title(title, fontsize=24)
plt.show()

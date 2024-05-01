# -*- coding: utf-8 -*-
"""Final

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12LKEG4mpKvQQ8APfqDKKjOmdgMYGte06
"""

pip install ucimlrepo

pip install requests

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix,
    roc_curve, roc_auc_score, classification_report
)
from scipy.stats import pointbiserialr, chi2_contingency
from sklearn.calibration import calibration_curve
from sklearn.model_selection import train_test_split, cross_val_score
import requests
from io import StringIO

# Set up visuals
sns.set_style("whitegrid")

# Function to fetch the Haberman dataset
def fetchHaberman():
    """ Fetches the Haberman dataset from the UCI Machine Learning Repository and returns it as a DataFrame. """
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/haberman/haberman.data"
    response = requests.get(url)
    data = StringIO(response.text)
    columnNames = ['Age', 'Year', 'Nodes', 'Status']
    df = pd.read_csv(data, names=columnNames)
    return df


# Function to load and preprocess the data
def loadData():
    """ Loads and preprocesses the Haberman dataset. Returns: DataFrame, a Preprocessed DataFrame. """
    return fetchHaberman()

# Function to preprocess the data
def processData(dataSet):
    """ Preprocesses the dataset by adjusting column values. """
    dataSet['Year'] = dataSet['Year'].apply(lambda x: 1900 + x)
    dataSet['Status'] = dataSet['Status'].apply(lambda x: 0 if x == 1 else 1)  # Switching survival/death mapping
    return dataSet

# Function to split the data into training and testing sets
def splitData(dataframe, testSize, randState):
    """ Splits the dataset into training and testing sets. Returns a tuple: Four DataFrames representing X_train, X_test, y_train, and y_test. """
    xData = dataframe.drop('Status', axis=1)
    yData = dataframe['Status']
    xTrain, xTest, yTrain, yTest = train_test_split(xData, yData, test_size=testSize, random_state=randState)
    return xTrain, xTest, yTrain, yTest

# Function to make predictions using a trained model
def predict(model, xTest):
    """ Predicts target labels using a trained model. Returns an array of Predicted labels. """
    yPrediction = model.predict(xTest)
    return yPrediction

# Function to evaluate model performance
def evalPerformance(yTest, yPred, yProba):
    """ Evaluates the performance of a classification model. Takes in yTest (array): True labels, yPred (array): Predicted labels, yProba (array): Predicted probabilities.
    Returns dict: Dictionary containing evaluation metrics, dict: Classification report, tuple: ROC curve data. """
    # Generate a classification report
    report = classification_report(yTest, yPred, target_names=['Survived', 'Not Survived'], output_dict=True, zero_division=0)

    # Calculate the ROC curve and AUC
    fpr, tpr, thresholds = roc_curve(yTest, yProba[:, 1])
    auc = roc_auc_score(yTest, yProba[:, 1])

    # Compile metrics into a dictionary
    metrics = {
        'Accuracy': accuracy_score(yTest, yPred),
        'Precision': precision_score(yTest, yPred, zero_division=0),
        'Recall': recall_score(yTest, yPred, zero_division=0),
        'F1 Score': f1_score(yTest, yPred, zero_division=0),
        'ROC AUC': auc
    }

    return metrics, report, (fpr, tpr, auc)

# Function to calculate correlations
def calculateCorrelations(df):
    """ Calculates point-biserial correlations between features and target. Returns: a Dictionary containing correlation coefficients."""
    correlationCoeff = {}
    for column in df.columns.drop('Status'):
        correlation, _ = pointbiserialr(df[column], df['Status'])
        correlationCoeff[column] = correlation
    return correlationCoeff

# Function to perform chi-squared tests
def chiSquaredTest(df):
    """ Performs chi-squared tests for independence. Returns a dictionary containing chi-squared test results. """
    chiSqResults = {}
    for column in df.columns.drop('Status'):
        contingencyTable = pd.crosstab(df[column], df['Status'])
        chi2, pValue, dof, expected = chi2_contingency(contingencyTable)
        chiSqResults[column] = {'Chi-square statistic': chi2, 'p-value': pValue, 'Degrees of freedom': dof, 'Expected frequencies': expected}
    return chiSqResults

# Function to get user input for prediction
def getUserInput(ageRange, yearRange, nodesRange):
    """ Gets user input for prediction. Returns: a DataFrame of User input data. """
    while True:
        print("Would you like to predict within or outside the dataset? Predicting outside may be less accurate.")
        userChoice = input("Type 'within' or 'outside': ").strip().lower()
        if userChoice in ["within", "outside"]:
            break
        else:
            print("Invalid input! Please enter either 'within' or 'outside'.")

    if userChoice == "within":
        while True:
            age = int(input(f"Enter patient's age (range in dataset is {ageRange[0]} to {ageRange[1]}): "))
            if ageRange[0] <= age <= ageRange[1]:
                break
            print("Invalid age! Please enter a value within the specified range.")

        while True:
            year = int(input(f"Enter the year of operation (full year, range in dataset is {yearRange[0]} to {yearRange[1]}): "))
            if yearRange[0] <= year <= yearRange[1]:
                break
            print("Invalid year! Please enter a value within the specified range.")

        while True:
            nodes = int(input(f"Enter the number of positive axillary nodes detected (range in dataset is {nodesRange[0]} to {nodesRange[1]}): "))
            if nodesRange[0] <= nodes <= nodesRange[1]:
                break
            print("Invalid node count! Please enter a value within the specified range.")
    else:
        age = int(input("Enter patient's age: "))
        year = int(input("Enter the year of operation (full year): "))
        nodes = int(input("Enter the number of positive axillary nodes detected: "))

    return pd.DataFrame([[age, year, nodes]], columns=['Age', 'Year', 'Nodes'])

# Function to make predictions using a trained model
def makePrediction(model, inputData):
    """ Makes predictions using a trained model. Returns an array of Predicted labels. """
    prediction = model.predict(inputData)
    return prediction

# Function to visualize statistical analyses
def visualiseStats(allCorrelationCoeffs, allChiSqResults):
    """ Visualizes statistical analyses. """
    fig, ax = plt.subplots(1, 2, figsize=(15, 6))  # Modified to have one row and two columns

    # Collect all correlation coefficients and chi-squared statistics
    correlations = {feature: values for featureDict in allCorrelationCoeffs for feature, values in featureDict.items()}
    chi2_stats = {feature: values for featureDict in allChiSqResults for feature, values in featureDict.items()}

    # Bar plot for Point-Biserial Correlation Coefficients
    ax[0].bar(correlations.keys(), correlations.values(), color='dodgerblue')
    ax[0].set_title('Point-Biserial Correlation Coefficients')
    ax[0].set_ylabel('Correlation Coefficient')
    ax[0].set_xlabel('Variables')
    ax[0].set_xticks(range(len(correlations.keys())))  # Set tick positions
    ax[0].set_xticklabels(correlations.keys(), rotation=45, ha='right')  # Set tick labels

    # Bar plot for Chi-squared Test Statistics with p-values as labels
    bars = ax[1].bar(chi2_stats.keys(), [values['Chi-square statistic'] for values in chi2_stats.values()], color='salmon')
    ax[1].set_title('Chi-squared Test Statistics')
    ax[1].set_ylabel('Chi-square Statistic')
    ax[1].set_xlabel('Variables')
    ax[1].set_xticks(range(len(chi2_stats.keys())))  # Set tick positions
    ax[1].set_xticklabels(chi2_stats.keys(), rotation=45, ha='right')  # Set tick labels

    # Adding p-values as labels to each bar
    for bar, pValue in zip(bars, [values['p-value'] for values in chi2_stats.values()]):
        height = bar.get_height()
        ax[1].text(bar.get_x() + bar.get_width() / 2, height, f'p={pValue:.3f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.show()


# Function to perform cross-validation for machine learning models
def crossValidateMLModel(model, X, y, runs, featureName, modelName):
    """ Performs cross-validation for machine learning models. Returns a dictionary of cross-validation results. """
    scores = cross_val_score(model, X, y, cv=runs, scoring='accuracy')
    meanScore = np.mean(scores)
    stdDevScore = np.std(scores)
    return {'Fold Scores': scores, f'Mean Accuracy ({featureName}, {modelName})': meanScore, f'Standard Deviation ({featureName}, {modelName})': stdDevScore}

# Function to visualize cross-validation results
def visualizeCrossValid(cvResults, featureName, modelName):
    """ Visualizes cross-validation results. """
    scores = cvResults['Fold Scores']
    meanScore = cvResults[f'Mean Accuracy ({featureName}, {modelName})']
    stdDevScore = cvResults[f'Standard Deviation ({featureName}, {modelName})']

    fig, ax = plt.subplots(figsize=(15, 6))  # Adjusted to match the size of other plots

    ax.bar(range(1, len(scores) + 1), scores, color='skyblue', label='Fold Score')
    ax.axhline(y=meanScore, color='r', linestyle='--', label=f'Mean Accuracy')
    ax.fill_between(range(1, len(scores) + 1), meanScore - stdDevScore, meanScore + stdDevScore, color='gray', alpha=0.2, label=f'±1 std dev')
    ax.set_title(f'Cross-Validation Consistency of Accuracy for {modelName} - {featureName}')
    ax.set_xlabel('Fold Number')
    ax.set_ylabel('Accuracy')
    ax.set_xticks(range(1, len(scores) + 1))
    ax.legend()

    plt.show()

# Function to train logistic regression model
def logRegression(xTrain, yTrain):
    """ Trains a logistic regression model. Returns: LogisticRegression: Trained logistic regression model. """
    logReg = LogisticRegression(random_state=29, max_iter=1000)
    return logReg.fit(xTrain, yTrain)

# Function to train KNN model
def KNN(xTrain, yTrain, nNeighbors):
    """ Trains a KNN classifier. Returns: KNeighborsClassifier: Trained KNN model."""
    neigh = KNeighborsClassifier(n_neighbors=nNeighbors)
    return neigh.fit(xTrain, yTrain)

# Function to visualize model performance
def visualizePerformance(model, xTest, yTest, featureName, modelName):
    """ Visualizes model performance. Returns: dict: Performance metrics. """
    # Ensure we use only the columns that were used during model training
    xTestSubset = xTest[[featureName]]
    yPred = model.predict(xTestSubset)
    yProba = model.predict_proba(xTestSubset)

    # Evaluate performance
    cm = confusion_matrix(yTest, yPred)
    accuracy = accuracy_score(yTest, yPred)
    precision = precision_score(yTest, yPred, zero_division=0)
    recall = recall_score(yTest, yPred, zero_division=0)
    f1 = f1_score(yTest, yPred, zero_division=0)

    # Adjust the size of the entire plot to accommodate three subplots
    fig, ax = plt.subplots(1, 3, figsize=(21, 6))

    # Plot Confusion Matrix
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax[0])
    ax[0].set_title(f'Confusion Matrix: {modelName} - {featureName}')
    ax[0].set_xlabel('Predicted Labels')
    ax[0].set_ylabel('True Labels')
    ax[0].set_xticklabels(['Survived', 'Not Survived'])
    ax[0].set_yticklabels(['Survived', 'Not Survived'])

    # Plot Calibration Curve
    trueProb, predProb = calibration_curve(yTest, yProba[:, 1], n_bins=10)
    ax[1].plot(predProb, trueProb, marker='o', linestyle='-')
    ax[1].plot([0, 1], [0, 1], linestyle='--', color='gray')
    ax[1].set_xlabel('Mean Predicted Probability')
    ax[1].set_ylabel('Fraction of Positives')
    ax[1].set_title(f'Calibration Curve: {modelName} - {featureName}')
    ax[1].grid(True)

    # Plot ROC Curve
    fpr, tpr, _ = roc_curve(yTest, yProba[:, 1])
    auc = roc_auc_score(yTest, yProba[:, 1])
    ax[2].plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {auc:.2f})')
    ax[2].plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    ax[2].set_xlabel('False Positive Rate')
    ax[2].set_ylabel('True Positive Rate')
    ax[2].set_title(f'ROC Curve: {modelName} - {featureName}')
    ax[2].legend(loc="lower right")
    ax[2].grid(True)

    plt.tight_layout()
    plt.show()

    return {'accuracy': accuracy, 'precision': precision, 'recall': recall, 'f1_score': f1, 'roc_auc': auc}

# Main function to orchestrate the entire process
def main():
    df = loadData()
    print("Data loaded successfully.")

    processedDf = processData(df)
    print("Data processed successfully.")

    ageRange = (processedDf['Age'].min(), processedDf['Age'].max())
    yearRange = (processedDf['Year'].min(), processedDf['Year'].max())
    nodesRange = (processedDf['Nodes'].min(), processedDf['Nodes'].max())

    xTrain, xTest, yTrain, yTest = splitData(processedDf, testSize=0.2, randState=42)
    print("Data split into training and testing sets.")

    logisticModel = LogisticRegression(random_state=29, max_iter=1000).fit(xTrain, yTrain)
    knnModel = KNeighborsClassifier(n_neighbors=5).fit(xTrain, yTrain)

    allCorrelationCoeffs = []
    allChiSqResults = []

    userInput = getUserInput(ageRange, yearRange, nodesRange)

    logPrediction = makePrediction(logisticModel, userInput)
    knnPrediction = makePrediction(knnModel, userInput)

    accuracyLog = accuracy_score(yTest, logisticModel.predict(xTest))
    accuracyKNN = accuracy_score(yTest, knnModel.predict(xTest))

    print(f"\nPredicted survival status using Logistic Regression: {'Survived' if logPrediction[0] == 0 else 'Not Survived'}")
    print(f"Predicted survival status using KNN: {'Survived' if knnPrediction[0] == 0 else 'Not Survived'}")

    print(f"\nAccuracy of Logistic Regression model: {accuracyLog*100:.2f}%")
    print(f"Accuracy of KNN model: {accuracyKNN*100:.2f}%")
    comparisonLog = "better" if accuracyLog > 0.5 else "worse"
    comparisonKNN = "better" if accuracyKNN > 0.5 else "worse"
    print(f"This is {comparisonLog} than flipping a coin for Logistic Regression.")
    print(f"This is {comparisonKNN} than flipping a coin for KNN.")

    # Iterate over features for individual analysis
    for feature in ['Age', 'Year', 'Nodes']:
        print(f"\nAnalyzing feature: {feature}")

        # Train and evaluate Logistic Regression
        logisticModel = logRegression(xTrain[[feature]], yTrain)
        logisticMetrics = visualizePerformance(logisticModel, xTest, yTest, feature, modelName='Logistic Regression')
        print("Performance of Logistic Regression evaluated:", logisticMetrics)

        yProbaLog = logisticModel.predict_proba(xTest[[feature]])
        logMetrics, logReport, logROC = evalPerformance(yTest, logisticModel.predict(xTest[[feature]]), yProbaLog)

        # Train and evaluate KNN
        knnModel = KNN(xTrain[[feature]], yTrain, nNeighbors=5)
        knn_metrics = visualizePerformance(knnModel, xTest, yTest, feature, modelName='KNN')
        print("Performance of KNN evaluated:", knn_metrics)

        # Calculate statistical tests
        featureDF = processedDf[['Status', feature]]  # Isolating the feature and Status for analysis
        correlations = calculateCorrelations(featureDF)
        chiSqResults = chiSquaredTest(featureDF)
        allCorrelationCoeffs.append(correlations)
        allChiSqResults.append(chiSqResults)


        # Cross-validation
        logCvResults = crossValidateMLModel(logisticModel, xTrain[[feature]], yTrain, runs=5, featureName=feature, modelName='Logistic Regression')
        knnCvResults = crossValidateMLModel(knnModel, xTrain[[feature]], yTrain, runs=5, featureName=feature, modelName='KNN')

        print("\nCross-validation results for Logistic Regression -", feature)
        print(logCvResults)
        visualizeCrossValid(logCvResults, feature, 'Logistic Regression')

        print("\nCross-validation results for KNN -", feature)
        print(knnCvResults)
        visualizeCrossValid(knnCvResults, feature, 'KNN')


    # Visualize all statistical analyses at once after the loop
    visualiseStats(allCorrelationCoeffs, allChiSqResults)

if __name__ == "__main__":
    main()
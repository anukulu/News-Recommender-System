#!/usr/bin/env python
# coding: utf-8

# # Import Necessary Modules

# In[1]:


import pandas as pd
import numpy as np
import itertools
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, HashingVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression



# # Using Logistic Regression to Classify as FAKE or REAL


#Reading the Dataset from CSV file
data = pd.read_csv('./fake_or_real_news.csv', header=None)


#Splitting the Data into Train and Test with 0.33 as test sets
train_x, test_x, train_y, test_y = train_test_split(data[2], data[3])


data.head()


#Using the Tfid Vectorizer because the size of the dataset is Large
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_train_x = vectorizer.fit_transform(train_x)


#Now using the Logistic Regression Algorithm to characterize as Fake or Real
classifier = LogisticRegression()
classifier.fit(tfidf_train_x, train_y)



#After transform the test data will be stored as a float in case of TFID
tfidf_test_x = vectorizer.transform(test_x)
print(tfidf_test_x.shape)
tfidf_test_x


#Finding the Accuracy Score for the Algorithm
accuracy = cross_val_score(classifier, tfidf_test_x, test_y, cv=5)
acc = accuracy.mean()
print(acc * 100)


#Entering the news to check its validity
print("Enter the news you want to validate: \n\n")
news = [input()]
output = classifier.predict(vectorizer.transform(news))


print((output[0]+" ")*3+"!!!") 

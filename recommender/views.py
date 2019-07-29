from django.shortcuts import render
import numpy as np
import h5py
import operator
import time
import random

countTable = np.zeros((10,10), dtype=int)
controlVar = None
news = open("recommender/content.txt", encoding="UTF-8").read().split("----------")
topics = open("recommender/topics.txt", encoding="UTF-8").read().split("\n")
previousControlVarStore = None

#######
categories = open("recommender/categories.txt", 'r').read().split("\n")
categories1 = list(set(categories))
systemTime = time.time()
categoryAndTempClicks = {}
for category in categories1:
	categoryAndTempClicks[category] = 0
######

class News:
	def __init__(self, topic, content, index, category):
		self.topic = topic
		self.content = content
		self.index = index
		####
		self.category = category
		####

def index(request):
	global news
	global topics
	global categories
	categories2 = open("recommender/categories.txt", 'r').read().split("\n")
	setOfCategories = list(set(categories))
	random.shuffle(setOfCategories)

	# i = 0
	catego = []
	newsAndTopics = []
	newsAndTopics2 = {}
	for cat in setOfCategories:
		templist = []
		for ctgry in categories2:
			if(ctgry == cat):
				indx = categories2.index(ctgry)
				templist.append(indx)
				categories2[indx] = "ThisIsTheReplacementText"
		catego.append(templist)

	i = 0
	for categ in catego:
		j = 0 
		random.shuffle(categ)
		newsAndTopics = []
		for indx in categ:
			if(j < 5):
				newsAndTopics.append(News(topics[indx], news[indx], indx, categories[indx]))
				j = j + 1
		newsAndTopics2[setOfCategories[i]] = newsAndTopics
		i = i + 1

	# for topic in topics:
	# 	if (topic != ""):
	# 		newsAndTopics.append(News(topic, news[i], i, categories[i])) 
	# 		i = i + 1
	return render(request, "recommender/index.html", {'newsAndTopics2' : newsAndTopics2})

def content(request, category, newsId):
	global controlVar
	global news
	global topics
	global previousControlVarStore
	categories3 = open("recommender/categories.txt", 'r').read().split("\n")
	recommendations2 = []

	#####
	global categories
	global categoryAndTempClicks
	defaultValue = '1'
	if(request.COOKIES.get(category, None) == None):
		currentValue = defaultValue
		categoryAndTempClicks[category] = int(defaultValue)
	else:
		currentValue = str(int(request.COOKIES.get(category)) + 1)
		# print(category)
		categoryAndTempClicks[category] = (categoryAndTempClicks[category] + 1)

	maxCategory = GetMaxCategory(request)

	#####

	recommendations = []
	columnIndices = []
	previousControlVarStore = str(controlVar)
	controlVar = newsId
	categories3[controlVar] = "ThisIsTheReplacementText"

	if(previousControlVarStore != "None"):
		prevControl = int(previousControlVarStore)
		with h5py.File('recommender/countTable.h5', 'r') as hf:
			data = hf['countDataset'][:]
			data[prevControl][controlVar] += 1
		print(data)
		if(sum(data[controlVar]) > 0):
			probabilityCount = np.array([x/sum(data[controlVar]) for x in data[controlVar]])
			sortedProbability = np.sort(probabilityCount)[::-1]
			print(sortedProbability)
			for probs in sortedProbability:
				if(probs > 0):
					columnIndexList = np.where(probabilityCount == probs)
					if(len(columnIndexList[0]) > 1):
						for indices in columnIndexList[0]:
							columnIndices.append(int(indices))
					else:
						columnIndices.append(int(columnIndexList[0][0]))
			columnIndices = set(columnIndices)
			print(columnIndices)
			for column in columnIndices:
				if(column != controlVar):
					recommendations.append(News(topics[column], news[column], column, categories[column]))
					categories3[column] = "ThisIsTheReplacementText"
		with h5py.File('recommender/countTable.h5', 'w') as hf:
			hf.create_dataset("countDataset",  data=data)
	newsContent = news[newsId]
	newsTopic = topics[newsId]
	
	numberOfRecommendations = 10 - len(recommendations)
	i = 0
	newsIndex = []
	for ctgry in categories3:
		if (i <= int(0.4 * numberOfRecommendations)):
			if ctgry == maxCategory:
				print("This is executed")
				indx = categories3.index(ctgry)
				newsIndex.append(indx)
				categories3[indx] = "ThisIsTheReplacementText"
				i = i + 1
		elif (int(0.4 * numberOfRecommendations) < i and i <= (0.6 * numberOfRecommendations)):
			if(ctgry == category):
				indx = categories3.index(ctgry)
				newsIndex.append(indx)
				categories3[indx] = "ThisIsTheReplacementText"
				i = i + 1
		elif ((0.6 * numberOfRecommendations) and i <= numberOfRecommendations):
			if(ctgry != category and ctgry != maxCategory):
				indx = categories3.index(ctgry)
				newsIndex.append(indx)
				categories3[indx] = "ThisIsTheReplacementText"
				i = i + 1
		else:
			break

	print(newsIndex)
	random.shuffle(newsIndex)

	for indx in newsIndex:
		newS = News(topics[indx], news[indx], indx, categories[indx])
		if(newS not in recommendations):
			recommendations2.append(newS)

	response =  render(request, "recommender/contentpage.html",  {'newsTopic': newsTopic, 'newsContent' : newsContent, 'recommendations': recommendations, 'recommendations2' : recommendations2})
	response.set_cookie(category, currentValue)
	return response

#####
def GetMaxCategory(request):
	global categories1
	global systemTime
	global categoryAndTempClicks
	categoryAndFactor = {}
	timeLap = 20
	difference = time.time() - systemTime

	if(difference > timeLap):
		systemTime = time.time()
		for category in categories1:
			if category in request.COOKIES:
				categoryAndTempClicks[category] = 0
	for category in categories1:
		if category in request.COOKIES:
			rateOfClicks = (categoryAndTempClicks[category] / timeLap)	# rate of clicks of that category 
			print(str(rateOfClicks))
			viewFactor = (int(request.COOKIES.get(category)) / sum([int(x) for x in request.COOKIES.values()]))
			determiningFactor = (0.4 * rateOfClicks + 0.6 * viewFactor)
			categoryAndFactor[category] = determiningFactor
			print(str(determiningFactor) + '\n')

	if (len(categoryAndFactor) == 0):
		return ('nothing')
	else:
		return(max(categoryAndFactor.items(), key=operator.itemgetter(1))[0])
####
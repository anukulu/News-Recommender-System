from django.shortcuts import render
import numpy as np
import h5py
import operator
import time

countTable = np.zeros((10,10), dtype=int)
controlVar = None
news = open("recommender/content.txt", 'r').read().split("----------")
topics = open("recommender/topics.txt", 'r').read().split("\n")

#######
categories = open("recommender/categories.txt", "r").read().split("\n")
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

	i = 0
	newsAndTopics = []
	for topic in topics:
		newsAndTopics.append(News(topic, news[i], i, categories[i])) 
		i = i + 1
	return render(request, "recommender/index.html", {'newsAndTopics' : newsAndTopics})

def content(request, category, newsId):
	global controlVar
	global news
	global topics

	#####
	global categories
	global categoryAndTempClicks
	defaultValue = '1'
	if(request.COOKIES.get(category, None) == None):
		currentValue = defaultValue
		categoryAndTempClicks[category] = int(defaultValue)
	else:
		currentValue = str(int(request.COOKIES.get(category)) + 1)
		categoryAndTempClicks[category] = (categoryAndTempClicks[category] + 1)

	maxCategory = GetMaxCategory(request)
	#####

	recommendations = []
	columnIndices = []
	previousControlVarStore = open("recommender/control.txt", "w").write(str(controlVar))
	controlVar = newsId
	previousControlVar = open("recommender/control.txt", 'r').read()

	if(previousControlVar != "None"):
		prevControl = int(previousControlVar)
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
		with h5py.File('recommender/countTable.h5', 'w') as hf:
			hf.create_dataset("countDataset",  data=data)
	newsContent = news[newsId]
	newsTopic = topics[newsId]
	response =  render(request, "recommender/contentpage.html",  {'newsTopic': newsTopic, 'newsContent' : newsContent, 'recommendations': recommendations, 'maxCategory' : maxCategory})
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
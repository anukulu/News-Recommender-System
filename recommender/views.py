from django.shortcuts import render
import numpy as np
import h5py

countTable = np.zeros((10,10), dtype=int)
controlVar = None

class News:
	def __init__(self, topic, content, index):
		self.topic = topic
		self.content = content
		self.index = index

def index(request):
	news = open("recommender/content.txt", 'r').read().split("----------")
	topics = open("recommender/topics.txt", 'r').read().split("\n")
	
	i = 0
	newsAndTopics = []
	for topic in topics:
		newsAndTopics.append(News(topic, news[i], i)) 
		i = i + 1
	return render(request, "recommender/index.html", {'newsAndTopics' : newsAndTopics})

def content(request, newsId):
	global controlVar
	recommendations = []
	previousControlVarStore = open("recommender/control.txt", "w").write(str(controlVar))
	controlVar = newsId
	previousControlVar = open("recommender/control.txt", 'r').read()
	if(previousControlVar != "None"):
		prevControl = int(previousControlVar)
		with h5py.File('recommender/countTable.h5', 'r') as hf:
			data = hf['countDataset'][:]
			data[prevControl][controlVar] += 1
		if(sum(data[controlVar]) > 0):
			probabilityCount = np.array([x/sum(data[controlVar]) for x in data[controlVar]])
			maxProbability = max(probabilityCount)
			columnIndex = int(np.where(probabilityCount == maxProbability)[0][0])
			news = open("recommender/content.txt", 'r').read().split("----------")
			topics = open("recommender/topics.txt", 'r').read().split("\n")
			recommendations.append(News(topics[columnIndex], news[columnIndex], columnIndex))
		with h5py.File('recommender/countTable.h5', 'w') as hf:
			hf.create_dataset("countDataset",  data=data)
	news = open("recommender/content.txt", 'r').read().split("----------")[newsId]
	return render(request, "recommender/contentpage.html",  {'newsContent' : news, 'recommendations': recommendations})
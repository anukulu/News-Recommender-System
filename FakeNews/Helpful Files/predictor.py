import pickle
import numpy as np

var = input("Please enter the news that you want to verify as fake or real: ")

#predicts whether the news is fake or not
def detecting_fake_news(var):
#logreg has the maximum accuracy so retrieving it
    load_model = pickle.load(open('final_logreg_model.sav', 'rb'))
    news = np.array([var])
    news = news.reshape(1,-1)
    #Working Up to here
    prediction = load_model.predict(news)
    prob = load_model.predict_proba(news)
    print("good")

    return (print("The given statement is ",prediction[0]),
        print("The truth probability score is ",prob[0][1]))


if __name__ == '__main__':
    detecting_fake_news(var)

import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import load_model
import random
import json
import pickle

nltk.download('punkt')
nltk.download('wordnet')

# Load the chatbot model and other necessary data
lemmatizer = WordNetLemmatizer()
model = load_model('chatbotmodel.h5')
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
intents = json.loads(open("intents.json").read())

# clean_up_sentences(sentence): Separate words from the input sentence
def clean_up_sentences(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

# bagw(sentence): Create a bag of words vector for the sentence
def bagw(sentence):
    sentence_words = clean_up_sentences(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

# predict_class(sentence): Predict the class of the input sentence
def predict_class(sentence):
    bow = bagw(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []

    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})

    return return_list

# get_response(intents_list, intents_json): Get a response based on intent
def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent'] if intents_list else 'default_fallback'
    list_of_intents = intents_json['intents']
    result = ""
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

# get_bot_response(message): Get the chatbot's response and tag probabilities
def get_bot_response(message):
    ints = predict_class(message)
    response = get_response(ints, intents)
    tag_probabilities = [{"intent": intent['intent'], "probability": intent['probability']} for intent in ints]
    return response, tag_probabilities


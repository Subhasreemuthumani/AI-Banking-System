import pickle

vectorizer = pickle.load(open("model/vectorizer.pkl","rb"))
category_model = pickle.load(open("model/category_model.pkl","rb"))
severity_model = pickle.load(open("model/severity_model.pkl","rb"))
root_model = pickle.load(open("model/rootcause_model.pkl","rb"))
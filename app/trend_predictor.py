import pandas as pd

def complaint_trends():

    data = pd.read_csv("data/complaints.csv")

    trend = data["Product"].value_counts()

    return trend.to_dict()
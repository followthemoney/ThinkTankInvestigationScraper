import pandas as pd
from pandas import json_normalize
import json

def load_ID(json_data):
    with open(json_data) as inputfile:
        my_json = json.load(inputfile) #Loads a list
    my_json = json_normalize(my_json)
    df = pd.DataFrame.from_dict(my_json['resultList.interestRepresentative'][0])
    df = df[df['registrationCategory']=="Think tanks and research institutions"]
    return df['identificationCode'].values

import pandas as pd 
import numpy as np 

def load_data(file_path):
    data = pd.read_csv(file_path)

    return data 
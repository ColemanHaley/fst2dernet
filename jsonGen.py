import pandas as pd 
DIR = "networks/ess.tsv"

data = pd.read_table(DIR)

root2idx = {}
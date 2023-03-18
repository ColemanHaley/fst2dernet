import pandas as pd 
import re 
import pickle
import numpy as np 
DIR = "networks/ess1.tsv"  
data = pd.read_table(DIR)
for i in range(len(data["idx"])):
    if not np.isnan(data["idx"][i]):
        data["lookup"][i] = int(data["idx"][i]) #a lookup index for each root
data["idx"] = list(map(lambda x:str(x),data["idx"]))
data["parent"] = list(map(lambda x:str(x),data["parent"])) 
idx = data["idx"]
for i in range(1,len(idx)):
    if re.search(r"[0-9]\.[0-9]1",idx[i]): 
        idx[i-1]+="0" #the 0 in numbers like 3.10, 4.20... sometimes disappear in the tsv file. 


pickle.dump(data,open("networks/ess.data","wb"))


import pandas as pd 
import re 
import pickle
import numpy as np
import json 
import sys 
DIR = "networks/ess1.data"
data = pickle.load(open(DIR,"rb"))
word2id = {}

for i,r in data.iterrows():
    if re.search(r"[0-9]\.0$",r["idx"]):
        id = r["idx"]
        id = int(float(id))
        word2id[r["raw"]] = id
def get_word_df(root:str):
    """
    root: a Yup'ik word that will be the parent node in the derivational network.

    return: a dataframe object that contains all the derivationally related words with the root. 
    """

    id = word2id[root]
    df = data[data["lookup"]==id]
    return df 

def add_child_to_parent(parent,js:dict,child):
    """
    add a children (derived word) to its parent (root) in the nested json dictionary.

    parent: the parent to which the child is added 
    js: the js dictionary whose inner structure to be changed 

    """
    cur_parent = js["name"]
    if cur_parent == parent and len(js)==1: #add children list if the target root doesn't have children
        js["children"] = []
    if len(js) == 1:#exit when the current root doesn't have children
        return 
    if cur_parent == parent: #add child to children. 
        js["children"].append({"name":child})
        return 
    for i in range(len(js["children"])):
        add_child_to_parent(parent,js["children"][i],child) #continue exploring other children

def construct_js(root):
    """
    Construct a json dictionary representing the derivational network, given the root. 

    return: a json dictionary. 
    """
    info = get_word_df(root)
    index = info.index
    js = {}
    for i in range(len(index)):
        raw = info.iloc[i]["raw"]
        parent_id = info.iloc[i]["parent"]
     
        if parent_id == "nan": 
            js["name"] = raw
            js["children"] = []
        else: 
            if i>0 and raw == info.iloc[i-1]["raw"]: #remove duplicated form from the js dict.
                continue

            parent = info[info["idx"] == parent_id]["raw"].item()
            add_child_to_parent(parent,js,raw)

    json.dump(js,open("jsons/{}.json".format(root),"w"))
    return js 

if __name__ == "__main__":
    root = "aanuuq"
    print(construct_js(root)) 
    
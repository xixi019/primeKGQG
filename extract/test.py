import os
import json
import ipdb
# This script is to read the json files generated by endpoint.py and count statistics.
# And to convert the rdf forms into textual form and save in a file textualized.json under the same directory.
# this seprated the files by train test split and count statistics.
from tqdm import tqdm
import random
from string import Template
from SPARQLWrapper import SPARQLWrapper, JSON
import time
from sklearn.model_selection import train_test_split

# this function is used to calculate how many triples in specific file
def get_stat():
    for filename in os.listdir(os.getcwd()):
        if filename.endswith('.json') and filename in ['0_test.json']:
            with open(os.path.join(os.getcwd(), filename), 'r') as f: 
                triples = json.loads(f)
                print(triples[0], filename)
                con = dict()
                for i in triples:
                    for value in i.values():
                        if value["value"] in con:
                            con[value["value"]] += 1
                        if value["value"] not in con:
                            con[value["value"]] = 0
                ipdb.set_trace()
                print(f'This file {filename} has {len(con)} different entities, with totaly {len(triples)} graphs matched.')
    return

def get_answer(query):
    out = list()
    endpoint = "http://sems-coypu-4.informatik.uni-hamburg.de:8890/sparql/"
    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(JSON)
    if not isinstance(query, str):
        query = query.safe_substitute()

    try:
        sparql.setQuery(
        query
        )
    except:
        pass
    try:
        ret = sparql.queryAndConvert()

        for r in ret["results"]["bindings"]:
            out.append(r)
#        return ret["results"]["bindings"]
    except Exception as e:
        print(e)
    time.sleep(2) 
    return out
# main function to: 1. get the triple files in the same directory; 
# 2. convert the triples to text form
# 3. save in a json file
def convert(entDict:dict):
    '''
    entDict: dictionary from getEntDIct function
    return the number of triple processed and a line of info
    '''
    out = []
    for filename in [i for i in os.listdir(os.getcwd()) if i.endswith("json")]:
        if filename.endswith('.json'):
            with open(os.path.join(os.getcwd(), filename), 'r') as f:   
                triples = json.load(f)
                for triple in tqdm(triples):
                    # extract the triplea based on the subgraph-pattern
                    if filename.startswith("0"):
                        text_triple = {"type":filename.split("json")[0]}
                        subgraphs = [(triple["subj"], triple["prop"]["value"], triple["obj"])]
                        for idx in range(len(subgraphs)):
                            subgraphs[idx] = ["<" + i["value"] + ">"if isinstance(i, dict) else "<" + i + ">" for i in  subgraphs[idx]]
                        answer = random.choice([subgraphs[0][0], subgraphs[0][1], subgraphs[0][2]])
                        subgraphs = [(Eid2label(triple["subj"], entDict), triple["prop"]["value"].split('/vocab/')[-1], Eid2label(triple["obj"], entDict))]
                        if "vocab" in answer:
                            text_triple["ans_type"] = "rel"
                            answer = answer.split('/vocab/')[-1]
                        else:
                            answer = Eid2label(answer.strip(">"), entDict)
                            text_triple["ans_type"] = "ent"
                        text_triple["value"] = subgraphs
                        text_triple["answer_"] = answer



                    if filename.startswith("1_v2.json"):
                        text_triple = { "type":filename.split("json")[0]}
                        subgraphs = [(triple["subj"], triple["prop1"]["value"], triple["obj1"]), 
                                    (triple["subj"], triple["prop2"]["value"], triple["obj2"])]
                        for idx in range(len(subgraphs)):
                            subgraphs[idx] = ["<" + i["value"] + ">"if isinstance(i, dict) else "<" + i + ">" for i in  subgraphs[idx]]
                        answer = random.choice([subgraphs[0][2], subgraphs[0][1], subgraphs[1][1]])
                        subgraphs = [(Eid2label(triple["subj"], entDict), triple["prop1"]["value"].split('/vocab/')[-1], Eid2label(triple["obj1"], entDict)), 
                                    (Eid2label(triple["subj"], entDict), triple["prop2"]["value"].split('/vocab/')[-1], Eid2label(triple["obj2"], entDict))]
                        if "vocab" in answer:
                            text_triple["ans_type"] = "rel"
                            answer = answer.split('/vocab/')[-1]
                        else:
                            answer = Eid2label(answer.strip(">"), entDict)
                            text_triple["ans_type"] = "ent"
                        text_triple["value"] = subgraphs
                        text_triple["answer_"] = answer

                    if filename.startswith("2"):
                        text_triple = {"type":filename.split("json")[0]}
                        subgraphs = [(triple["subj"], triple["prop1"]["value"], triple["obj1"]), 
                                    (triple["obj1"], triple["prop2"]["value"], triple["obj2"])]
                        for idx in range(len(subgraphs)):
                            subgraphs[idx] = ["<" + i["value"] + ">"if isinstance(i, dict) else "<" + i + ">" for i in  subgraphs[idx]]
                        answer = random.choice([subgraphs[0][2], subgraphs[0][1], subgraphs[1][1]])
                        subgraphs = [(Eid2label(triple["subj"], entDict), triple["prop1"]["value"].split('/vocab/')[-1], Eid2label(triple["obj1"], entDict)), 
                                    (Eid2label(triple["subj"], entDict), triple["prop2"]["value"].split('/vocab/')[-1], Eid2label(triple["obj2"], entDict))]
                        if "vocab" in answer:
                            answer = answer.split('/vocab/')[-1]
                            text_triple["ans_type"] = "rel"
                        else:
                            answer = Eid2label(answer.strip(">"), entDict)
                            text_triple["ans_type"] = "ent"
                        text_triple["value"] = subgraphs
                        text_triple["answer_"] = answer
        
                    if filename.startswith("3"):
                        text_triple = { "type":filename.split("json")[0]}
                        subgraphs = [(triple["subj"], triple["prop1"]["value"], triple["obj1"]), 
                                    (triple["subj"], triple["prop2"]["value"], triple["obj2"]),
                                  (triple["obj1"], triple["prop3"]["value"], triple["subj"])]
                        for idx in range(len(subgraphs)):
                            subgraphs[idx] = ["<" + i["value"] + ">"if isinstance(i, dict) else "<" + i + ">" for i in  subgraphs[idx]]
                        answer = random.choice([subgraphs[0][0], subgraphs[0][1], subgraphs[1][1], subgraphs[2][1]])
                        subgraphs = [(Eid2label(triple["subj"], entDict), triple["prop1"]["value"].split('/vocab/')[-1], Eid2label(triple["obj1"], entDict)), 
                                    (Eid2label(triple["subj"], entDict), triple["prop2"]["value"].split('/vocab/')[-1], Eid2label(triple["obj2"], entDict)),
                                    (Eid2label(triple["obj1"], entDict), triple["prop3"]["value"].split('/vocab/')[-1], Eid2label(triple["subj"], entDict))]       
                        if "vocab" in answer:
                            text_triple["ans_type"] = "rel"
                            answer = answer.split('/vocab/')[-1]
                        else:
                            text_triple["ans_type"] = "ent"
                            answer = Eid2label(answer.strip(">"), entDict)
                        text_triple["value"] = subgraphs
                        text_triple["answer_"] = answer


                    if filename.startswith("4_v2"):
                        text_triple = { "type":filename.split("json")[0]}
                        subgraphs = [(triple["subj1"], triple["prop1"]["value"], triple["obj"]), 
                                    (triple["subj2"], triple["prop2"]["value"], triple["obj"])]                                  
                        for idx in range(len(subgraphs)):
                            subgraphs[idx] = ["<" + i["value"] + ">"if isinstance(i, dict) else "<" + i + ">" for i in  subgraphs[idx]]
                        answer = random.choice([subgraphs[0][2], subgraphs[0][1], subgraphs[1][1]])
                        subgraphs = [(Eid2label(triple["subj1"], entDict), triple["prop1"]["value"].split('/vocab/')[-1], Eid2label(triple["obj"], entDict)), 
                                    (Eid2label(triple["subj2"], entDict), triple["prop2"]["value"].split('/vocab/')[-1], Eid2label(triple["obj"], entDict))]    
                        if "vocab" in answer:
                            text_triple["ans_type"] = "rel"
                            answer = answer.split('/vocab/')[-1]
                        else:
                            text_triple["ans_type"] = "ent"
                            answer = Eid2label(answer.strip(">"), entDict)
                        text_triple["value"] = subgraphs
                        text_triple["answer_"] = answer

                    if filename.startswith("7"):
                        text_triple = { "type":filename.split("json")[0]}
                        subgraphs = [(triple["subj"], triple["prop1"]["value"], triple["obj1"]), 
                                    (triple["obj1"], triple["prop2"]["value"], triple["obj2"]), 
                                    (triple["obj1"], triple["prop3"]["value"], triple["subj"])]
                        
                        for idx in range(len(subgraphs)):
                            subgraphs[idx] = ["<" + i["value"] + ">"if isinstance(i, dict) else "<" + i + ">" for i in  subgraphs[idx]]
                        answer = random.choice([subgraphs[0][2], subgraphs[0][1], subgraphs[1][1], subgraphs[2][1]])
                        subgraphs = [(Eid2label(triple["subj"], entDict), triple["prop1"]["value"].split('/vocab/')[-1], Eid2label(triple["obj1"], entDict)), 
                                    (Eid2label(triple["obj1"], entDict), triple["prop2"]["value"].split('/vocab/')[-1], Eid2label(triple["obj2"], entDict)), 
                                    (Eid2label(triple["obj1"], entDict), triple["prop3"]["value"].split('/vocab/')[-1], Eid2label(triple["subj"], entDict))]
                        if "vocab" in answer:
                            text_triple["ans_type"] = "rel"
                            answer = answer.split('/vocab/')[-1]
                        else:
                            text_triple["ans_type"] = "ent"
                            answer = Eid2label(answer.strip(">"), entDict)
                        text_triple["value"] = subgraphs
                        text_triple["answer_"] = answer

                    if filename.startswith("8"):
                        text_triple = { "type":filename.split("json")[0]}
                        subgraphs = [(triple["subj"], triple["prop1"]["value"], triple["obj1"]), 
                                    (triple["obj1"], triple["prop2"]["value"], triple["obj2"]), 
                                    (triple["obj1"], triple["prop3"]["value"], triple["subj"]), 
                                    (triple["obj2"], triple["prop4"]["value"], triple["obj1"])]
                        for idx in range(len(subgraphs)):
                            subgraphs[idx] = ["<" + i["value"] + ">"if isinstance(i, dict) else "<" + i + ">" for i in  subgraphs[idx]]
                        answer = random.choice([subgraphs[0][2], subgraphs[0][1], subgraphs[1][1], subgraphs[2][1], subgraphs[3][1]])
                        subgraphs = [(Eid2label(triple["subj"], entDict), triple["prop1"]["value"].split('/vocab/')[-1], Eid2label(triple["obj1"], entDict)), 
                                                  (Eid2label(triple["obj1"], entDict), triple["prop2"]["value"].split('/vocab/')[-1], Eid2label(triple["obj2"], entDict)), 
                                                  (Eid2label(triple["obj1"], entDict), triple["prop3"]["value"].split('/vocab/')[-1], Eid2label(triple["subj"], entDict)), 
                                                  (Eid2label(triple["obj2"], entDict), triple["prop4"]["value"].split('/vocab/')[-1], Eid2label(triple["obj1"], entDict))]
                        if "vocab" in answer:
                            text_triple["ans_type"] = "rel"
                            answer = answer.split('/vocab/')[-1]
                        else:
                            text_triple["ans_type"] = "ent"
                            answer = Eid2label(answer.strip(">"), entDict)
                        text_triple["value"] = subgraphs
                        text_triple["answer_"] = answer
                    
                    if filename == ("4e_v2.json"):
                        text_triple = { "type":filename.split("json")[0]}
                        subgraphs = [(triple["subj1"], triple["prop1"]["value"], triple["obj1"]), 
                                    (triple["obj1"], triple["prop2"]["value"], triple["obj2"]), 
                                    (triple["obj2"], triple["prop3"]["value"], triple["obj3"])]
                        for idx in range(len(subgraphs)):
                            subgraphs[idx] = ["<" + i["value"] + ">"if isinstance(i, dict) else "<" + i + ">" for i in  subgraphs[idx]]
                        answer = random.choice([subgraphs[0][0], subgraphs[0][1], subgraphs[0][2], subgraphs[1][1], subgraphs[1][2], subgraphs[2][1], subgraphs[2][2]])
                        subgraphs = [(Eid2label(triple["subj1"], entDict), triple["prop1"]["value"].split('/vocab/')[-1], Eid2label(triple["obj1"], entDict)), 
                                    (Eid2label(triple["obj1"], entDict), triple["prop2"]["value"].split('/vocab/')[-1], Eid2label(triple["obj2"], entDict)), 
                                    (Eid2label(triple["obj2"], entDict), triple["prop3"]["value"].split('/vocab/')[-1], Eid2label(triple["obj3"], entDict))]
                        if "vocab" in answer:
                            text_triple["ans_type"] = "rel"
                            answer = answer.split('/vocab/')[-1]
                        else:
                            text_triple["ans_type"] = "ent"
                            answer = Eid2label(answer.strip(">"), entDict)
                        text_triple["value"] = subgraphs
                        text_triple["answer_"] = answer

                    if filename == ("4f_v2.json"):
                        text_triple = { "type":filename.split("json")[0]}
                        subgraphs = [(triple["subj1"], triple["prop1"]["value"], triple["obj1"]), 
                                    (triple["subj1"], triple["prop2"]["value"], triple["obj2"]), 
                                    (triple["subj1"], triple["prop3"]["value"], triple["obj3"])]
                        for idx in range(len(subgraphs)):
                            subgraphs[idx] = ["<" + i["value"] + ">"if isinstance(i, dict) else "<" + i + ">" for i in  subgraphs[idx]]
                        answer = random.choice([subgraphs[0][0], subgraphs[0][1], subgraphs[1][1], subgraphs[2][1]])
                        subgraphs = [(Eid2label(triple["subj1"], entDict), triple["prop1"]["value"].split('/vocab/')[-1], Eid2label(triple["obj1"], entDict)), 
                                    (Eid2label(triple["subj1"], entDict), triple["prop2"]["value"].split('/vocab/')[-1], Eid2label(triple["obj2"], entDict)), 
                                    (Eid2label(triple["subj1"], entDict), triple["prop3"]["value"].split('/vocab/')[-1], Eid2label(triple["obj3"], entDict))]
                        if "vocab" in answer:
                            answer = answer.split('/vocab/')[-1]
                            text_triple["ans_type"] = "rel"
                        else:
                            answer = Eid2label(answer.strip(">"), entDict)
                            text_triple["ans_type"] = "ent"
                        text_triple["value"] = subgraphs
                        text_triple["answer_"] = answer


                    # filter out the triples with null values, resulted from long id which are falsely created
                    for text_graph in text_triple["value"]:
                        if None in text_graph:
                            text_triple = None
                            break
                    if text_triple:
                        out.append(text_triple)



    with open("total/for_submission.json", 'w') as f:
        json.dump(out, f, indent=4)

    f.close()
    print(f"{len(out)} textualized triples have beem created")
    return


# helper function to convert the long EID to text form
def Eid2label(triple, entDict:dict):
    '''
    id: triple saved in the json file from endpoint output
    labe: textual label
    '''
    if isinstance(triple, dict):
        triple = triple["value"]
    id = triple.split("node/")[-1]
    if len(id) <= 10:
        return entDict[id]
    return None


# load the entity ID2Label dictionary 
def getEntDIct(filename:str) -> dict:
    '''
    filename: the address of the dictionary generated by reading kg.csv file
    '''
    with open(filename) as f:
        entDict = json.load(f)[0]
    f.close()
    return entDict

# check the duplicate relation percentage in different files
def compare():
    num_1 = {}
    num_2 = {}

    for filename in os.listdir(os.getcwd()):
        if filename =="12_v2.json":
            with open(os.path.join(os.getcwd(), filename), 'r') as f: 
                triples = json.load(f)
                for triple in triples:
                    if triple["prop1"] == triple["prop5"]:
                        if triple["prop1"]["value"] in num_1:
                            num_1[triple["prop1"]["value"]] += 1
                        else:
                           num_1[triple["prop1"]["value"]] = 0
                    if triple["prop2"] == triple["prop4"]:
                        if triple["prop2"]["value"] in num_2:
                            num_2[triple["prop2"]["value"]] += 1
                        else:
                           num_2[triple["prop2"]["value"]] = 0
    print(num_1, num_2)
    return    

def stat():
    file = "/storage/yan/primekg/generatedTriple/total/full.json"
    
    with open (file, 'r') as f:
        triples = json.loads(f.read())
        new = list()
        for triple in triples:
            if "noAsso" in triple["type"]:
                continue
            if len(triple["answer_sparql"]) == 0:
                continue
            else:
                new.append(triple)
        print(len(new))
        train, test = train_test_split(new, test_size=0.4)
        val, test = train_test_split(test, test_size=0.5)
        print(get_num(train))
        print(get_num(test))
        print(get_num(val))
        with open("total/final_test.json", 'w') as f:
            json.dump(test, f, indent=4)
        with open("total/final_train.json", 'w') as f:
            json.dump(train, f, indent=4)
        with open("total/final_val.json", 'w') as f:
            json.dump(val, f, indent=4)

    return
def get_num(triples):
    ents, rel = [], []
    node_2, node_3, node_4, rel_ans = 0, 0, 0 ,0
    for triple in triples:
        subgraph = triple["value"]
        for line in subgraph:
            ents.append(line[0])
            rel.append(line[1])
            ents.append(line[2])
        if "0" in triple["type"]:
            node_2 += 1
        elif "4e" in triple["type"] or "4f" in triple["type"]:
            node_4 += 1
        else:
            node_3 += 1
        try:
            if triple["ans_type"] == "rel":
                rel_ans += 1
        except KeyError:
            pass

    return len(ents), len(rel), len(set(ents)),len(set(rel)), node_2, node_3, node_4, rel_ans, len(triples)

if __name__ == "__main__":
    # convert ids to labels
#    entDict = getEntDIct("/storage/yan/primekg/kg/ent_dict.json")
#    convert(entDict)
    stat()
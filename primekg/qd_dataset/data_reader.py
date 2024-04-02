import json
import ipdb
from rdflib import Graph
from wikidata.client import Client
import requests
from tqdm import tqdm
import time
from SPARQLWrapper import SPARQLWrapper, JSON
import re

# for SQB
class Convert:
    def __init__(self):
        # from freebaseID to wikidataID, abandoned after sparql is used
#        self.mapping = self.load_mapping()
        # wikidata client 
        self.client = Client() 
        self.data = []

    # main function to load the sqb json file to triples for evaluation in attribute self.data
    def load_SQB(self,):
        with open("/storage/yan/primekg/qg_dataset/SQB/sqb_dev.json") as f:
            data = json.load(f)
            for pair in tqdm(data):
                question = pair["question"]
                triple = [pair["subject_text"], self.Rel2Text(pair["relation"])[0], self.Id2Text(pair["object"])]
                triple = [pair["subject_text"], pair["relation"], self.Id2Text(pair["object"])]
                # can not find the entity id in freebase dump 2013
                if not triple[-1]:
                    continue
                rel_fact = self.Rel2Text(pair["relation"])[1]
                self.data.append({"value":[triple], "answer":triple[-1], "question":question, "additional_fct":rel_fact})
        print(f"We have processed {len(self.data)} of data in sqb_dev. Example is {self.data[0]}")
        return

    # input a freebase id and output the label based
    # to be replaced by using sparql endpoint
    def Id2Text(self, id="m.0gwrvq_"):
        endpoint = "http://localhost:8890/sparql"
        sparql = SPARQLWrapper(endpoint)
        sparql.setReturnFormat(JSON)
        
        sparql.setQuery(
            """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT DISTINCT ?label
                WHERE {
                <http://rdf.freebase.com/ns/m.0bmdj0x> rdfs:label ?label.
                }
                """.replace("m.0bmdj0x", id)
        )

        try:
            ret = sparql.queryAndConvert()

            for r in ret["results"]["bindings"]:
                if r["label"]["xml:lang"] == "en":
                    out = r["label"]["value"]
                    return out
    #        return ret["results"]["bindings"]
        except Exception as e:
            print(e)
        time.sleep(2) 
        return None

    # input a freebase relation and output the label  and a pair of label info based on the template:“the relation  is of type in domain.”
    def Rel2Text(self, rel="media_common.netflix_genre.titles"):
        text = rel.split(".")
        label = text[-1].replace("_", " ")
        label_info = "[the relation " + text[-1].replace("_", " ") + "] [is of type " + text[1].replace("_", " ") + "] [in domain " + text[0].replace("_", " ") + "]."
        return label, label_info

    def load_mapping(self, ):
        g = Graph()
        mapping = dict()
        g.parse("/storage/yan/fb2w.nt")
        for pair in g:
            mapping[pair[0].split("/")[-1]] = pair[-1].split("/")[-1]
        return mapping

    def save_sqb(self,):
        self.load_SQB()
        with open("Full_processed_sqb_dev.json" , "w") as f:
            json.dump(self.data, f, indent=4)
        return

# for loading webSP
class load_webSP:
    def __init__(self):
        self.triples = list()
        
    def read_file(self,):
        with open("/storage/yan/primekg/qg_dataset/webSP/test.json") as f:
            file = json.load(f)
            num = len(file["Questions"])
            print(f"There are {num} pairs in the file")
            for pair in tqdm(file["Questions"]):
                qid = pair["QuestionId"]
                question = pair["RawQuestion"]
                answer = pair["Parses"][0]["Answers"]
                answer_text = list()
                for i in answer:
                    if i["AnswerType"] == "Entity":
                        answer_text.append(i["EntityName"])
                    else:
                        answer_text.append(i["AnswerArgument"])
                answer_text = "; ".join(answer_text)
                out ={"Qtype":qid, 
                    "QuestionId":qid,
                    "question":question,
                    "answer":answer_text,
                    "value":[],
                    "additional_fct":[]}
                relation = pair["Parses"][0]["InferentialChain"]
                subject = pair["Parses"][0]["TopicEntityName"]
                try:
                    a = len(pair["Parses"][0]["InferentialChain"])
                except TypeError:
                    continue
                if len(relation) ==1:
                    out["Qtype"]  = 1
                else:
                    out["Qtype"]  = 2

                for rel in relation:
                    out["value"].append([subject, rel, answer_text])
                    # turns out the added value method does work well with LLM
                    _, added_info = self.Rel2Text(rel)
                    out["additional_fct"].append(added_info)
                self.triples.append(out)
        return 

            
    def Rel2Text(self, rel="media_common.netflix_genre.titles"):
        text = rel.split(".")
        label = text[-1].replace("_", " ")
        label_info = "[the relation " + text[-1].replace("_", " ") + "] [is of type " + text[1].replace("_", " ") + "] [in domain " + text[0].replace("_", " ") + "]."
        return label, label_info


    def save(self,):
        filename = "/storage/yan/primekg/qg_dataset/webSP/processed_webSP.json"
        with open(filename, "w") as f:
            json.dump(self.triples, f, indent=4)
        print(f"{len(self.triples)} triples has been saved in the file {filename}")
        one_hop = [i for i in self.triples if i["Qtype"]==1]
        two_hop = [i for i in self.triples if i["Qtype"]==2]
        with open( "/storage/yan/primekg/qg_dataset/webSP/processed_webSP_1hop.json", "w") as f:
            json.dump(one_hop, f, indent=4)
        print(f"{len(one_hop)} triples has been saved in the file {filename} for 1hop")
        with open( "/storage/yan/primekg/qg_dataset/webSP/processed_webSP_2hop.json", "w") as f:
            json.dump(two_hop, f, indent=4)
        print(f"{len(two_hop)} triples has been saved in the file {filename} for 2hop")
        return

class load_lcquad:
    def __init__(self):
        self.triples = list()


    def read_file(self,):
        with open ("/storage/yan/primekg/qg_dataset/lc-quad/test.json", "r") as f:
            pairs = json.load(f)
            for pair in tqdm(pairs):
                # we do not support count operation yet
                if "count" in pair["sparql_query"] or "?x" in pair["sparql_query"]:
                    continue
                out = dict()
                out["question"] = pair["corrected_question"]
                out["id"] = pair["_id"]
                query = pair["sparql_query"]
                answer = self.get_answer(query)
                if len(answer) != 0:
                    try:
                        answer_text = [i["uri"]["value"] for i in answer]
                        answer_text = "; ".join(answer_text)
                        out["answer"] = answer_text.split("/")[-1]
                        print(out["answer"])
                    except KeyError:
                        answer_text = [i["callret-0"]["value"] for i in answer]
                else:
                    continue
    
                out["value"] = self.extract(query, answer_text)

                self.triples.append(out)
        return 
     
    # for loading the answer from Lc_quad
    def get_answer(self, query):
        out = list()
        endpoint = "http://dbpedia.org/sparql"
        sparql = SPARQLWrapper(endpoint)
        sparql.setReturnFormat(JSON)
        
        sparql.setQuery(
           query
        )

        try:
            ret = sparql.queryAndConvert()

            for r in ret["results"]["bindings"]:
                out.append(r)
        except Exception as e:
            print(e)
        time.sleep(2)
        
        return out

    # exract triple from sparql with regular expression
    def extract(self, query, answer="answer_blank"):
        value = list()
        patterns = query.strip("} .").split("WHERE {")[-1].strip(" }")
        patterns = [i.strip('') for i in patterns.split(". ") if len(i)>2]
        for pattern in patterns:
            items = pattern.split(" ")
            for idx in range(len(items)):
                if "resource" in items[idx]:
                    items[idx] =  items[idx].split("resource/")[-1].strip(">")
                if "property" in items[idx]:
                    items[idx] =  items[idx].split("property/")[-1].strip(">")
                if "ontology" in items[idx]:
                    items[idx] =  items[idx].split("ontology/")[-1].strip(">")
                if "22-rdf-syntax-ns#" in items[idx]:
                    items[idx] =  items[idx].split("22-rdf-syntax-ns#")[-1].strip(">")
                if "?uri" in items[idx]:
                    items[idx] =  answer
            if '' in items:
                items.remove('')
            if not len(items) == 3:
                items.remove('')
            assert len(items) ==3
            value.append(items)
        return value

    def save(self,):
        filename = "/storage/yan/primekg/qg_dataset/lc-quad/processed_lcquad.json"
        with open(filename, "w") as f:
            json.dump(self.triples, f, indent=4)
        print(f"{len(self.triples)} triples has been saved in the file {filename}")
        return

if __name__ == "__main__":
    convert = load_lcquad()
    convert.read_file()
    convert.save()

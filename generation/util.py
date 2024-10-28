import json
import ipdb
from rdflib import Graph
from wikidata.client import Client
import requests
from tqdm import tqdm
import time
from SPARQLWrapper import SPARQLWrapper, JSON

proj_known_property_abbreviations = {
    'ppi': "is in protein-protein interaction with",
    'carrier': 'is the carrier of',
    'enzyme': "enzymes",
    'target': "targets",
    'transporter': "is the transporter of",
    'contraindication': "is contraindication for",
    'indication': "is indicated for",
    'off-label%20use': "has off-label use:",
    'synergistic%20interaction': "has synergistic interactio with",
    'associated%20with': "is associated with",
    'parent-child': "has parent-child relation with",
    'phenotype%20absent':"absents the phenotype",
    'phenotype%20present': "presents the phenotype",
    'side%20effect':"has side effect of",
    'interacts%20with':"interacts with",
    'linked%20to': "is linked to",
    'expression%20present': "presents the expression",
    'expression%20absent': "absents the expression",
}

def form_prompt_gpt(triples:list, bracket=False, baseline=False) -> str:
    '''
    triples: list of a list of triples composed of sub, prop, obj and their similar questions in bioAsk
    output: lists of prmopts to send to chatGPT 
    '''
    few_shot_example = "\nThe example of generating questions based on facts and answer are: "
    # non-answer setting
    few_shot_example = "\nThe example of generating questions based on facts:"
    example1 = "\n1. Given an fact: [Long QT syndrome-1/ROMANO-WARD syndrome] [is associated with] [KCNQ1]. The answer is: [KCNQ1]. The question is:  Which genes are affected in ROMANO-WARD syndrome? "
    example2 = "\n2. Given two facts: [CADASIL] [is caused mostly by] [missense mutations in the NOTCH3 gen]; [Missense mutations in the NOTCH3 gene] [is associated with] [a cysteine residue]. The answer is [Cysteine]. The question is: Which amino acid residue appears mutated in most of the cases reported with cadasil syndrome?"
    natural_example1 = "\n1. Given an fact: Long QT syndrome-1/ROMANO-WARD syndrome is associated with KCNQ1. The answer is: KCNQ1. The question is:  Which genes are affected in ROMANO-WARD syndrome? "
    natural_example2 = "\n2. Given two facts: CADASIL is caused mostly by missense mutations in the NOTCH3 gen; Missense mutations in the NOTCH3 gene is associated with a cysteine residue. The answer is Cysteine. The question is: Which amino acid residue appears mutated in most of the cases reported with cadasil syndrome?"
    # without answer setting, does not work well
#    no_ans_natural_example2 = "\n1. Given an fact: Long QT syndrome-1/ROMANO-WARD syndrome is associated with [unknown]. The question is:  Which genes are affected in ROMANO-WARD syndrome? "
#    no_ans_natural_example1 = "\n2. Given two facts: CADASIL is caused mostly by missense mutations in the NOTCH3 gen; Missense mutations in the NOTCH3 gene is associated with a [unknown]. The question is: Which amino acid residue appears mutated in most of the cases reported with cadasil syndrome?"

    
    if bracket:
        few_shot_example += example1
        few_shot_example += example2
    else:
        few_shot_example += natural_example1
        few_shot_example += natural_example2
    
    # masking answer
    #few_shot_example += no_ans_natural_example1
    #few_shot_example += no_ans_natural_example2
    
    systems, usrs, eval = list(), list(), list()
    for triple in triples:
        len_triple = len(triple["value"])
        text = triple["value"]
        # new_setting
       # ans_orig = triple["answer_"]
       # try:
       #     ans_orig = proj_known_property_abbreviations[ans_orig]
       # except:
       #     pass
        try:
            answer = proj_known_property_abbreviations[triple["answer"]]
        except:
            if isinstance(triple["answer"], str):
                answer = triple["answer"]
            if isinstance(triple["answer"], list):
                if triple["answer"][0] in proj_known_property_abbreviations.keys():
                    answer = "; ".join([proj_known_property_abbreviations[i] for i in triple["answer"]])
                else:
                    answer = "; ".join([i for i in triple["answer"] if i is not None])
        answer = answer[:250]
        if bracket:
            for triple in text:
                for idx in range(3):
                    if idx in [0, 2]:
                        triple[idx] = '[' + triple[idx][:120] + ']'
                    else:
                        try:
                            triple[idx] = '[' + proj_known_property_abbreviations[triple[idx]] + ']'
                        except:
                            triple[idx] = '[' + triple[idx][:120] + ']'
            # slicing it due to max token limit
            text = [" ".join(i) for i in text]
            text = "; ".join(text).strip().replace("%20", ' ')
            answer = "[" + answer + "]"

            
        else:
            for triple in text:

                try:
                    triple[1] = proj_known_property_abbreviations[triple[1]] 
                except KeyError:
                    triple[1] = triple[1][:120]

                    # masking the answer
#                    if idx == 2:
#                        triple[idx] = "[unknown]"
            # slicing it due to max token limit
            text = [" ".join(i) for i in text]
            text = "; ".join(text).strip().replace("%20", ' ')
        text = text[:100]
        

        COT = " Let's think step by step"
        system = f"You are a biologist. You will propose one question based on {len_triple} facts and 1 given answer. Add an explanation." + few_shot_example
        # new setting
#        system = f"You will propose one question based on {len_triple} facts. Add an explanation." + no_ans_natural_example1 + no_ans_natural_example2

        if baseline:
            system = f"You are a biologist. You will propose one question based on {len_triple} facts and 1 given answer."
#        else:
#            system = f"You are a biologist. You will propose a complex question based on {len_triple} facts from a biomedical knowledge graph and a given answer. Add an explaination." + few_shot_example
       
        usr = f"\nNow generate a question based on {len_triple} facts and 1 given answer: {text}. The answer is {answer}." + COT
        # new setting
#        usr = f"\nNow generate a question based on {len_triple} facts: {text}." + COT

        if baseline:
            usr = f"\nNow generate a question based on {len_triple} facts and 1 given answer: {text}. The answer is {answer}."
#        systems.append(system)
        systems.append(system+ " Be concise!")
        usrs.append(usr)
        eval.append([text, answer])
    print(f"Eaxmple of system prompt: {systems[0]}, \nand an user promot: {usrs[0]}.")
    assert len(systems) == len(usrs)
    return systems, usrs, eval

 
def eval_prompt(source, ans, qs=["", "", ""]):

    prompt = f""
    return prompt


# load sqb dev data and save it in triple forms in self.data
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
        with open("sqb_dev_fullRel.json" , "w") as f:
            json.dump(self.data, f, indent=4)
        return

def pos_processing(ans):
        text = ans.split("Explanation")[0]
        text = text.split("Question")[-1]
        text = text.split("The question is: ")[-1]
        text = text.split("the question could be")[-1]
        text = text.split("the following question")[-1]
        text = text.split("?")[0] +"?"
        if "Wh" in text:
            text = "Wh" +text.split("Wh")[-1] 
        return text.strip(": \n")    
def pos_processing(ans):
            text = ans.split("Explanation")[0]
            text = text.split("The question is:")[-1]
            text = text.split("Based on the given facts, we can generate a question")[-1]
            text = text.split("Question")[-1]
            text = text.split("\nQuestion")[-1]
            text = text.split("question could be")[-1]
            text = text.split("question would be")[-1]
            text = text.split("we can generate a question: ")[-1]
            text = text.split("Determine the question:")[-1]
            text = text.split("question can be")[-1]
            text = text.split("a question based on the facts and answer:")[-1]
            text = text.split(" ask a question: ")[-1]
            text = text.split("the following question")[-1]
            text = text.split("3. Based on the facts, generate a question:")[-1]
            text = text.split("the following question")[-1]
            text = text.split("question we can generate is:")[-1]
            text = text.split("propose a question:")[-1]
            text = text.split("possible question that can be generated based on the given fact and answer is:")[-1]
            text = text.split("We can ask")[-1]
            text = text.split("?")[0] +"?"
            if "Wh" in text:
                text = "Wh" +text.split("Wh")[-1] 
            if len(text) >= 250:
                return ""
            return text.strip(": \n")
        
'''
        text = ans.split("generate a question:")[-1]
        text = text.split("Determine the question:")[-1]
        text = text.split("question could be")[-1]
        text = text.split("question can be")[-1]
        text = text.split("the following question")[-1]
        text = text.split("question we can generate is:")[-1]
        text = text.split("can ask a question")[-1]
        text = text.split("propose a question:")[-1]
        text = text.split("Formulate a question based on the facts and answer: ")[-1]
        text = text.split("possible question that can be generated based on the given fact and answer is:")[-1]
        text = text.split("Question")[-1]
        text = text.split(":")[-1]
        text = text.split("?")[0] +"?"
        if "Wh" in text:
            text = "Wh" +text.split("Wh")[-1] 
        if len(text) >= 200:
            return f"THIS is a failed post processing case and the original answer is {ans}"
        return text.strip(": \n")
'''

if __name__ == "__main__":
    # for converting sqb dataset and save in a json file.
    con = Convert()
    con.save_sqb()

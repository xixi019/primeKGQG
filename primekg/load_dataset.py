import os
import ipdb
import json 
from SPARQLWrapper import SPARQLWrapper, JSON
import ipdb
import time

Bgee = "dataset/Bioinformatics/Bgee"
BgeeS = "dataset/Bioinformatics/Bgeesimple"
fedBgee = "dataset/Bioinformatics/FederatedBgee-OMA"
Oma = "dataset/Bioinformatics/OMA"
#Cordis = "dataset/CORDIS"
qald4test = "dataset/QALD4/test"
qald4train = "dataset/QALD4/train"

def read_rd(filename):
    f = open(filename, 'r')
    f = f.read()
    qs = f.split('\n\n')[0].split('#')[1][1:]
    query = f.split('\n\n')[1]
    return qs, query 

# if you want to retrieve the answers from the KG
def get_answer(pair):
    if "Bgee" in pair["source"]:
        endpoint = "https://bgee.org/sparql/"
    if "OMA" in pair["source"]:
        endpoint = "https://sparql.omabrowser.org/sparql/"
    if 'QALD' in pair["source"]:
        return
        # dysfunctional endpoints
#       endpoint = "https://drugbank.bio2rdf.org/sparql"
#        endpoint = "https://wifo5-03.informatik.uni-mannheim.de/drugbank/sparql"
#        endpoint = "http://wifo5-03.informatik.uni-mannheim.de/drugbank/sparql"
#        endpoint = "http://www4.wiwiss.fu-berlin.de/drugbank/sparql"
#        endpoint = "http://vtentacle.techfak.uni-bielefeld.de:443/sparql"
    query = pair["query"].replace("\n", " ").replace("\t", "  ")
    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(JSON)
    sparql.setQuery(f"""
                    {query}
        """
        )

    try:
        ret = sparql.queryAndConvert()

        for r in ret["results"]["bindings"]:
            print(r)
        return ret["results"]["bindings"]
    except Exception as e:
        print(e)
    time.sleep(2) 
    return

def collect(dataset):
    out = list()
    for file in os.listdir(dataset):
        if file.endswith("rq"):
            qs, query = read_rd(dataset+'/'+file)
            q = {"source": dataset, "qs":qs, "query":query}
#            q["ans"] = get_answer(q)
#            ipdb.set_trace()
            out.append(q)
    return out    

out = []
for dataset in [Bgee, BgeeS, fedBgee, Oma, qald4test, qald4train]:
    out.extend(collect(dataset))

id  = 0 
for pair in out:
    pair["id"] = id
    id += 1
template = [{"qs":pair["qs"], "qs_temp":pair["qs"], "id":pair["id"], "n_entities":0, "sq":pair["query"], "sq_temp":pair["query"]} for pair in out]


json_object = json.dumps(out, indent=4)
template_object = json.dumps(template, indent=4)

#with open("dataset/template.json", "w") as outfile:
#    outfile.write(template_object)

with open("dataset/sample.json", "w") as outfile:
    outfile.write(json_object)

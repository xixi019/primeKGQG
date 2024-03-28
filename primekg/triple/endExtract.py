
# -*- coding: utf-8 -*-
from SPARQLWrapper import SPARQLWrapper, JSON
import time
import json

# endpoint of the primekg under informatik

def get_answer():
    out = list()
    endpoint = "http://sems-coypu-4.informatik.uni-hamburg.de:8890/sparql/"
    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(JSON)
    
    sparql.setQuery(
        """
            SELECT DISTINCT ?subj1 ?obj1 ?obj2 ?obj3 ?prop1 ?prop2 ?prop3
            WHERE {{
                    {
                        ?subj1 ?prop1 ?obj1.
                        OPTIONAL
                        {
                        ?obj1 ?prop1 ?subj1.
                        }
                    }
                    {
                        ?subj1 ?prop2 ?obj2.
                        OPTIONAL
                        {
                        ?obj2 ?prop2 ?subj1.
                        }
                    }
                    {
                        ?subj1 ?prop3 ?obj3.
                        OPTIONAL
                        {
                        ?obj3 ?prop3 ?subj1.
                        }
                    }
                FILTER (strstarts(str(?subj1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
                FILTER (strstarts(str(?obj1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
                FILTER (strstarts(str(?obj2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
                FILTER (strstarts(str(?obj3), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
                FILTER (strstarts(str(?prop1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
                FILTER (strstarts(str(?prop2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
                FILTER (strstarts(str(?prop3), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
                FILTER (str(?prop1) != "https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab/associated%20with")
                FILTER (str(?prop2) != "https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab/associated%20with")
                FILTER (str(?prop3) != "https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab/associated%20with")
            }}
            """
    )

    try:
        ret = sparql.queryAndConvert()

        for r in ret["results"]["bindings"]:
            print(r)
            out.append(r)
#        return ret["results"]["bindings"]
    except Exception as e:
        print(e)
    time.sleep(2) 
    return out

def get_sparql(type):
    if type==0:
        sparql = """
        SELECT DISTINCT ?subj ?prop ?obj
        WHERE {{
            ?subj ?prop ?obj.
            FILTER (strstarts(str(?subj), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/'))
            FILTER (strstarts(str(?prop), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?obj), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
            FILTER (str(?prop) != "https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab/associated%20with")

        }}
        """
        sparql = sparql.encode("UTF-8")
    if type==1:
        sparql = """
        SELECT DISTINCT ?subj ?prop1 ?obj1 ?prop2 ?obj2
        WHERE {{
            ?subj ?prop1 ?obj1.
            ?subj ?prop2 ?obj2
            FILTER (strstarts(str(?subj), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/'))
            FILTER (strstarts(str(?prop1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab'))
            FILTER (strstarts(str(?prop2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab'))
            FILTER (strstarts(str(?obj1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/'))
            FILTER (strstarts(str(?obj2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/'))
        }}
        """
        sparql = sparql.encode("UTF-8")

    if type == 2:
        sparql = f"""
        SELECT DISTINCT ?subj ?prop1 ?obj1 ?prop2 ?obj2
        WHERE {{
            ?subj ?prop1 ?obj1.
            ?obj1 ?prop2 ?obj2
            FILTER (strstarts(str(?subj), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
            FILTER (strstarts(str(?prop1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
        }}
        """

    if type == 3:
        sparql = u"""
        SELECT ?subj ?prop1 ?obj1 ?prop2 ?obj2 ?prop3
        WHERE {
            ?subj ?prop1 ?obj1.
            ?subj ?prop2 ?obj2.
            ?obj1 ?prop3 ?subj
            FILTER (strstarts(str(?subj), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
            FILTER (strstarts(str(?prop1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop3), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER ( ?prop1 != ?prop3)

        }
        """

    if type == 4:
        sparql = """
        SELECT DISTINCT ?subj1 ?prop1 ?obj ?subj2 ?prop2
        WHERE {
            ?subj1 ?prop1 ?obj.
            ?subj2 ?prop2 ?obj
            FILTER (strstarts(str(?subj1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
            FILTER (strstarts(str(?prop1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 

        }
        """

    if type == 5:
        sparql = """
        SELECT DISTINCT ?subj1 ?prop1 ?subj2 ?prop2 ?obj ?prop3
        WHERE {
            ?subj1 ?prop1 ?obj.
            ?subj2 ?prop2 ?obj.
            ?subj1 ?prop3 ?subj2
            FILTER (strstarts(str(?subj1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
            FILTER (strstarts(str(?prop1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop3), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
        }
        """
    # nothing can be extracted
    if type == 6:
        sparql = """
        SELECT DISTINCT ?subj1 ?prop1 ?obj ?subj2 ?prop2 ?prop3 ?prop4 
        WHERE {
            ?subj1 ?prop1 ?obj.
            ?subj2 ?prop2 ?obj.
            ?subj1 ?prop3 ?subj2.
            ?subj2 ?prop4 ?subj1
            FILTER (strstarts(str(?subj1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
            FILTER (strstarts(str(?prop1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop3), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop4), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER ( ?prop3 != ?prop4)

        }
        """
    # exclude has node is relation
    if type ==7:
        sparql = """
        SELECT DISTINCT ?subj ?prop1 ?obj1 ?prop2 ?obj2 ?prop3
        WHERE {
            ?subj ?prop1 ?obj1.
            ?obj1 ?prop2 ?obj2.
            ?obj1 ?prop3 ?subj
            FILTER (strstarts(str(?subj), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
            FILTER (strstarts(str(?prop1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop3), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER ( ?prop3 != ?prop1)
            FILTER ( str(?prop3) != "https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab/has_node_id")

        }
        """
    if type == 8:
        sparql = """ 
        SELECT DISTINCT ?subj ?prop1 ?obj1 ?prop2 ?obj2 ?prop3 ?prop4
        WHERE {
            ?subj ?prop1 ?obj1.
            ?obj1 ?prop2 ?obj2.
            ?obj1 ?prop3 ?subj.
            ?obj2 ?prop4 ?obj1
            FILTER (strstarts(str(?subj), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
            FILTER (strstarts(str(?prop1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop3), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop4), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER ( ?prop3 != ?prop1)
            FILTER ( ?prop2 != ?prop4)

        }
        """
    
    if type == 9:
        sparql = """ 
        SELECT DISTINCT ?subj ?prop1 ?obj1 ?prop2 ?obj2 ?prop3 ?prop4
        WHERE {
            ?subj ?prop1 ?obj1.
            ?obj1 ?prop2 ?obj2.
            ?obj2 ?prop3 ?subj
            FILTER (strstarts(str(?subj), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
            FILTER (strstarts(str(?prop1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop3), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 

        }
        """

    if type == 10:
        sparql = """
        SELECT DISTINCT ?subj1 ?prop1 ?obj ?subj2 ?prop2 ?prop3 ?prop4
        WHERE {
            ?subj1 ?prop1 ?obj.
            ?subj2 ?prop2 ?obj.
            ?subj1 ?prop3 ?subj2.
            ?obj ?prop4 ?subj1
            FILTER (strstarts(str(?subj1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
            FILTER (strstarts(str(?prop1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop3), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop4), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER ( ?prop1 != ?prop4)

        }
        """
    
    if type == 11:
        sparql = """
        SELECT DISTINCT ?subj1 ?prop1 ?obj ?subj2 ?prop2 ?prop3 ?prop4
        WHERE {
            ?subj1 ?prop1 ?obj.
            ?subj2 ?prop2 ?obj.
            ?subj1 ?prop3 ?subj2.
            ?obj ?prop4 ?subj2
            FILTER (strstarts(str(?subj1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
            FILTER (strstarts(str(?prop1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop3), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop4), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER ( ?prop2 != ?prop4)

        }
        """

    if type == 12:
        sparql = """
        SELECT DISTINCT ?subj1 ?prop1 ?obj ?subj2 ?prop2 ?prop3 ?prop4 ?prop5 
        WHERE {
            ?subj1 ?prop1 ?obj.
            ?subj2 ?prop2 ?obj.
            ?subj1 ?prop3 ?subj2.
            ?obj ?prop4 ?subj2.
            ?obj ?prop5 ?subj1
            FILTER (strstarts(str(?subj1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
            FILTER (strstarts(str(?prop1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop3), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop4), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop5), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER ( ?prop1 != ?prop5)
            FILTER ( ?prop2 != ?prop4)

        }
        """
    # nothing can be extracted when we remove the duplicate
    if type == 13:
        sparql = """
        SELECT DISTINCT ?subj1 ?prop1 ?obj ?subj2 ?prop2 ?prop3 ?prop4 ?prop5 ?prop6
        WHERE {
            ?subj1 ?prop1 ?obj.
            ?subj2 ?prop2 ?obj.
            ?subj1 ?prop3 ?subj2.
            ?obj ?prop4 ?subj2.
            ?obj ?prop5 ?subj1.
            ?subj2 ?prop6 ?subj1
            FILTER (strstarts(str(?subj1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
            FILTER (strstarts(str(?prop1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop3), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop4), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop5), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER (strstarts(str(?prop6), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            FILTER ( ?prop1 != ?prop5)
            FILTER ( ?prop2 != ?prop4)
            FILTER ( ?prop3 != ?prop6)

        }
        """

    # wanna try with 4 node options?
    # one of the basic connection four 4 node motifs
    if type == 40:
            sparql =  """
            SELECT DISTINCT ?subj1 ?obj1 ?obj2 ?obj3 ?prop1 ?prop2 ?prop3
            WHERE {{
                    {
                        ?subj1 ?prop1 ?obj1.
                        OPTIONAL
                        {
                        ?obj1 ?prop1 ?subj1.
                        }
                    }
                    {
                        ?obj1 ?prop2 ?obj2.
                        OPTIONAL
                        {
                        ?obj2 ?prop2 ?obj1.
                        }
                    }
                    {
                        ?obj2 ?prop3 ?obj3.
                        OPTIONAL
                        {
                        ?obj3 ?prop3 ?obj2.
                        }
                    }
                FILTER (strstarts(str(?subj1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
                FILTER (strstarts(str(?obj1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
                FILTER (strstarts(str(?obj2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
                FILTER (strstarts(str(?obj3), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
                FILTER (strstarts(str(?prop1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
                FILTER (strstarts(str(?prop2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
                FILTER (strstarts(str(?prop3), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
            }}
            """
    # the most basic type of four node connection, which reults in 0 subgraph
    if type == 43:
            sparql =   """
            SELECT DISTINCT ?subj1 ?obj1 ?obj2 ?obj3 ?prop1 ?prop2 ?prop3
            WHERE {{
                    {
                        ?subj1 ?prop1 ?obj1.
                        OPTIONAL
                        {
                        ?obj1 ?prop1 ?subj1.
                        }
                    }
                    {
                        ?subj1 ?prop2 ?obj2.
                        OPTIONAL
                        {
                        ?obj2 ?prop2 ?subj1.
                        }
                    }
                    {
                        ?subj1 ?prop3 ?obj3.
                        OPTIONAL
                        {
                        ?obj3 ?prop3 ?subj1.
                        }
                    }
                FILTER (strstarts(str(?subj1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
                FILTER (strstarts(str(?obj1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
                FILTER (strstarts(str(?obj2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
                FILTER (strstarts(str(?obj3), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/')) 
                FILTER (strstarts(str(?prop1), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
                FILTER (strstarts(str(?prop2), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
                FILTER (strstarts(str(?prop3), 'https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab')) 
                FILTER (str(?prop1) != "https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab/associated%20with")
                FILTER (str(?prop2) != "https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab/associated%20with")
                FILTER (str(?prop3) != "https://zitniklab.hms.harvard.edu/projects/PrimeKG/vocab/associated%20with")
            }}
            """
    return sparql

# get answer from the endpoint and save in json format
def save_json():
    out =  get_answer()
    with open("4f_v2_noAsso.json", "a") as f:
        json.dump(out, f, indent=4)

   
    f.close()
    return

save_json()
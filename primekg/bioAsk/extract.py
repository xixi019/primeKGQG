import glob
import json 


# a fuction to generate a filtered set for triple2question training.
def get_data(address:str, question_only:True):
    '''
    address: the address where you save the bioAsk dataset
    to_save: a dict where "data" is the filtered bioask pair with triples, "count" is a list of the number of the triples.
    '''
    files1 = glob.glob(address+"*.json")
    files2 = glob.glob(address+"*/*.json")
    total = files1 + files2

    triple_count, qa_pairs, qs = [], [], []
    to_save = {"data":[], "count":[]}

    for file in total[1:]:
        with open(file) as f:
            data = json.load(f) 
            for pair in data["questions"]:
                if question_only:
                    if pair["body"] not in qs:
                        qs.append(pair["body"])
                if "triples" in pair.keys():
                    assert type(pair["triples"]) == list, pair
                    if len(pair['triples']) > 0:
                        if pair not in qa_pairs:
                            triple_count.append(len(pair['triples']))
                            qa_pairs.append(pair)
            f.close()
    to_save["data"], to_save["count"] = qa_pairs, triple_count
    
    with open("/export/home/yan/primekg/bioAsk/"+'filtered.json', 'w') as f:
        json.dump(to_save, f, indent=4)
    f.close()
    
    if question_only:
        with open("/export/home/yan/primekg/bioAsk/"+'bioQs.json', 'w') as f:
            json.dump(qs, f, indent=4)
        f.close()


    return to_save

if __name__ == "__main__":
    get_data("/export/home/yan/primekg/bioAsk/", question_only=True)
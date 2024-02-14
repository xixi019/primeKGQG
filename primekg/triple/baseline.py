from openai import OpenAI
import json
import ipdb
import sent2vec
from nltk import word_tokenize
from nltk.corpus import stopwords
from string import punctuation
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import numpy
import requests
import json
import os
nltk.download('punkt')
nltk.download('stopwords')
# this is a script for generating baseline result on triple2ques task of primekg
# system one is with chatGPT


# a dictionary to map the property abbreviation to text, unfinished since 
# 1. not sure whethee this is a good idea 
# 2. need professional to annptate
proj_known_property_abbreviations = {
    'ppi':"is in protein-protein interaction with",
    'carrier': 'is the carrier of',
    'enzyme': "enzyme",
    'target': "target",
    'transporter': "is the transporter of",
    'contraindication': "",
    'indication': "",
    'off-label use': "",
    'synergistic interaction': " ",
    'associated with': "",
    'parent-child': " ",
    'phenotype absent':" ",
    'phenotype present':" ",
    'side effect':" ",
    'interacts with':" ",
    'linked to':"",
    'expression present':" ",
    'expression absent':" ",
}


# load the textualized triples, return a list of graphs that's made of dictionaries
def load_dataset(filename:str) -> list:
    with open(filename) as f:
        triples = json.load(f)
    return triples


def get_context(subgraphs:list, filename:str) -> list:
    '''
    subgraphs: a list of subgraphs that loaded from textualized.json
    filename: address for thw BioQs, question list from BioAsk series.
    '''

    # load questions 
    with open(filename) as f:
        Qs = json.load(f)
    # load a pretrained sentence similarity model and embed the questions from bio-Ask
    model = load_bio_model("../model_similarity/BioSentVec_PubMed_MIMICIII-bigram_d700.bin")
    embs = model.embed_sentences(Qs)


    contextualized_input = list()
    stop_words = set(stopwords.words('english'))
    for graph in subgraphs:
        text = ''
        for triple in graph["value"]:
            triple = [ item.replace("%20", " ") for item in triple]
            text += " ".join(triple)  + " "
        sentence = " ".join([token for token in word_tokenize(text) if token not in punctuation and token not in stop_words])
        sentence_vector = model.embed_sentence(sentence)

        cosine_sim = cosine_similarity(embs, sentence_vector)
        simi_sent_index = numpy.argsort(cosine_sim.reshape(1, 5061))[0, 5059:5061]
        simi_sents = [Qs[i] for i in simi_sent_index]
        graph["context"] = simi_sents
        contextualized_input.append(graph)
        print(f"Processing {len(contextualized_input)/len(subgraphs)}, in a low speed")


    with open("contextualized_graph.json", 'w') as f:
        json.dump(contextualized_input, f, indent=4)
    f.close()
    print("file contextualized_graph.json has been created.")
    return contextualized_input


# helper function for get_context
def load_bio_model(model_path:str):
    '''
    model_path: the path to the bioSimilary model, download with https://ftp.ncbi.nlm.nih.gov/pub/lu/Suppl/BioSentVec/BioWordVec_PubMed_MIMICIII_d200.vec.bin
    output: a loaded model
    '''
    model = sent2vec.Sent2vecModel()
    try:
        model.load_model(model_path)
    except Exception as e:
        print(e)
    print('model successfully loaded')
    return model

# take a triple, find it's close questions and form a prompt for sending it to ChatGPT
def form_prompt(triples:list) -> str:
    '''
    triples: list of a list of triples composed of sub, prop, obj and their similar questions in bioAsk
    output: lists of prmopts to send to chatGPT 
    '''
    systems, usrs = list(), list()
    for triple in triples:
        len_triple = len(triple)
        context, text = triple["context"], triple["value"]
        text = [" ".join(i) for i in text]
        text = "; ".join(text).strip().replace("%20", ' ')
        if  len_triple <=3:
            system = f"You are a biologist. You will propose a simple question based on {len_triple} facts from a biomedical knowledge graph and some example questions."
        else:
            system = f"You are a biologist. You will propose a complex question based on {len_triple} facts from a biomedical knowledge graph and some example questions."
       
        usr = f"The facts are: {text}.\n Examples are: {context[0]} \n {context[1]}"
        systems.append(system)
        usrs.append(usr)
    
    assert len(systems) == len(usrs)
    return systems, usrs



def call_openAI(triples):
    OpenAI.api_key =  # put yout api key here
    with_ans = list()
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OpenAI.api_key}"
    }

    systems, usrs = form_prompt(triples)
    for system, usr, triple in zip(systems, usrs, triples):
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": system
                },
                {
                    "role": "user",
                    "content": usr
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data)

        # Check if the request was successful
        if response.status_code == 200:
            print("Response from OpenAI:", response.json())
            print('\n')
            print(response.json()['choices'][0]['message']['content'])
            triple["answer_GPT3"] = response.json()['choices'][0]['message']['content']
            with_ans.append(triple)
        else:
            print("Error:", response.status_code, response.text)
        print(f"processing percentage {len(with_ans)/100}.")
    return with_ans

if __name__ == '__main__':
    API_key = 
#    combine the triples with similar questions from bioAsk
#    triples = load_dataset("../generatedTriple/textualized.json") 
#    out = get_context(triples, "/export/home/yan/primekg/bioAsk/bioQs.json")
    with open("contextualized_graph.json", 'r') as f:
        triples = json.load(f)
    f.close()
    

    # already run with top 100 samples, saved in contextualized_graph_ans.json
    with_ans = call_openAI(triples=triples[:1])

    with open('chatGPT_ans.json', 'w') as f:
        json.dump(with_ans, f, indent =4)
    f.close()
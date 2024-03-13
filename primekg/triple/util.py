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

def form_prompt_gpt(triples:list, bracket:True) -> str:
    '''
    triples: list of a list of triples composed of sub, prop, obj and their similar questions in bioAsk
    output: lists of prmopts to send to chatGPT 
    '''
    few_shot_example = "\nTwo example of generating questions based on facts and answer are: "
    example1 = "\n1. Given an fact: [Long QT syndrome-1/ROMANO-WARD syndrome] [is associated with] [KCNQ1]. The answer is: [KCNQ1]. The question is:  Which genes are affected in ROMANO-WARD syndrome? "
    example2 = "\n2. Given two facts: [CADASIL] [is caused mostly by] [missense mutations in the NOTCH3 gen]; [Missense mutations in the NOTCH3 gene] [is associated with] [a cysteine residue]. The answer is [Cysteine]. The question is: Which amino acid residue appears mutated in most of the cases reported with cadasil syndrome?"
    few_shot_example += example1
    few_shot_example += example2
    systems, usrs, ans = list(), list(), list()
    for triple in triples:
        len_triple = len(triple)
        try:
            text, answer = triple["value"], proj_known_property_abbreviations[triple["answer"]]
        except KeyError:
            text, answer = triple["value"], triple["answer"]
        if bracket:
            for triple in text:
                for idx in range(3):
                    if idx in [0, 2]:
                        triple[idx] = '[' + triple[idx] + ']'
                    else:
                        triple[idx] = '[' + proj_known_property_abbreviations[triple[idx]] + ']'
    #        answer = random.choice(random.choice(text))
            text = [" ".join(i) for i in text]
            text = "; ".join(text).strip().replace("%20", ' ')
        else:
            for triple in text:
                for idx in range(3):
                    if not idx in [0, 2]:
                        triple[idx] = proj_known_property_abbreviations[triple[idx]] 
            text = [" ".join(i) for i in text]
            text = "; ".join(text).strip().replace("%20", ' ')
#        if  len_triple <=3:
        system = f"You are a biologist. You will propose one question based on {len_triple} facts and 1 given answer. Add an explanation." + few_shot_example
#        else:
#            system = f"You are a biologist. You will propose a complex question based on {len_triple} facts from a biomedical knowledge graph and a given answer. Add an explaination." + few_shot_example
       
        usr = f"\nNow generate a question based on {len_triple} facts and 1 given answer: {text}. The answer is [{answer}]."
        systems.append(system)
        usrs.append(usr)
    print(f"Eaxmple of system prompt: {systems[0]}, \nand an user promot: {usrs[0]}.")
    assert len(systems) == len(usrs)
    return systems, usrs
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import json 
from datasets import Dataset
from transformers.pipelines.pt_utils import KeyDataset
from tqdm import tqdm
from transformers.utils.quantization_config import BitsAndBytesConfig
import torch
from util import form_prompt_gpt, pos_processing, eval_prompt
import ipdb

def call_mistral(triples, baseline=False):
    ans, out = list(), list()
    bnb_config = BitsAndBytesConfig(
                                    load_in_4bit=True,
                                    bnb_4bit_use_double_quant=True,
                                    bnb_4bit_quant_type="nf4",
                                    bnb_4bit_compute_dtype=torch.bfloat16
                                    )
    model_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side="left", truncation = True)

    model = AutoModelForCausalLM.from_pretrained(
                                                model_id,
                                                quantization_config = bnb_config,
                                                torch_dtype=torch.float16,
                                                attn_implementation="flash_attention_2",
                                                device_map="cuda",
                                                )

    tokenizer.pad_token_id = model.config.eos_token_id    
    tokenizer.bos_token_id=model.config.bos_token_id
    tokenizer.eos_token_id=model.config.eos_token_id

    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, do_sample = True, temperature=0.1, top_k=50, top_p=0.02)

    systems, usrs, eval = form_prompt_gpt(triples, bracket=False, baseline=baseline)
    data_set = []
    for system, usr, triple, source in zip(systems, usrs, triples, eval):       
        chat = [
                    {
                        "role": "user",
                        "content": system,
                    }
                    ,
                    {
                        "role": "assistant",
                        "content": usr,
                    }
                ]
        text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True, return_tensors="pt")
        triple["prompt"] = text
        data_set.append({"prompt":text , "triple":triple})
        triple["eval"] = source

    
    dataset = Dataset.from_list(data_set)
    
    
    for out in tqdm(pipe(KeyDataset(dataset, "prompt"), batch_size=20, max_new_tokens=200)):
        ans.extend(out)

    for text, triple in zip(ans, triples):
        triple["generated_text"] = pos_processing(text["generated_text"][len(triple["prompt"]):])
        triple["orig_output"] = text["generated_text"][len(triple["prompt"]):]

        out.append(triple)


    return out

def call_bioLLM(triples):
    out = list()
    model_id = "AdaptLLM/medicine-LLM-13B"
#    model_id = "AdaptLLM/medicine-chat"
    
    tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side="left", use_fast=False, truncation = True, max_length=2048)
    bnb_config = BitsAndBytesConfig(
                                    load_in_4bit=True,
                                    bnb_4bit_use_double_quant=True,
                                    bnb_4bit_quant_type="nf4",
                                    bnb_4bit_compute_dtype=torch.bfloat16
                                    )
    model = AutoModelForCausalLM.from_pretrained(
                                                model_id,
                                                quantization_config= bnb_config,
                                                torch_dtype=torch.float16,
                                                attn_implementation="flash_attention_2",
                                                device_map="cuda",
                                                )

    tokenizer.pad_token_id = model.config.eos_token_id    
    tokenizer.bos_token_id=model.config.bos_token_id
    tokenizer.eos_token_id=model.config.eos_token_id
    
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, do_sample = True, temperature=0.1, top_k=50, top_p=0.02)
    
    systems, usrs, eval = form_prompt_gpt(triples, True)
    data_set, answers = list(), list()
    for system, usr, triple, test in zip(systems, usrs, triples, eval):       
        prompt = system + "/n/n" + usr
        data_set.append(prompt)
        triple["prompt"] = prompt
        triple["eval"] = test
    
    dataset = Dataset.from_dict({"prompt":data_set})
    for ans in tqdm(pipe(KeyDataset(dataset, "prompt"), batch_size=10, max_new_tokens=200)):
        answers.append(ans[0]["generated_text"])
    for ans, triple in zip(answers, triples):
        triple["orig_output"] = ans[len(triple["prompt"]):]
        triple["generated_text"] = pos_processing(ans[len(triple["prompt"]):])
        out.append(triple)    
    print(f"file from baseline.py {out}")
    return out

def save_annotator(model, out):
    num = 80
    for data in out:
        data["grammar"]= None
        data["coverage"]=None
        data["consistency"]= None 
        data["generated_question"]= data["generated_text"]
        data["id"] = num
        num += 1

    outfile = f"val_{model}.json"
    with open(outfile, 'w') as f:
        json.dump(out, f, indent=4)
    f.close()
    print(f"{outfile} has been saved!")
    return

if __name__ == '__main__':

    # run experiment on the samples
    filename = "/storage/yan/primekg/generatedTriple/total/final_val.json"
    
    with open(filename, 'r') as f:
        triples = json.load(f)
    f.close()
    for data in triples:
        data["answer"] = data["answer_sparql"]
        assert len(data["answer"]) >= 1

    print(f'we are processing {filename}, {len(triples)}')
    out = call_bioLLM(triples)
    save_annotator("call_bioLLM", out)

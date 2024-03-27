from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import json 
from datasets import Dataset
from transformers.pipelines.pt_utils import KeyDataset
from tqdm import tqdm
from transformers.utils.quantization_config import BitsAndBytesConfig
import torch
from mistral.util import form_prompt_gpt
import ipdb
def call_mistral(triples):
    ans, out = list(), list()
    bnb_config = BitsAndBytesConfig(
                                    load_in_4bit=True,
                                    bnb_4bit_use_double_quant=True,
                                    bnb_4bit_quant_type="nf4",
                                    bnb_4bit_compute_dtype=torch.bfloat16
                                    )
    model_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side="left")

    model = AutoModelForCausalLM.from_pretrained(
                                                model_id,
                                                quantization_config = bnb_config,
                                                torch_dtype=torch.float16,
                                                attn_implementation="flash_attention_2",)

    tokenizer.pad_token_id = model.config.eos_token_id    
    tokenizer.bos_token_id=model.config.bos_token_id
    tokenizer.eos_token_id=model.config.eos_token_id

    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, do_sample = True, temperature=0.1, top_k=50, top_p=0.02)

    systems, usrs = form_prompt_gpt(triples, True)
    data_set = []
    for system, usr, triple in zip(systems, usrs, triples):       
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
        data_set.append({"prompt":text, "triple":triple})
    
    dataset = Dataset.from_list(data_set)
    
    
    for out in tqdm(pipe(KeyDataset(dataset, "prompt"), batch_size=20, max_new_tokens=200)):
        ans.extend(out)

    for text, triple in zip(ans, triples):
        triple["question_mistral_noContext"] = text["generated_text"].split("</s>")[-1]
        out.append(triple)


    return out

def call_bioLLM(triples):
    out = list()
    model_id = "AdaptLLM/medicine-LLM-13B"
#    model_id = "AdaptLLM/medicine-chat"
    
    tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side="left", use_fast=False)
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
                                                attn_implementation="flash_attention_2",)

    tokenizer.pad_token_id = model.config.eos_token_id    
    tokenizer.bos_token_id=model.config.bos_token_id
    tokenizer.eos_token_id=model.config.eos_token_id
    
    
    systems, usrs = form_prompt_gpt(triples, True)
    data_set = []
    '''
    for system, usr, triple in zip(systems, usrs, triples):       
        prompt = system + "/n/n" + usr
        inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).input_ids.to(model.device)
        outputs = model.generate(input_ids=inputs, max_length=2048)[0]

        answer_start = int(inputs.shape[-1])
        pred = tokenizer.decode(outputs[answer_start:], skip_special_tokens=True)

        print(f'### User Input:\n{prompt}\n\n### Assistant Output:\n{pred}')

        triple["question_bioLLM"] = pred.split("The question is:")[-1]
        out.append(triple)

    '''
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, do_sample = True, temperature=0.1, top_k=50, top_p=0.02)

    systems, usrs = form_prompt_gpt(triples, True)
    for system, usr, triple in zip(systems, usrs, triples):       
        prompt = system + "/n/n" + usr
        data_set.append({"prompt":prompt})
    
    dataset = Dataset.from_list(data_set)
    
    answers = list()
    
    for ans in pipe(KeyDataset(dataset, "prompt"), batch_size=15, max_new_tokens=200):
        answers.append(ans[0]["generated_text"])
    for ans, triple in zip(answers, triples):
        triple["generated_answer"] = ans
        out.append(triple)    
    return out

def pos_processing(ans):

    if "Question:" in ans:
        cleaned_ans = ans.split("Question: ")[-1]
    elif "question:" in ans:
        cleaned_ans = ans.split("question:")[-1]
    elif "The question is" in ans:
        cleaned_ans = ans.split("The question is")[-1]
    else:
        cleaned_ans = ans.split("\n\n")[-1].split(': ')[-1]
    return cleaned_ans


if __name__ == '__main__':

    # run experiment on the samples
    
    with open("/storage/yan/primekg/NoDuplicates_samples.json", 'r') as f:
        triples = json.load(f)
    f.close()
    out = call_bioLLM(triples)
       
    with open('Mistral_fewshot_smallbracket_COT.json', 'w') as f:
        json.dump(out, f, indent=4)
    f.close()
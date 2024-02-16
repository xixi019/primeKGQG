from baseline import form_prompt
from transformers import AutoModelForCausalLM, AutoTokenizer
import json 


# run on a CPU since model is too big to load on our GPU
def call_mistral(triples):
    with_ans = list()
    model_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side="left")

    model = AutoModelForCausalLM.from_pretrained(model_id)
    model

    systems, usrs, _ = form_prompt(triples)
    for system, usr, triple in zip(systems, usrs, triples):       
        chat = [
                    {
                        "role": "user",
                        "content": system,
                    },
                    {
                        "role": "assistant",
                        "content": usr,
                    }
                ]

        text = tokenizer.apply_chat_template(chat, tokenize=True, add_generation_prompt=True, return_tensors="pt")
        outputs = model.generate(text, max_new_tokens=200)
        generated = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Check if the request was successful
        
        triple["question_mistral"] = pos_processing(generated)
        with_ans.append(triple)
        print(f"processing percentage {len(with_ans)/len(triples)}.")

    return with_ans


def pos_processing(ans):

    if "Question:" in ans:
        cleaned_ans = ans.split("Question: ")[-1]
    elif "question:" in ans:
        cleaned_ans = ans.split("question:")[-1]
    else:
        cleaned_ans = ans.split("\n\n")[-1].split(': ')[-1]
    return cleaned_ans


if __name__ == '__main__':

    # run experiment on the samples from chatGPT
    
    with open("chatGPT_anGiven.json", 'r') as f:
        triples = json.load(f)
    f.close()
    with_ans = call_mistral(triples)
       
    with open('Mistral_ans.json', 'w') as f:
        json.dump(with_ans, f, indent=4)
    f.close()
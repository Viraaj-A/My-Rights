from model_loader import get_classifier_model_and_tokenizer, get_torch
import requests
from nltk.tokenize import sent_tokenize
import json

model, tokenizer = get_classifier_model_and_tokenizer()
torch = get_torch()

def issue_translator(predictor_query):
    def create_llm_prompt(simplified_text):
        system_message = (
            "\\n\\n Below is an instruction that describes a task, paired with an input that provides further context. "
            "Write a response that appropriately completes the request."
        )

        prompt = (
            "Instruction:\n Strictly adhere to the following instructions when converting any informal non-legal terminology to formal legal language in the user input: "
            "- Do not add any extra detail that detracts from the original meaning. "
            "- The output must be as close to the original meaning of the input. "
            "- The output must be as close to the original input length as possible.\\n\\n###"
            " Input:\\n"
            f"{simplified_text}\\n\\n### Response:\n"
        )

        final_prompt = (
            f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>{system_message}<|eot_id|>"
            f"<|start_header_id|>user<|end_header_id|>{prompt}<|eot_id|>"
            f"<|start_header_id|>assistant<|end_header_id|>\\n\\n"
        )

        return final_prompt

    def predibase_llm_api(llm_prompt):
        # JSON payload for the request
        data = {
            "inputs": llm_prompt,
            "parameters": {
                "adapter_id": "issue_identifier/1",
                "adapter_source": "pbase",
                "max_new_tokens": 30,
                "temperature": 0.0  # Set to the lowest temperature for consistency
            }
        }

        url = "https://serving.app.predibase.com/363ca091/deployments/v2/llms/llama-3-1-8b-instruct/generate"

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer pb_ik19emsOXxWxqbKTOJaZZg"
        }

        # Make the POST request
        response = requests.post(url, json=data, headers=headers)

        try:
            response_json = response.json()
        except ValueError:
            response_json = {}

        generated_text = response_json.get('generated_text', 'No generated_text found in response.')

        # If the generated_text is a list, join its elements into a single string
        if isinstance(generated_text, list):
            generated_text = ' '.join(generated_text)

        return generated_text

    llm_prompt = create_llm_prompt(predictor_query)
    legal_converted_query = predibase_llm_api(llm_prompt)
    sentences = sent_tokenize(legal_converted_query)
    complete_sentences = [sentence for sentence in sentences if sentence.endswith(('.', '?', '!'))]
    # If complete_sentences is a list with one element, return that element
    if len(complete_sentences) == 1:
        return complete_sentences[0]
    else:
        return complete_sentences


def mlc_prediction(predictor_query):
    def generate_labels():
        label_mapping = {'': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                         '11': 11, '12': 12, '13': 13, '14': 14, '15': 15, '18': 16, 'P1-1': 17, 'P1-2': 18, 'P1-3': 19,
                         'P4-2': 20, 'P4-4': 21, 'P6-1': 22, 'P7-1': 23, 'P7-2': 24, 'P7-3': 25, 'P7-4': 26}




        
        reverse_label_mapping = {v: k for k, v in label_mapping.items()}

        label_summaries = {
            'P6-1': "Abolition of the death penalty (Protocol 6, Article 1)",
            'P7-4': "Right not to be tried or punished twice (Protocol 7, Article 4)",
            'P7-1': "Procedural safeguards relating to the expulsion of aliens (Protocol 7, Article 1)",
            'P1-1': "Protection of property (Protocol 1, Article 1)",
            'P7-2': "Right of appeal in criminal matters (Protocol 7, Article 2)",
            'P1-3': "Right to free elections (Protocol 1, Article 3)",
            'P4-4': "Prohibition of collective expulsion of aliens (Protocol 4, Article 4)",
            'P1-2': "Right to education (Protocol 1, Article 2)",
            'P7-3': "Compensation for wrongful conviction (Protocol 7, Article 3)",
            'P4-2': "Freedom of movement (Protocol 4, Article 2)",
            '1': "Obligation to respect human rights (Article 1)",
            '2': "Right to life (Article 2)",
            '3': "Prohibition of torture (Article 3)",
            '4': "Prohibition of slavery and forced labor (Article 4)",
            '5': "Right to liberty and security (Article 5)",
            '6': "Right to a fair trial (Article 6)",
            '7': "No punishment without law (Article 7)",
            '8': "Right to respect for private and family life (Article 8)",
            '9': "Freedom of thought, conscience, and religion (Article 9)",
            '10': "Freedom of expression (Article 10)",
            '11': "Freedom of assembly and association (Article 11)",
            '12': "Right to marry (Article 12)",
            '13': "Right to an effective remedy (Article 13)",
            '14': "Prohibition of discrimination (Article 14)",
            '15': "Derogation in time of emergency (Article 15)",
            '18': "Limitation on use of restrictions on rights (Article 18)",
            '25': "Right to individual petition (Article 25, prior to Protocol 11)",
            '34': "Right to individual application to the court (Article 34)",
            '37': "Striking out applications (Article 37)",
            '': "No violation"
        }

        return reverse_label_mapping, label_summaries
    
    reverse_label_mapping, label_summaries = generate_labels()
    inputs = tokenizer(predictor_query, padding=True, truncation=True, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.sigmoid(logits)

    # Convert predictions to labels with classifier index, article, summary, and probability
    predicted_labels = [(i, reverse_label_mapping[i], label_summaries[reverse_label_mapping[i]], probabilities[0, i].item())
                        for i in range(probabilities.size(1))]

    print(f"Predicted Labels: {predicted_labels}")
    return predicted_labels







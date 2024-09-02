from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification
import torch

# Define the paths where the models and tokenizers are saved
search_model_path = "models/all-MiniLM-L6-v2"
classifier_model_path = "models/roberta_echr_truncated_facts_all_labels"

# Load the search model and tokenizer from the local directory
search_tokenizer = AutoTokenizer.from_pretrained(search_model_path)
search_model = AutoModel.from_pretrained(search_model_path)

def get_search_model_and_tokenizer():
    return search_model, search_tokenizer

# Load the classifier model and tokenizer from the local directory
classifier_tokenizer = AutoTokenizer.from_pretrained(classifier_model_path)
classifier_model = AutoModelForSequenceClassification.from_pretrained(classifier_model_path)

def get_classifier_model_and_tokenizer():
    return classifier_model, classifier_tokenizer

def get_torch():
    return torch

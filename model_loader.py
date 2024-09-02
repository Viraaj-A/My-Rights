from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification
import torch

search_model_id = "sentence-transformers/all-MiniLM-L6-v2"
search_tokenizer = AutoTokenizer.from_pretrained(search_model_id)
search_model = AutoModel.from_pretrained(search_model_id)

def get_search_model_and_tokenizer():
    return search_model, search_tokenizer

classifier_model_id = "LawItApps/roberta_echr_truncated_facts_all_labels"
classifier_tokenizer = AutoTokenizer.from_pretrained(classifier_model_id)
classifier_model = AutoModelForSequenceClassification.from_pretrained(classifier_model_id)

def get_classifier_model_and_tokenizer():
    return classifier_model, classifier_tokenizer

def get_torch():
    return torch
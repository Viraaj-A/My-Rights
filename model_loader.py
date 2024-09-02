from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification
import torch
import os

def setup_model_paths():
    # Get the current working directory
    base_path = os.getcwd()

    # Define the paths for the models
    search_model_path = os.path.join(base_path, 'models', 'all-MiniLM-L6-v2')
    classifier_model_path = os.path.join(base_path, 'models', 'roberta_echr_truncated_facts_all_labels')

    # Ensure that the directories exist
    if not os.path.exists(search_model_path):
        raise FileNotFoundError(f"Search model path does not exist: {search_model_path}")
    if not os.path.exists(classifier_model_path):
        raise FileNotFoundError(f"Classifier model path does not exist: {classifier_model_path}")

    return search_model_path, classifier_model_path

# Run the setup function to get the paths
search_model_path, classifier_model_path = setup_model_paths()

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

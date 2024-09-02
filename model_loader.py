from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification
import torch
import os

def setup_and_download_models():
    # Get the current working directory
    base_path = os.getcwd()

    # Define the paths where the models will be saved
    model_download_dir = os.path.join(base_path, 'models')
    search_model_dir = os.path.join(model_download_dir, 'all-MiniLM-L6-v2')
    classifier_model_dir = os.path.join(model_download_dir, 'roberta_echr_truncated_facts_all_labels')

    # Ensure the directories exist
    os.makedirs(search_model_dir, exist_ok=True)
    os.makedirs(classifier_model_dir, exist_ok=True)

    # Download and save the search model and tokenizer (one-time setup)
    AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2', cache_dir=search_model_dir)
    AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2', cache_dir=search_model_dir)

    AutoTokenizer.from_pretrained('roberta-base', cache_dir=classifier_model_dir)
    AutoModelForSequenceClassification.from_pretrained('roberta-base', cache_dir=classifier_model_dir)

def load_models():
    # Get the current working directory
    base_path = os.getcwd()

    # Define the paths where the models were saved
    search_model_path = os.path.join(base_path, 'models', 'all-MiniLM-L6-v2')
    classifier_model_path = os.path.join(base_path, 'models', 'roberta_echr_truncated_facts_all_labels')

    # Load the search model and tokenizer from the local directory
    search_tokenizer = AutoTokenizer.from_pretrained(search_model_path)
    search_model = AutoModel.from_pretrained(search_model_path)

    # Load the classifier model and tokenizer from the local directory
    classifier_tokenizer = AutoTokenizer.from_pretrained(classifier_model_path)
    classifier_model = AutoModelForSequenceClassification.from_pretrained(classifier_model_path)

    return search_tokenizer, search_model, classifier_tokenizer, classifier_model

# Run the setup function to download the models if they aren't already downloaded
setup_and_download_models()

# Load the models from the downloaded paths
search_tokenizer, search_model, classifier_tokenizer, classifier_model = load_models()

def get_search_model_and_tokenizer():
    return search_model, search_tokenizer

def get_classifier_model_and_tokenizer():
    return classifier_model, classifier_tokenizer

def get_torch():
    return torch

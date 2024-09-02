from app import init_app
import faiss
from model_loader import get_search_model_and_tokenizer, get_classifier_model_and_tokenizer, get_torch

app = init_app()

Development = True


if Development == False:
    if __name__ == "__main__":
        app.run(debug=False)
else:
    if __name__ == "__main__":
        def load_models():
            index_with_ids = faiss.read_index('models/index_with_ids.index')
            search_model, search_tokenizer = get_search_model_and_tokenizer()
            classifier_model, classifier_tokenizer = get_classifier_model_and_tokenizer()
            torch = get_torch()

            return index_with_ids, search_model, search_tokenizer, classifier_model, classifier_tokenizer, torch
        index_with_ids, search_model, search_tokenizer, classifier_model, classifier_tokenizer, torch = load_models()
        app.run(debug=True)


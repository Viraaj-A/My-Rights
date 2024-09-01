from sqlalchemy import text, func, or_
import numpy as np
from model_loader import get_search_model_and_tokenizer, get_torch

model, tokenizer = get_search_model_and_tokenizer()
torch = get_torch()


def full_text_search(search_term, db, DisplayCases, date_from=None, date_to=None, originating_bodies=[], importance_levels=[], respondent_states=[]):
    # Start by building the base query with possible filters
    query = db.session.query(
        DisplayCases.judgment_url,
        DisplayCases.title, DisplayCases.importance_level,
        DisplayCases.judgment_date, DisplayCases.judgment_facts, DisplayCases.judgment_conclusion
    )

    # Apply filters if provided
    if originating_bodies:
        query = query.filter(DisplayCases.originating_body.in_(originating_bodies))
    if importance_levels:
        query = query.filter(DisplayCases.importance_level.in_(importance_levels))
    if respondent_states:
        query = query.filter(or_(*[DisplayCases.respondent_state.like(f"%{state}%") for state in respondent_states]))
    if date_from:
        query = query.filter(DisplayCases.judgment_date >= date_from)
    if date_to:
        query = query.filter(DisplayCases.judgment_date <= date_to)

    # Only apply full-text search if there is a search term
    if search_term:
        squery = func.websearch_to_tsquery('english', search_term)
        query = query.add_columns(
            func.ts_headline('english', DisplayCases.judgment_full_text, squery,
                             'StartSel = <b>, StopSel = </b>, ShortWord = 3, MinWords = 50, MaxWords = 60').label('highlighted_text'),
            func.ts_rank_cd(DisplayCases.search_vector, squery).label('rank')
        ).filter(
            DisplayCases.search_vector.op('@@')(squery)
        ).order_by(
            text('rank DESC')
        )

    return query




def semantic_query_normalisation(query):
    def generate_embedding(query):
        inputs = tokenizer(query, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
        # Mean pooling
        embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings.squeeze().cpu().numpy()

    # Generate the embedding for the query
    query_embedding = generate_embedding(query)

    # Normalize the query embedding
    def normalize_single(vector):
        norm = np.linalg.norm(vector)
        return vector / norm

    normalized_query_embedding = normalize_single(query_embedding)

    return normalized_query_embedding

def semantic_search(query, index_with_ids, k):
    query_to_process = semantic_query_normalisation(query)
    distances, indices = index_with_ids.search(query_to_process[np.newaxis, :], k)
    nearest_ids = indices[0]
    return nearest_ids


def semantic_search_with_filters(query, db, DisplayCases, date_from=None, date_to=None, originating_bodies=[], importance_levels=[], respondent_states=[], index_with_ids=None):
    # Perform the semantic search
    nearest_ids = semantic_search(query, index_with_ids, k=50)

    # Start building the base query
    query = db.session.query(
        DisplayCases.judgment_url,
        DisplayCases.title,
        DisplayCases.importance_level,
        DisplayCases.judgment_date,
        DisplayCases.judgment_facts,
        DisplayCases.judgment_conclusion
    )

    # Apply filters if provided
    if originating_bodies:
        query = query.filter(DisplayCases.originating_body.in_(originating_bodies))
    if importance_levels:
        query = query.filter(DisplayCases.importance_level.in_(importance_levels))
    if respondent_states:
        query = query.filter(or_(*[DisplayCases.respondent_state.like(f"%{state}%") for state in respondent_states]))
    if date_from:
        query = query.filter(DisplayCases.judgment_date >= date_from)
    if date_to:
        query = query.filter(DisplayCases.judgment_date <= date_to)

    # Apply semantic search filter
    if nearest_ids.size > 0:
        query = query.filter(DisplayCases.id.in_(nearest_ids.tolist()))

    return query

def prediction_semantic(query, db, DisplayCases, index_with_ids=None):
    # Perform the semantic search
    nearest_ids = semantic_search(query, index_with_ids, k=5)

    # Start building the base query
    query = db.session.query(
        DisplayCases.judgment_url,
        DisplayCases.title,
        DisplayCases.importance_level,
        DisplayCases.judgment_date,
        DisplayCases.judgment_facts,
        DisplayCases.judgment_conclusion
    )

    # Apply semantic search filter
    if nearest_ids.size > 0:
        query = query.filter(DisplayCases.id.in_(nearest_ids.tolist()))

    return query
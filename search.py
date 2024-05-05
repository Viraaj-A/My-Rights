from sqlalchemy import text, func


def full_text_search(search_term, db, DisplayCases):
    squery = func.websearch_to_tsquery('english', search_term)
    query = db.session.query(
        DisplayCases.judgment_url,
        DisplayCases.title, DisplayCases.importance_level,
        DisplayCases.judgment_date, DisplayCases.judgment_facts, DisplayCases.judgment_conclusion,
        func.ts_headline('english', DisplayCases.judgment_full_text, squery,
                         'StartSel = <b>, StopSel = </b>, ShortWord = 3, MinWords = 50, MaxWords = 60').label(
            'highlighted_text'),
        func.ts_rank_cd(DisplayCases.search_vector, squery).label('rank')
    ).where(
        DisplayCases.search_vector.op('@@')(squery)
    ).order_by(
        text('rank DESC')
    )
    return query


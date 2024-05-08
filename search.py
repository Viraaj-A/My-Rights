from sqlalchemy import text, func, or_


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

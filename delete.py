



@app.route('/results', methods=['GET', 'POST'])
def results():
    form = SearchForm()
    case = text_search(form.searched.data)[0]  # Passing user query into search function
    query = form.data
    return render_template('results.html', form=form, searched=case, query=query)

    """
    SELECT item_id, requests_url, ts_headline('english', entire_text, query, 'StartSel = <em>, StopSel = </em>, ShortWord = 1') as entire_text_highlights
    FROM (SELECT item_id, requests_url, entire_text, ts_rank_cd(textsearchable_index_col, query) AS rank, query
    FROM processed_judgment_html, websearch_to_tsquery('english', %s) AS query
    WHERE textsearchable_index_col @@ query
    ORDER BY rank DESC
    LIMIT 10) AS query_results;
"""

<div class="container">
			<div class="row border">
					<p><a href="{{result[1]}}" title="">{{result[0]}}</a></p>
					{{result[2]|safe}}
			</div>
		</div>



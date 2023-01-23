from flask import Flask, render_template, session
from webforms import SearchForm, QuestionnaireForm
from search import text_search
from questionnaire_analysis import return_results
from questionnaire_cases import ecli_results
from all_cases import DF_All_Cases
from flask_paginate import Pagination, get_page_args
import time


def init_app():
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False)

    app.config['SECRET_KEY'] = 'any secret string'

    app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'


    with app.app_context():

        # Importing Routes
        @app.route('/')
        def index():
            return render_template('index.html')

        @app.route('/about/')
        def about():
            return render_template('about.html')

        @app.route('/search/')
        def search():
            form = SearchForm()
            search_rights = f'Enter search, for example, "protection against torture"'
            return render_template('search.html', form=form, input_search=search_rights)

        @app.route('/results/', methods=['GET', 'POST'])
        def results():
            search_form = SearchForm()
            case = text_search(search_form.searched.data)[0]
            return render_template('results.html', form=search_form, searched=case, query=search_form.searched.data)

        @app.route('/questionnaire/')
        def questionnaire():
            q_form = QuestionnaireForm()
            return render_template('questionnaire.html', q_form=q_form)

        @app.route('/questionnaire/1/', methods=['GET', 'POST'])
        def navigate_forward():
            q_form = QuestionnaireForm()
            physical_q = q_form.physical_q.data
            procedural_q = q_form.procedural_q.data
            mental_q = q_form.mental_q.data
            age_q = q_form.age_q.data
            gender_q = q_form.gender_q.data
            family_q = q_form.family_q.data
            community_q = q_form.community_q.data
            nationality_q = q_form.nationality_q.data
            property_q = q_form.property_q.data

            applicable_rights, remaining_rights = return_results(procedural_q, physical_q, mental_q, age_q,
                                                                 gender_q, family_q, community_q, nationality_q,
                                                                 property_q)

            session["search_rights"] = applicable_rights
            return render_template('questionnaire_results.html', applicable_rights=applicable_rights,
                                   remaining_rights=remaining_rights)



        @app.route('/questionnaire_cases/', methods=['GET', 'POST'])
        def questionnaire_cases():
            #Obtain session data and access empty DF class to load cases
            search_rights = session.get("search_rights", None)
            total_no = len(search_rights)
            ecli_list, applicable_numbers = ecli_results(search_rights)
            applicable_numbers = applicable_numbers['count'].tolist()
            all_cases = DF_All_Cases.dataFrameHolder
            filtered_cases = all_cases.set_index('ecli').loc[ecli_list].reset_index()
            del all_cases
            filtered_cases = filtered_cases.values.tolist()

            #Pagination
            page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
            def get_cases(offset=0, per_page=10):
                return filtered_cases[offset: offset + per_page]
            pagination_cases = get_cases(offset=offset, per_page=per_page)
            del filtered_cases
            pagination = Pagination(css_framework='bootstrap3', page=page, per_page=per_page,
                                    total=len(ecli_list))
            return render_template('questionnaire_paginated_cases.html', cases=pagination_cases, total_no=total_no,
                                   page=page, per_page=per_page,
                                   applicable_numbers=applicable_numbers, pagination=pagination)



        #Importing Dash Application
        from plotly_dash.__init__ import init_dashboard
        app = init_dashboard(app)


        return app

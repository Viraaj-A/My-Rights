from flask import Flask, render_template, session, request
from webforms import SearchForm, QuestionnaireForm
from search import text_search
from questionnaire_analysis import return_results
from questionnaire_cases import ecli_results
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.sql.expression import case
from sqlalchemy import text

def init_app():
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False)

    app.config['SECRET_KEY'] = 'any secret string'

    app.config[
        "SQLALCHEMY_DATABASE_URI"] = 'postgresql://doadmin:AVNS_SbC_UqXYG665R47kxY4@db-postgresql-fra1-kyr-0001-do-user-12476250-0.b.db.ondigitalocean.com:25060/defaultdb'

    app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'


    with app.app_context():


        db = SQLAlchemy(app)
        Base = automap_base()
        Base.prepare(db.engine, reflect=True)
        English_Search = Base.classes.english_search

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

        # @app.route('/questionnaire_cases/', methods=['GET', 'POST'])
        # def questionnaire_cases():
        #     query = "Questionnaire Results"
        #     search_rights = session.get("search_rights", None)
        #     case = ecli_results(search_rights)
        #     return render_template('questionnaire_cases.html', searched=case, query=query)


        #Importing Dash Application
        from plotly_dash.__init__ import init_dashboard
        app = init_dashboard(app)


        #Pagination of questionnaire case results
        @app.route('/questionnaire_cases/', methods=['GET', 'POST'])
        def questionnaire_cases():
            search_rights = session.get("search_rights", None)
            ecli_list = ecli_results(search_rights)
            rows_per_page = 5
            page = request.args.get('page', 1, type=int)
            stmt = case(value=English_Search.ecli, whens={ecli: i for i, ecli in enumerate(ecli_list)})
            cases = db.session.query(English_Search, stmt).paginate(page=page, per_page=rows_per_page)
            paginated_cases = cases.items
            return render_template('test.html', cases=paginated_cases)
            session.close()



        return app

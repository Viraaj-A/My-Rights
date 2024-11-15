import flask
from flask import Flask, render_template, request, current_app
from webforms import SearchForm, QuestionnaireForm, PredictorForm
from search import full_text_search, semantic_search_with_filters, prediction_semantic
from questionnaire_analysis import return_results
from questionnaire_cases import ecli_results
from prediction_workflow import issue_translator, mlc_prediction
from all_cases import DF_All_Cases
from flask_paginate import Pagination, get_page_args
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, text, case, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.dialects.postgresql import TSVECTOR
from autocorrect import Speller
from scraping_files.scheduler import start_scheduler
from turbo_flask import Turbo
import faiss
import os
import faiss
from model_loader import get_search_model_and_tokenizer, get_classifier_model_and_tokenizer, get_torch
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    """Construct core Flask application with embedded Dash app and loaded ML models."""
    app = Flask(__name__, instance_relative_config=False)

    # Configure the app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config[
        "SQLALCHEMY_DATABASE_URI"] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.secret_key = os.getenv('SECRET_KEY')

    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

    # Initialize NLTK and models
    with app.app_context():
        run_nltk()
        print("Loading FAISS index and models...")
        index_with_ids = faiss.read_index('models/index_with_ids.index')
        search_model, search_tokenizer = get_search_model_and_tokenizer()
        classifier_model, classifier_tokenizer = get_classifier_model_and_tokenizer()
        torch = get_torch()

        current_app.index_with_ids = index_with_ids
        current_app.search_model = search_model
        current_app.search_tokenizer = search_tokenizer
        current_app.classifier_model = classifier_model
        current_app.classifier_tokenizer = classifier_tokenizer
        current_app.torch = torch
        print("Models loaded successfully.")

    # Importing and initializing the Dash application
    from plotly_dash import init_dashboard
    app = init_dashboard(app)

    return app


def run_nltk():
    """Initialize NLTK resources."""
    nltk_data_path = os.path.join(os.getcwd(), 'models', 'nltk_files')
    os.environ["NLTK_DATA"] = nltk_data_path
    import nltk
    os.makedirs(nltk_data_path, exist_ok=True)
    nltk.data.path.append(nltk_data_path)
    nltk.download('punkt', download_dir=nltk_data_path)
    nltk.download('punkt_tab', download_dir=nltk_data_path)


app = create_app()

# Initialize database and other components within the app context
with app.app_context():
    db = SQLAlchemy(app)
    Base = automap_base()
    turbo = Turbo(app)


    class DisplayCases(Base):
        __tablename__ = "display_cases"
        existing = True

        id = Column(Integer, primary_key=True)
        title = Column(Text)
        judgment_url = Column(Text)
        originating_body = Column(Text)
        importance_level = Column(Text)
        respondent_state = Column(Text)
        judgment_date = Column(Date)
        judgment_facts = Column(Text)
        judgment_conclusion = Column(Text)
        judgment_full_text = Column(Text)
        search_vector = Column(TSVECTOR)


    Base.metadata.create_all(db.engine)
    Session = sessionmaker(bind=db.engine)
    session = Session()

# Importing Routes
@app.route('/')
def index():
    form = PredictorForm()
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
    form = SearchForm(request.form)
    page = request.args.get('page', 1, type=int)

    query = request.args.get('searched', '') if request.method == 'GET' else form.searched.data
    spell = Speller()
    corrected = spell(query)
    if corrected == query:
        corrected = None

    originating_bodies = request.args.getlist('originating_body') if request.method == 'GET' else [x for x in
                                                                                                   form.originating_body.data
                                                                                                   if x]
    importance_levels = request.args.getlist('importance_level') if request.method == 'GET' else [x for x in
                                                                                                  form.importance_level.data
                                                                                                  if x]
    respondent_states = request.args.getlist('respondent_state') if request.method == 'GET' else [x for x in
                                                                                                  form.respondent_state.data
                                                                                                  if x]
    date_from = request.args.get('date_from', '') if request.method == 'GET' else form.date_from.data
    date_to = request.args.get('date_to', '') if request.method == 'GET' else form.date_to.data

    if form.semantic_submit.data or request.args.get('semantic_submit'):
        paginate = semantic_search_with_filters(
            query, db, DisplayCases, date_from, date_to, originating_bodies,
            importance_levels, respondent_states,
            current_app.index_with_ids, current_app.search_model, current_app.search_tokenizer, current_app.torch
        ).paginate(page=page, per_page=10)
    else:
        paginate = full_text_search(
            query, db, DisplayCases, date_from, date_to, originating_bodies,
            importance_levels, respondent_states
        ).paginate(page=page, per_page=10)

    start_case = (page - 1) * paginate.per_page + 1
    end_case = min(page * paginate.per_page, paginate.total)

    return render_template(
        'semantic_results_fragment.html' if form.semantic_submit.data or request.args.get(
            'semantic_submit') else 'results_fragment.html',
        pagination=paginate,
        query=query,
        corrected=corrected,
        form=form,
        originating_bodies=originating_bodies,
        importance_levels=importance_levels,
        respondent_states=respondent_states,
        date_from=date_from,
        date_to=date_to,
        start_case=start_case,
        end_case=end_case
    )


@app.route('/prediction/')
def prediction():
    form = PredictorForm()
    return render_template('prediction.html', form=form)


@app.route('/generate_text', methods=['POST'])
def generate_text():
    user_prompt = request.form['prompt']
    spell = Speller()
    corrected = spell(user_prompt)
    print(user_prompt)
    legal_prompt = issue_translator(corrected if corrected != user_prompt else user_prompt)
    print(legal_prompt)
    return render_template('issue_converter_fragments.html', legal_prompt=legal_prompt)


@app.route('/mlc_predict', methods=['POST'])
def mlc_predict():
    legal_prompt = request.form.get('edited_text') or request.form['legal_prompt']
    predicted_violations = list(
        mlc_prediction(legal_prompt, current_app.classifier_model, current_app.classifier_tokenizer, current_app.torch))

    return render_template('mlc_prediction_fragment.html', predicted_violations=predicted_violations,
                           legal_prompt=legal_prompt)


@app.route('/prediction_cases', methods=['POST'])
def prediction_cases():
    legal_prompt = request.form.get('edited_text') or request.form['legal_prompt']
    paginate = prediction_semantic(
        legal_prompt, db, DisplayCases, current_app.index_with_ids,
        current_app.search_model, current_app.search_tokenizer, current_app.torch
    ).paginate(page=1, per_page=5)

    return render_template('prediction_semantic_fragments.html', pagination=paginate)


Development = False


if Development == False:
    if __name__ == "__main__":
        app.run(debug=False)
else:
    if __name__ == "__main__":
        app.run(debug=True)



        ## The following code represents the unused questionnaire to identify relevant human rights harms. It has been
        ## replaced by the Predictor

        # @app.route('/questionnaire/')
        # def questionnaire():
        #     q_form = QuestionnaireForm()
        #     return render_template('questionnaire.html', q_form=q_form)

        # @app.route('/questionnaire_cases/', methods=['GET', 'POST'])
        # def questionnaire_cases():
        #     #Obtain session data and access empty DF class to load cases
        #     search_rights = flask.session.get("search_rights", None)
        #     total_no = len(search_rights)
        #     ecli_list, applicable_numbers = ecli_results(search_rights)
        #     applicable_numbers = applicable_numbers['count'].tolist()
        #     all_cases = DF_All_Cases.dataFrameHolder
        #     filtered_cases = all_cases.set_index('ecli').loc[ecli_list].reset_index()
        #     del all_cases
        #     filtered_cases = filtered_cases.values.tolist()
        #
        #     #Pagination
        #     page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        #     def get_cases(offset=0, per_page=10):
        #         return filtered_cases[offset: offset + per_page]
        #     pagination_cases = get_cases(offset=offset, per_page=per_page)
        #     del filtered_cases
        #     pagination = Pagination(css_framework='bootstrap3', page=page, per_page=per_page,
        #                             total=len(ecli_list))
        #     return render_template('questionnaire_paginated_cases.html', cases=pagination_cases, total_no=total_no,
        #                            page=page, per_page=per_page,
        #                            applicable_numbers=applicable_numbers, pagination=pagination)

        # @app.route('/questionnaire/1/', methods=['GET', 'POST'])
        # def navigate_forward():
        #     q_form = QuestionnaireForm()
        #     physical_q = q_form.physical_q.data
        #     procedural_q = q_form.procedural_q.data
        #     mental_q = q_form.mental_q.data
        #     age_q = q_form.age_q.data
        #     gender_q = q_form.gender_q.data
        #     family_q = q_form.family_q.data
        #     community_q = q_form.community_q.data
        #     nationality_q = q_form.nationality_q.data
        #     property_q = q_form.property_q.data
        #
        #     applicable_rights, remaining_rights = return_results(procedural_q, physical_q, mental_q, age_q,
        #                                                          gender_q, family_q, community_q, nationality_q,
        #                                                          property_q)
        #
        #     flask.session["search_rights"] = applicable_rights
        #     return render_template('questionnaire_results.html', applicable_rights=applicable_rights,
        #                            remaining_rights=remaining_rights)
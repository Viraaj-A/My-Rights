from flask import Flask, render_template
from webforms import SearchForm
from search import text_search

def init_app():
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False)

    app.config['SECRET_KEY'] = 'any secret string'

    with app.app_context():
        # Importing Routes
        @app.route('/')
        def index():
            return render_template('index.html')

        @app.route('/questionnaire/')
        def questionnaire():
            return render_template('questionnaire.html')

        @app.route('/about/')
        def about():
            return render_template('about.html')

        @app.route('/search/')
        def search():
            form = SearchForm()
            return render_template('search.html', form=form)

        @app.route('/results', methods=['GET', 'POST'])
        def results():
            form = SearchForm()
            case = text_search(form.data)[0] #Passing user query into search function
            return render_template('results.html', form=form, searched=case, query=form.data)

        #Importing Dash Application
        from plotly_dash.__init__ import init_dashboard
        app = init_dashboard(app)


        return app
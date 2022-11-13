from flask import Flask, render_template, redirect
from webforms import SearchForm
from search import text_search

def init_app():
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False)

    with app.app_context():
        # Import Dash application

        from plotly_dash.__init__ import init_dashboard
        @app.route('/')
        def index():
            return render_template('index.html')

        @app.route('/about/')
        def about():
            return render_template('about.html')

        @app.route('/search/')
        def search():
            return render_template('search.html', form=search)

        @app.route('/results', methods=['GET', 'POST'])
        def results():
            form = SearchForm()
            case = text_search(form.searched.data)[0]
            return render_template('results.html', form=form, searched=case)

        app = init_dashboard(app)


        return app
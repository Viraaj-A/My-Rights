from dash import Dash, html, dcc, Input, Output, State, dash_table
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
from plotly_dash.layout import html_layout
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import json

development = False

#Connecting with SQLAlchemy
if development == True:
    connection_string = 'postgres:password@localhost/restore_Oct_13'
else:
    connection_string = 'doadmin:AVNS_SbC_UqXYG665R47kxY4@db-postgresql-fra1-kyr-0001-do-user-12476250-0.b.db.ondigitalocean.com:25060/defaultdb'

engine = create_engine(f'postgresql+psycopg2://{connection_string}',poolclass=NullPool)


# ********************* DASH APP *********************
def init_dashboard(server):
    # ********************* DATA IMPORT *********************
    # Function to initialise the main dataframe containing relevant judgment details
    def discrete_data_df():
        df_english_raw = pd.read_sql(text("""Select * from processed_english_case_detail"""), engine.connect(), parse_dates=["judgment_date"])
        df_french_raw = pd.read_sql(text('Select * from processed_french_case_detail'), engine.connect(), parse_dates=["judgment_date"])
        df = pd.concat([df_french_raw, df_english_raw]).drop_duplicates(subset='ecli', keep="first")
        del df_french_raw, df_english_raw
        # Associate country iso codes to the respondent information
        df_country_codes = pd.read_csv('data/map/country_iso_codes.csv')
        df_country_group = pd.merge(df, df_country_codes, on='respondent', how='inner')
        del df
        df_country_group = df_country_group.drop(
            columns=['strasbourg', 'keywords', 'application_number', 'item_id', 'id'])
        # Retain only the year information of the cases
        df_country_group['judgment_date'] = df_country_group['judgment_date'].dt.year
        df_country_group['articles_considered'] = df_country_group['articles_considered'].str.replace(';', ',',
                                                                                                      regex=False)
        df_country_group['articles_considered'] = df_country_group.articles_considered.replace(regex=['-.'], value='')
        df_country_group['articles_considered'] = df_country_group.articles_considered.replace(regex=['more…'],
                                                                                               value='')
        df_country_group['articles_considered'] = df_country_group.articles_considered.replace(r'[^a-zA-Z0-9]', ',',
                                                                                               regex=True)
        df_country_group['articles_considered'] = df_country_group.articles_considered.replace(r',,', ',', regex=True)
        df_country_group['articles_considered'] = df_country_group.articles_considered.str.rstrip(',')
        del df_country_codes
        return df_country_group

    # Retrieves geojson 3 digit location information
    def geojson_data():
        # loading GeoJSON
        handle = open('data/map/europe.geojson')
        geojson = json.load(handle)
        return geojson

    # Helper functions for dropdowns and slider
    def create_dropdown_options(series):
        options = [{'label': i, 'value': i} for i in series.sort_values().unique()]
        return options

    def create_dropdown_value(series):
        value = series.sort_values().unique().tolist()
        return value

    # List of all convention articles
    def create_article_list():
        articles = []
        for i in range(1, 59):
            articles.append(str(i))
        for j in range(1, 13):
            articles.append(f'P{j}')
        return articles

    df_country_group = discrete_data_df()
    geojson = geojson_data()
    article_list = create_article_list()

    #Dash App initilisation
    dash_app = Dash(server=server,
        routes_pathname_prefix="/visualisation/",)

    dash_app.index_string = html_layout


    # App layout
    dash_app.layout = html.Div(className='container',
    children=[
     # First Row
     html.Div(className='row',
              children=[
                  # LEFT Column INPUTS
                  html.Div(className="col-sm-5",
                           children=[
                               html.Div([
                                   html.Label(
                                       "Choose countries that you are interested in, for example:",
                                        style={'margin-top': 6, 'margin-bottom': 0}),
                                   dcc.Dropdown(
                                       options=create_dropdown_options(
                                           df_country_group[
                                               'respondent']),
                                       value=["Germany", "Spain",
                                              "Russia", "France",
                                              "United Kingdom"],
                                       id='respondent_dropdown',
                                       multi=True,
                                       style={'margin-bottom': 15})
                               ]),
                               html.Div([
                                   html.Label(
                                       "Select your human rights",
                                        style={'margin-bottom': 0}),
                                   dcc.Dropdown(
                                       id="articles_dropdown",
                                       multi=True,
                                       options=article_list,
                                       value=["1"],
                                       style={'margin-bottom': 15})
                               ]),
                               html.Div([
                                   html.Label(
                                       "Select the importance of the judgment you want to see",
                                        style={'margin-bottom': 0}),
                                   dcc.Dropdown(
                                       id="importance_rating",
                                       multi=True,
                                       options=create_dropdown_options(
                                           df_country_group[
                                               'importance_number']),
                                       value=create_dropdown_value(
                                           df_country_group[
                                               'importance_number']),
                                       style={'margin-bottom': 15}
                                       )
                               ]),
                               html.Div([
                                   html.Label(
                                       "Choose if you want to see if judges had different opinions",
                                        style={'margin-bottom': 0}),
                                   dcc.Dropdown(
                                       id="separate_opinion",
                                       multi=True,
                                       options=create_dropdown_options(
                                           df_country_group[
                                               'separate_opinion']),
                                       value=create_dropdown_value(
                                           df_country_group[
                                               'separate_opinion']),
                                       style={'margin-bottom': 15}
                                       )
                               ]),
                               html.Div([
                                   html.Label(
                                       "Choose the court you want",
                                        style={'margin-bottom': 0}),
                                   dcc.Dropdown(id="court",
                                                multi=True,
                                                options=create_dropdown_options(
                                                    df_country_group[
                                                        'court']),
                                                value=create_dropdown_value(
                                                    df_country_group[
                                                        'court']),
                                                style={'margin-bottom': 15}
                                                )
                               ]),
                               html.Div([
                                   html.Label(
                                       "Select the years for when judgments were made",
                                        style={'margin-bottom': 0}),
                                   dcc.RangeSlider(
                                       min=df_country_group[
                                           'judgment_date'].min(),
                                       max=df_country_group[
                                           'judgment_date'].max(),
                                       step=1,
                                       marks={1960: '1960',
                                              1970: '1970',
                                              1980: '1980',
                                              1990: '1990',
                                              2000: '2000',
                                              2010: '2010',
                                              2020: '2020',
                                              2030: '2030'},
                                       value=[1960, 2022],
                                       id='year_slider')
                               ]),
                               html.Div([
                                   html.Br(),
                                   html.Button(
                                       id='submit-button-state',
                                       n_clicks=0,
                                       children='Submit',
                                       className='btn btn-default')
                               ])
                           ]
                           ),
                  # RIGHT COLUMN OUTPUT GRAPHS
                  html.Div(className="col-sm-7",
                           children=[
                               html.Div(className='row', children=[
                                   html.Div(
                                       className="col-xs-5 col-xs-offset-1",
                                       children=[
                                           html.H5(
                                               id='total_cases')]),
                                   html.Div(
                                       className="col-xs-5 col-xs-offset-1",
                                       children=[
                                           html.H5(
                                               id='filtered_cases')])
                               ]),
                               html.Div(className='row', children=[
                                   dcc.Loading([
                                   dcc.Graph(id='world_map',
                                             config={
                                                 'displayModeBar': False})]),
                                   dcc.Loading([
                                   dcc.Graph(id='importance_graph',
                                             config={
                                                 'displayModeBar': False})]),
                                   html.Br(),
                                   dcc.Loading([
                                   dcc.Graph(id='article_line',
                                             config={
                                                 'displayModeBar': False})])
                               ])
                           ])
              ]),
     # Second Row
     html.Div(className='row',
              children=[
                  html.Div(className="col-xs-12",
                           children=[
                               html.Div(id='data_table')
                           ])
              ])
    ]
    )


    @dash_app.callback(
        [
            Output('importance_graph', 'figure'),
            Output('world_map', 'figure'),
            Output('article_line', 'figure'),
            Output('total_cases', 'children'),
            Output('filtered_cases', 'children'),
            Output('data_table', 'children')
        ]
        ,
        [
            State('respondent_dropdown', 'value'),
            State('articles_dropdown', 'value'),
            State('importance_rating', 'value'),
            State('separate_opinion', 'value'),
            State('court', 'value'),
            State('year_slider', 'value'),
            Input('submit-button-state', 'n_clicks')
        ]
    )
    def update_graph(respondent_value, articles_values, importance_value, opinion_value, court_value, year_value,
                     n_clicks):
        filtered_df = df_country_group.copy()

        if n_clicks is not None:
            if len(respondent_value) > 0:
                filtered_df = filtered_df[filtered_df['respondent'].isin(respondent_value)]
            elif len(respondent_value) == 0:
                raise PreventUpdate

            if len(articles_values) > 0:
                pattern = '\\b(' + '|'.join(articles_values) + ')\\b'
                filtered_df = filtered_df[filtered_df['articles_considered'].str.contains(pattern, regex=True)]
            elif len(articles_values) == 0:
                raise PreventUpdate

            if len(importance_value) > 0:
                filtered_df = filtered_df[filtered_df['importance_number'].isin(importance_value)]
            elif len(importance_value) == 0:
                raise PreventUpdate

            if len(opinion_value) > 0:
                filtered_df = filtered_df[filtered_df['separate_opinion'].isin(opinion_value)]
            elif len(opinion_value) == 0:
                raise PreventUpdate

            if len(court_value) > 0:
                filtered_df = filtered_df[filtered_df['court'].isin(court_value)]
            elif len(court_value) == 0:
                raise PreventUpdate

            if len(year_value) > 0:
                years = list(range(year_value[0], (year_value[-1] + 1), 1))
                filtered_df = filtered_df[filtered_df['judgment_date'].isin(years)]
            elif len(year_value) == 0:
                raise PreventUpdate

        # Populating data for the time series and choropleth graphs
        df_time_series = filtered_df.copy()
        df_time_series['articles_considered'] = df_time_series['articles_considered'].str.split(',')
        df_time_series = df_time_series.explode('articles_considered').reset_index(drop=True)
        df_time_series = df_time_series.drop_duplicates(subset=['ecli', 'articles_considered'], keep='first')
        df_time_series = df_time_series[df_time_series.articles_considered.isin(articles_values) == True]
        df_time_series = df_time_series.groupby(['articles_considered', 'judgment_date']).size().reset_index(
        name='Count')
        df_choropleth = filtered_df.groupby(['code'], sort=False)['code'].count().reset_index(
        name='Number of Cases')

        # Obtain the number for Total Cases and Filtered Cases totals
        total_cases = f'Total judgments: {len(df_country_group.index)}'
        filtered_cases = f'Filtered judgments: {len(filtered_df.index)}'

        # Updating Importance Graph
        importance_graph = px.histogram(filtered_df, x="importance_number", color="importance_number",
                                        labels={"importance_number": "Importance Rating"})

        importance_graph.update_layout(transition_duration=500, margin=dict(t=20, b=40), height=300, width=710,
                                       yaxis_title="Number of Cases")

        importance_graph.update_traces(showlegend=False)

        # World Map
        world_map = px.choropleth_mapbox(df_choropleth, geojson=geojson, locations="code",
                                         color="code",
                                         color_continuous_scale=px.colors.sequential.Plasma,
                                         featureidkey="properties.ISO3",
                                         hover_name="Number of Cases",
                                         mapbox_style="open-street-map",
                                         zoom=1.5,
                                         center={"lat": 57.3785, "lon": 14.9706},
                                         opacity=0.5
                                         )

        world_map.update_layout(transition_duration=50, margin=dict(t=20, b=30), height=300, width=710)
        world_map.update_traces(showlegend=False)

        # Country Line Map
        article_line = px.line(df_time_series, x="judgment_date", y="Count", color='articles_considered',
                               labels={"articles_considered": "Articles Considered"})

        article_line.update_layout(transition_duration=50, margin=dict(t=0, b=70), height=400,
                                   xaxis_title='Judgment Date', yaxis_title="Number of Cases")

        # Data Table
        # Concatening two columns to create a hyperlinkable case column - 'case_link'
        filtered_df['case_link'] = '['+filtered_df['case_title']+']'+'('+filtered_df['document_url']+')'
        data = filtered_df.to_dict('rows')
        columns = [{"name": 'Case Name', "id": 'case_link', 'presentation': 'markdown'},
                   {"name": 'Importance', "id": 'importance_number'},
                   {"name": 'Articles Considered', "id": 'articles_considered'},
                   {"name": 'Respondent', "id": 'respondent'},
                   {"name": 'Date', "id": 'judgment_date'}]

        data_table = dash_table.DataTable(data=data, columns=columns,
                                          markdown_options={"link_target": "_blank"},
                                          sort_action="native",
                                          sort_mode="multi",
                                          export_format="csv",
                                          style_cell={'textAlign': 'left'})

        return importance_graph, world_map, article_line, total_cases, filtered_cases, data_table

    return dash_app.server
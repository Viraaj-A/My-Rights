from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import json
from plotly_dash.layout import html_layout


development = False

def init_dashboard(server):

    #Connecting with psycopg2/SQLAlchemy
    if development == True:
        connection_string = 'postgres:password@localhost/restore_Oct_13'
    else:
        connection_string = 'doadmin:AVNS_SbC_UqXYG665R47kxY4@db-postgresql-fra1-kyr-0001-do-user-12476250-0.b.db.ondigitalocean.com:25060/defaultdb'

    engine = create_engine(
        f'postgresql+psycopg2://{connection_string}',
        poolclass=NullPool)

    # Creating and cleaning dataframes for choropleth and importance rating
    df_english_raw = pd.read_sql('Select * from processed_english_case_detail', engine)
    df_french_raw = pd.read_sql('Select * from processed_french_case_detail', engine)
    df = pd.concat([df_french_raw, df_english_raw]).drop_duplicates(subset='ecli', keep="first")
    del df_french_raw, df_english_raw
    df_country_codes = pd.read_csv('data/map/country_iso_codes.csv')
    df_country_group = pd.merge(df, df_country_codes, on='respondent', how='inner')
    del df_country_codes
    df_choropleth = df_country_group.groupby(['code'], sort=False)['code'].count().reset_index(name='count')

    # Importing article_index table for the timeseries chart
    df_time_series = pd.read_sql('Select articles, judgment_date from article_index', engine)
    df_time_series['judgment_date'] = pd.to_datetime(df_time_series['judgment_date'], format='%Y-%m-%d')
    df_time_series['judgment_date'] = pd.DatetimeIndex(df_time_series['judgment_date']).year
    df_time_series = df_time_series.groupby(['articles','judgment_date']).size().reset_index(name='Count')


    #loading GeoJSON
    handle = open('data/map/europe.geojson')
    geojson = json.load(handle)


    #Dash App initilisation
    dash_app = Dash(server=server,
        routes_pathname_prefix="/visualisation/",)

    dash_app.index_string = html_layout


    map_fig = px.choropleth_mapbox(df_choropleth, geojson=geojson, locations="code",
                                   color="code",
                                   # hover_name="code", # column to add to hover information
                                   color_continuous_scale=px.colors.sequential.Plasma,
                                   featureidkey="properties.ISO3",
                                   hover_name = "count",
                                   mapbox_style="open-street-map",
                                   zoom=1.5,
                                   center={"lat":57.3785, "lon":14.9706},
                                   opacity=0.5)

    bar_fig = px.bar(df_time_series, y='Count', x='articles', color='articles')

    # Helper functions for dropdowns and slider
    def create_dropdown_options(series):
        options = [{'label': i, 'value': i} for i in series.sort_values().unique()]
        return options

    def create_dropdown_value(series):
        value = series.sort_values().unique().tolist()
        return value

    # App layout
    dash_app.layout = html.Div(className='container',
                          children=[
                              # First Row
                              html.Div(className='row',
                                       children=[
                                           # First Row First Column
                                           html.Div(className="col-xs-5",
                                                    children=[
                                                        html.Label("Total Graphs"),
                                                        dcc.Graph(),  # Total Graphs
                                                        html.Label("Human Rights/Articles"),
                                                        dcc.Dropdown(multi=True,
                                                                     options=create_dropdown_options(
                                                                         df_time_series['articles']
                                                                     ),
                                                                     value=create_dropdown_value(
                                                                         df_time_series['articles']
                                                                     )),
                                                        html.Label("Country"),
                                                        dcc.Dropdown(multi=True,
                                                                     options=create_dropdown_options(
                                                                         df_country_group['respondent']
                                                                     ),
                                                                     value=create_dropdown_value(
                                                                         df_country_group['respondent']
                                                                     )),
                                                        html.Label("Importance"),
                                                        dcc.Dropdown(multi=True,
                                                                     options=create_dropdown_options(
                                                                         df_country_group['importance_number']
                                                                     ),
                                                                     value=create_dropdown_value(
                                                                         df_country_group['importance_number']
                                                                     )),
                                                    ]
                                                    ),
                                           html.Div(className="col-xs-7",
                                                    children=[
                                                        dcc.Graph(id='importance-graph',
                                                                  config={'displayModeBar': False}),
                                                        html.Label("Separate Opinion Delivered"),
                                                        dcc.Dropdown(options=['Yes', 'No'],
                                                                         value=['Yes', 'No'],
                                                                     id='opinion-checklist',
                                                                     multi=True),
                                                        dcc.Graph(id='world_map', figure=map_fig,
                                                                  config={'displayModeBar': False}),
                                                        dcc.Graph(id='article_line', figure=bar_fig,
                                                                  config={'displayModeBar': False})
                                                    ])
                                       ])
                          ]
                          )


    @dash_app.callback(
        Output('importance-graph', 'figure'),
        Input('opinion-checklist', 'value')
    )
    def update_graph(opinion_value):
        df1 = df[df['separate_opinion'].isin(opinion_value)]

        fig = px.histogram(df1, x="importance_number", color="importance_number",
                           labels={"importance_number": "Importance Rating"})

        fig.update_layout(transition_duration=500)

        return fig

    return dash_app.server
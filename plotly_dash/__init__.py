from dash import Dash, html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
from plotly_dash.layout import html_layout
from plotly_dash.dash_data import discrete_data_df, time_series_df, exploded_df, choropleth_df, geojson_data

development = False

def init_dashboard(server):

    # ********************* DATA IMPORT *********************
    df_country_group = discrete_data_df()
    # choropleth_df = choropleth_df(df_country_group)
    time_series = time_series_df(df_country_group)
    geojson = geojson_data()

    # Helper functions for dropdowns and slider
    def create_dropdown_options(series):
        options = [{'label': i, 'value': i} for i in series.sort_values().unique()]
        return options

    def create_dropdown_value(series):
        value = series.sort_values().unique().tolist()
        return value

    # ********************* DASH APP *********************

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
                      html.Div(className="col-xs-5",
                               children=[
                                   html.Div([
                                       html.Label(
                                           "Choose countries that you are interested in"),
                                       dcc.Dropdown(
                                           options=create_dropdown_options(
                                               df_country_group[
                                                   'respondent']),
                                           value=["Germany", "Spain"],
                                           id='respondent_dropdown',
                                           multi=True)
                                   ]),
                                   html.Div([
                                       html.Label(
                                           "Select your human rights"),
                                       dcc.Dropdown(
                                           id="articles_dropdown",
                                           multi=True,
                                           options=create_dropdown_options(
                                               time_series[
                                                   'articles_considered']),
                                           value=["1", "2"]
                                           )
                                   ]),
                                   html.Div([
                                       html.Label(
                                           "Select the importance of the judgment you want to see"),
                                       dcc.Dropdown(
                                           id="importance_rating",
                                           multi=True,
                                           options=create_dropdown_options(
                                               df_country_group[
                                                   'importance_number']),
                                           value=create_dropdown_value(
                                               df_country_group[
                                                   'importance_number'])
                                           )
                                   ]),
                                   html.Div([
                                       html.Label(
                                           "Choose if you want to see if judges had different opinions"),
                                       dcc.Dropdown(
                                           id="separate_opinion",
                                           multi=True,
                                           options=create_dropdown_options(
                                               df_country_group[
                                                   'separate_opinion']),
                                           value=create_dropdown_value(
                                               df_country_group[
                                                   'separate_opinion'])
                                           )
                                   ]),
                                   html.Div([
                                       html.Label(
                                           "Choose the court you want"),
                                       dcc.Dropdown(id="court",
                                                    multi=True,
                                                    options=create_dropdown_options(
                                                        df_country_group[
                                                            'court']),
                                                    value=create_dropdown_value(
                                                        df_country_group[
                                                            'court'])
                                                    )
                                   ]),
                                   html.Div([
                                       html.Label(
                                           "Select the years for when judgments were made"),
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
                                       html.Button(
                                           id='submit-button-state',
                                           n_clicks=0,
                                           children='Submit')
                                   ])
                               ]
                               ),
                      # RIGT COLUMN OUTPUT GRAPHS
                      html.Div(className="col-xs-7",
                               children=[
                                   dcc.Graph(id='importance_graph',
                                             config={
                                                 'displayModeBar': False}),
                                   dcc.Graph(id='world_map', config={
                                       'displayModeBar': False}),
                                   dcc.Graph(id='article_line', config={
                                       'displayModeBar': False}),
                               ])
                  ])
     ]
     )


    @dash_app.callback(
        [
            Output('importance_graph', 'figure'),
            Output('world_map', 'figure'),
            Output('article_line', 'figure')
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
    def update_graph(respondent_value, importance_value, articles_values, opinion_value, court_value, year_value,
                     n_clicks):
        filtered_df = df_country_group.copy()
        df_time_series = time_series.copy()

        # Article values formed into a list to enable the isin functionality/checkbox functionality
        article_value = ('|'.join(articles_values))

        if n_clicks is not None:
            if len(respondent_value) > 0:
                filtered_df = filtered_df[filtered_df['respondent'].isin(respondent_value)]
                df_time_series = exploded_df(filtered_df)
            elif len(respondent_value) == 0:
                raise PreventUpdate

            if len(articles_values) > 0:
                filtered_df['articles_considered'] = filtered_df['articles_considered'].apply(', '.join)
                filtered_df = filtered_df[filtered_df['articles_considered'].str.contains(f'\b{article_value}\b')]
                df_time_series = df_time_series[
                    df_time_series['articles_considered'].str.contains(f'\b{article_value}\b')]
            elif len(articles_values) == 0:
                raise PreventUpdate

            if len(importance_value) > 0:
                filtered_df = filtered_df[filtered_df['importance_number'].isin(importance_value)]
                df_time_series = exploded_df(filtered_df)
            elif len(importance_value) == 0:
                raise PreventUpdate

            if len(opinion_value) > 0:
                filtered_df = filtered_df[filtered_df['separate_opinion'].isin(opinion_value)]
                df_time_series = exploded_df(filtered_df)
            elif len(opinion_value) == 0:
                raise PreventUpdate

            if len(court_value) > 0:
                filtered_df = filtered_df[filtered_df['court'].isin(court_value)]
                df_time_series = exploded_df(filtered_df)
            elif len(court_value) == 0:
                raise PreventUpdate

            if len(year_value) > 0:
                filtered_df = filtered_df[
                    filtered_df['judgment_date'].isin(list(range(year_value[0], year_value[1], 1)))]
                df_time_series = df_time_series[
                    df_time_series['judgment_date'].isin(list(range(year_value[0], year_value[1], 1)))]
            elif len(year_value) == 0:
                raise PreventUpdate

        # Updating Importance Graph
        importance_graph = px.histogram(filtered_df, x="importance_number", color="importance_number",
                                        labels={"importance_number": "Importance Rating", "color": 'Number of Cases'})

        importance_graph.update_layout(transition_duration=500)

        importance_graph.update_traces(showlegend=False)

        # World Map
        world_map = px.choropleth_mapbox(filtered_df, geojson=geojson, locations="code",
                                         color="code",
                                         # hover_name="code", # column to add to hover information
                                         color_continuous_scale=px.colors.sequential.Plasma,
                                         featureidkey="properties.ISO3",
                                         hover_name="articles_considered",
                                         mapbox_style="open-street-map",
                                         zoom=1.5,
                                         center={"lat": 57.3785, "lon": 14.9706},
                                         opacity=0.5
                                         )

        world_map.update_layout(transition_duration=500)
        world_map.update_traces(showlegend=False)

        # Country Line Map
        article_line = px.line(df_time_series, x="judgment_date", y="Count", color='articles_considered')

        return importance_graph, world_map, article_line

    return dash_app.server
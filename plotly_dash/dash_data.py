import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import json
import re


development = False


#Connecting with psycopg2/SQLAlchemy
if development == True:
    connection_string = 'postgres:password@localhost/restore_Oct_13'
else:
    connection_string = 'doadmin:AVNS_SbC_UqXYG665R47kxY4@db-postgresql-fra1-kyr-0001-do-user-12476250-0.b.db.ondigitalocean.com:25060/defaultdb'

engine = create_engine(
    f'postgresql+psycopg2://{connection_string}',
    poolclass=NullPool)

# ********************* DATA PREPARATION *********************

# Preparing dataframes for Choropleth and Importance Rating
def discrete_data_df():
    df_english_raw = pd.read_sql('Select * from processed_english_case_detail', engine, parse_dates=["judgment_date"])
    df_french_raw = pd.read_sql('Select * from processed_french_case_detail', engine, parse_dates=["judgment_date"])
    df = pd.concat([df_french_raw, df_english_raw]).drop_duplicates(subset='ecli', keep="first")
    del df_french_raw, df_english_raw
    df_country_codes = pd.read_csv('data/map/country_iso_codes.csv')
    df_country_group = pd.merge(df, df_country_codes, on='respondent', how='inner')
    del df
    df_country_group = df_country_group.drop(columns=['strasbourg', 'keywords', 'application_number', 'item_id', 'id'])
    df_country_group['judgment_date'] = df_country_group['judgment_date'].dt.year
    df_country_group['articles_considered'] = df_country_group['articles_considered'].str.replace(';', ',', regex=False)
    df_country_group['articles_considered'] = df_country_group.articles_considered.replace(regex=['-.'], value='')
    df_country_group['articles_considered'] = df_country_group.articles_considered.replace(regex=['more…'], value='')
    df_country_group['articles_considered'] = df_country_group.articles_considered.replace(r'[^a-zA-Z0-9]', ',', regex=True)
    del df_country_codes
    return df_country_group


# Creating Time Series Date
def time_series_df(dataframe):
    def create_article_list():
        articles = []
        for i in range(1, 57):
            articles.append(str(i))
        for j in range(1, 13):
            articles.append(f'P{j}')
        return articles
    article_list = create_article_list()
    df_index = dataframe
    df_index['articles_considered'] = df_index['articles_considered'].str.rstrip(',').str.split(',')
    df_index = df_index.explode('articles_considered').reset_index(drop=True)
    df_index = df_index.replace(r'^s*$', float('NaN'), regex=True)
    df_index.dropna(inplace=True)
    df_index = df_index.drop_duplicates(subset=['ecli', 'articles_considered'], keep='first')
    df_index = df_index[df_index.articles_considered.isin(article_list) == True]
    df_time_series = df_index.groupby(['articles_considered','judgment_date']).size().reset_index(name='Count')
    return df_time_series


def exploded_df(dataframe):
    def create_article_list():
        articles = []
        for i in range(1, 57):
            articles.append(str(i))
        for j in range(1, 13):
            articles.append(f'P{j}')
        return articles
    article_list = create_article_list()
    df_index = dataframe
    df_index = df_index.explode('articles_considered').reset_index(drop=True)
    df_index = df_index.replace(r'^s*$', float('NaN'), regex=True)
    df_index.dropna(inplace=True)
    df_index = df_index.drop_duplicates(subset=['ecli', 'articles_considered'], keep='first') #removes duplicates arising from subarticles
    df_index = df_index[df_index.articles_considered.isin(article_list) == True]
    df_time_series = df_index.groupby(['articles_considered','judgment_date']).size().reset_index(name='Count')
    del df_index
    return df_time_series


def choropleth_df(df_country_group):
    df_choropleth = df_country_group.groupby(['code'], sort=False)['code'].count().reset_index(name='Number of Cases')
    return df_choropleth


def geojson_data():
    #loading GeoJSON
    handle = open('data/map/europe.geojson')
    geojson = json.load(handle)
    return geojson

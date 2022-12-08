import pandas as pd

def return_results(procedural_q, physical_q, mental_q, age_q, gender_q, family_q, community_q,
                         nationality_q, property_q):
    rights = []
    article_groups = pd.read_csv("data/questionnaire_articles.csv")
    if procedural_q == 'Yes':
        rights.append(article_groups.loc[article_groups['Procedural'] == 'Yes', 'Right'].to_list())
    if physical_q == 'Yes':
        rights.append(article_groups.loc[article_groups['Physical'] == 'Yes', 'Right'].to_list())
    if mental_q == 'Yes':
        rights.append(article_groups.loc[article_groups['Mental'] == 'Yes', 'Right'].to_list())
    if age_q == 'Yes':
        rights.append(article_groups.loc[article_groups['Age'] == 'Yes', 'Right'].to_list())
    if gender_q == 'Yes':
        rights.append(article_groups.loc[article_groups['Gender'] == 'Yes', 'Right'].to_list())
    if family_q == 'Yes':
        rights.append(article_groups.loc[article_groups['Family affected'] == 'Yes', 'Right'].to_list())
    if community_q == 'Yes':
        rights.append(article_groups.loc[article_groups['Community Rights'] == 'Yes', 'Right'].to_list())
    if nationality_q == 'Yes':
        rights.append(article_groups.loc[article_groups['Nationality'] == 'Yes', 'Right'].to_list())
    if property_q == 'Yes':
        rights.append(article_groups.loc[article_groups['Property'] == 'Yes', 'Right'].to_list())
    flat_list = [item for sublist in rights for item in sublist]
    applicable_rights = set(flat_list)
    all_articles = article_groups.columns.values.tolist()
    remaining_rights = list(set(all_articles) - set(applicable_rights))
    applicable_rights = list(applicable_rights)

    return applicable_rights, remaining_rights






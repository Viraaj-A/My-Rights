from textblob import TextBlob

query = 'Torture and for Regina seal violence'

blob = TextBlob(query.lower())
corrected = blob.correct()
print(corrected)

from autocorrect import Speller
spell = Speller()
corrected = spell(query)

if corrected == query:
    print(True)
else:
    print(False)





# import spacy
# import contextualSpellCheck
#
# nlp = spacy.load('en_core_web_sm')
# contextualSpellCheck.add_to_pipe(nlp)
# doc = nlp(query)
#
# print(doc._.performed_spellCheck) #Should be True
# print(doc._.outcome_spellCheck)

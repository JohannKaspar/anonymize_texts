import spacy

# Load the de_core_news_md model
nlp = spacy.load('de_core_news_md')


def recognize_names(text):
    # Parse the text using the loaded model
    doc = nlp(text)  
  
    # Use the model to identify named entities in the text
    entities = [(e.text, e.label_) for e in doc.ents]
  
    # Filter the entities to only include those of type 'PER'
    names = [e[0] for e in entities if e[1] == 'PER']
  
    return names

# Test the function
text = "Herr Müller ist ein Patient im Krankenhaus. Er wurde von Dr. Schmidt behandelt, der ihm einige Tests verordnete."

print(recognize_names(text))
# Output: ['Müller', 'Dr. Schmidt']
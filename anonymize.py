import spacy
from spacy.matcher import PhraseMatcher

# Load the de_core_news_md model
nlp = spacy.load('de_core_news_lg')

def anonymize_names(text):
    # Parse the text using the loaded model
    doc = nlp(text)
  
    # Use the model to identify named entities in the text
    entities = [(e.text, e.label_) for e in doc.ents]
  
    # Filter the entities to only include those of type 'PER'
    names = [e[0] for e in entities if e[1] == 'PER']
  
    # TODO Use entity linking, so that spacy understands, that two mentions of a person
    # e.g. once with given name, once without, actuall refer to the same entity
    # maybee use Coreferee: https://github.com/msg-systems/coreferee#the-basic-idea

    # Create a new PhraseMatcher object from the spaCy vocabulary
    matcher = PhraseMatcher(nlp.vocab)

    # Initialize a dictionary to store the mapping of original names to anonymized names
    replacement_dict = {name.lower(): f"Person {i}" for i, name in enumerate(names)}

    # Create new patterns
    patterns = [nlp(name) for name in names]

    print(patterns)

    # Add a new pattern to the matcher object that will match the lowercase version of the name
    matcher.add("names", patterns)

    # Initialize an empty string to store the updated text after replacing the names
    anonymized_text = ''

    # Initialize a variable to keep track of the starting position of the buffer in the 'doc' object
    buffer_start = 0

    # Use the matcher object to find all instances of the names in the 'doc' object
    for match_id, match_start, match_end in matcher(doc):

        # If the start position of the match is greater than the current value of 'buffer_start', 
        if match_start > buffer_start:

            # add the tokens from 'buffer_start' to the start position of the match to the 'anonymized_text' string, along with any trailing whitespace from the previous token
            anonymized_text += doc[buffer_start: match_start].text + doc[match_start - 1].whitespace_
        
        # Replace the token with the anonymized name, with trailing whitespace if available
        anonymized_text += replacement_dict.get(doc[match_start:match_end].text.lower()) + doc[match_end - 1].whitespace_
        
        # Update the 'buffer_start' variable to the start position of the next token
        buffer_start = match_end
    
    # Add any remaining tokens from the end of the 'doc' object to the 'anonymized_text' string
    anonymized_text += doc[buffer_start:].text

    return anonymized_text

# Test the function
text = "Herr Anton Müller ist ein Patient im Krankenhaus. Herr Müller wurde von Dr. Schmidt behandelt, der dem Patienten einige Tests verordnete. Herr Müllers Leber ist gesund."

print(anonymize_names(text))
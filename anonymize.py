import argparse
import os

from flair.data import Sentence
from flair.models import SequenceTagger
from flair.tokenization import SegtokSentenceSplitter

def anonymize_names(filename_or_text):
    # if filename is provided, read text from file
    if os.path.exists(filename_or_text):
        with open(filename_or_text) as f:
            text = f.read()
    else:
        text = filename_or_text

    # load tagger
    tagger = SequenceTagger.load("flair/ner-german-large")

    # initialize sentence splitter
    splitter = SegtokSentenceSplitter()

    # use splitter to split text into list of sentences
    sentences = splitter.split(text)

    # predict tags for sentences
    tagger.predict(sentences)

    # make a list of all entities
    entities = []
    positions = {}
    for sentence in sentences:
        for entity in sentence.get_spans("ner"):
            if entity:
                if entity.get_label("ner").value == "PER":
                    if "David Schmitt" in entity.text:
                        print("stop")
                    positions[(entity.start_position + sentence.start_pos), (entity.end_position + sentence.start_pos)] = entity.text
                    entities.append(entity)
                    print(entity)
    positions = {k: v for k, v in sorted(positions.items(), key=lambda item: item[0][0])}

    # find most common name (this likely is the patients name)
    mentions = {}
    for entity in entities:
        name = entity.text
        if mentions.get(name):
            mentions[name] += 1
        else:
            mentions[name] = 1
    mentions = {k: v for k, v in sorted(mentions.items(), key=lambda item: item[1], reverse=True)}

    # make a dict of real name --> anonymized name
    name_dict = {}
    for i, name in enumerate(mentions.keys()):
        name_dict[name] = f"Person {i}"


    # from common mentions to uncommon: if name is substring in other name, they probably belong to the same person
    # in this case, the anonymized name should be the the anonymized name of the substring + the part outside the substring
    # e.g. "Müller" translates to "Meier", then "Müllers" should translate to "Meiers"
    processed = []
    for clear_name, anon_name in name_dict.items():
        for processed_name in processed:
            if processed_name in clear_name:
                name_dict[clear_name] = clear_name.replace(processed_name, name_dict.get(processed_name))
        processed.append(clear_name)

    # replace the names using entity.start_position and entity.end_position
    processed_text = ""
    cursor = 0
    # TODO Position zum einsetzen im jeweiligen Satz identifizieren
    # TODO Code untendrunter reevaluieren
    for (start_position, end_position), entity_text in positions.items():
        processed_text += text[cursor:start_position]
        processed_text += name_dict.get(entity_text)
        cursor = end_position

    processed_text += text[cursor:]

    return processed_text

if __name__ == "__main__":
    # create ArgumentParser object
    parser = argparse.ArgumentParser()

    # add arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--filename", help="filename to read text from")
    group.add_argument("-t", "--text", help="text to anonymize")

    # parse arguments
    args = parser.parse_args()

    # access arguments
    filename_or_text = args.filename or args.text
    print(anonymize_names(filename_or_text))
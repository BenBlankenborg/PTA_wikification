# Filename: wikification.py
# Date: 06-07-2022
# Authors: Katja Kamyshanova, Ben Blankenborg, Myrthe van der Veen
# This program contains a Wikification system.
# The program produces annotated data, including the entities:
# Country/State (COU), City/Town (CIT), Natural places (NAT), Person (PER),
# Organization (ORG), Animal (ANI), Sport (SPO), Entertainment (ENT)
# and their corresponding Wikipedia links.

# USAGE: $python3 wikification.py <dev/test directory> <direcotory_name>
# EXAMPLE USAGE: $python3 wikification.py dev d0554

from distutils.dep_util import newer_group
import os
import spacy
import nltk
import wikipedia
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet
import random
import sys


def read_file(current, head_folder, folder_name):

    """Takes in the current path name, head_folder name
    and the child folder name.
    Read the file en.tok.off.pos in this folder
    and returns list of data and a string of raw data.
    """
    found_it = False

    for elem in os.walk(current + "/" + head_folder + "/" + folder_name):
        for filename in elem[2]:
            os.chdir(elem[0])
            if filename == "en.tok.off.pos":
                found_it = True
                with open(filename, encoding="utf-8") as f1:
                    data_list = f1.readlines()
                raw_data = get_raw_file(elem[2])

    if not found_it:
        print("Error: working directory name is incorrect", file=sys.stderr)
        exit(-1)
    else:
        return data_list, raw_data


def run_wikification(data_list, raw_data):

    """Takes a list of data and a string of raw data,
    runs the whole wikification system with the separate fuctions.
    The function ends with running the output function
    (which write the file to en.tok.off.pos.ent).
    """

    pos_ent_data_list = []

    entities_list = ner(raw_data)
    ani_spo_ent_list = find_ner_bigrams(raw_data)
    if len(ani_spo_ent_list) != 0:
        # list contains (word, tag) tuples
        entities_list += ani_spo_ent_list
    gpe_list = tags_correction(entities_list)

    # list contains (word, tag, link) tuples
    ent_wiki_list = wikification(gpe_list)
    new_ent_list = split_ner(ent_wiki_list)

    for line in data_list:
        line_list = line.split()
        if len(line_list) == 5:
            for (word, label, link) in new_ent_list:
                ner_list = []
                if word == line_list[3]:
                    ner_list = line_list + [label] + [link]
                    pos_ent_data_list.append(ner_list)
                    break
            if not ner_list:
                # for words that are not recognised by spacy
                pos_ent_data_list.append(line_list + [" "])

    checked_pos_ent_data_list = check_current_list(pos_ent_data_list)
    output(checked_pos_ent_data_list)


def check_current_list(pos_ent_data_list):

    """Takes a list of already NER + wikification tagged data,
    finds NER tags and wiki links for entities that were not
    covered earlier and returns them in a list.
    """
    checked_pos_ent_data_list = []
    for line in pos_ent_data_list:
        checked_line = (check_non_name_tags(line))
        wiki_line = wikification_2(checked_line)
        checked_pos_ent_data_list.append(wiki_line)

    return checked_pos_ent_data_list


def output(checked_pos_ent_data_list):
    """Takes in a checked_pos_ent_data_list and write each list
    of this data list on a seperate line in an en.tok.off.pos.ent file.
    """

    current = os.getcwd()
    if not os.path.exists(current + "/temp"):
        os.mkdir("temp")
    os.chdir(current + "/temp")

    with open('en.tok.off.pos.ent', 'w') as out_file:
        sys.stdout = out_file
        for i in checked_pos_ent_data_list:
            print(' '.join(i))


def tags_correction(entities_list):

    """Takes a list of tuples, goes through each tuples and
    corrects specific tags values, then returns a list with
    changed tuples.
    """

    new_ent_list = []
    for ent in entities_list:
        if ent[1] == "GPE":
            try:
                wiki_sent = wikipedia.summary(ent[0], sentences=1).lower()
                wiki_sent_list = nltk.word_tokenize(wiki_sent)
                if "city" in wiki_sent_list or "town" in wiki_sent_list:
                    new_ent_list.append((ent[0], "CIT"))
                elif "country" in wiki_sent_list or "state" in wiki_sent_list:
                    new_ent_list.append((ent[0], "COU"))
                else:
                    new_ent_list.append((ent[0],
                                         random.choice(["CIT", "COU"])))
            except (wikipedia.exceptions.PageError,
                    wikipedia.exceptions.DisambiguationError):
                new_ent_list.append((ent[0], random.choice(["CIT", "COU"])))
        elif ent[1] == "LOC":
            new_ent_list.append((ent[0], "NAT"))
        elif ent[1] == "WORK_OF_ART":
            new_ent_list.append((ent[0], "ENT"))
        elif ent[1] == "PERSON":
            new_ent_list.append((ent[0], "PER"))
        else:
            new_ent_list.append(ent)

    return new_ent_list


def wikification(entities_list):

    """Takes a list of tuples, goes through each tuple,
    finds a wikipedia link for each term in a tuple,
    then adds the link into a new tuple and returns
    all tuples in a list.
    """
    wiki_list = []

    for (word, label) in entities_list:
        for term in wikipedia.search(word, results=1):
            if term != "":
                try:
                    wiki_list.append((word, label, wikipedia.page(term).url))
                except (wikipedia.exceptions.PageError,
                        wikipedia.exceptions.DisambiguationError):
                    if term == "New York City":
                        wiki_list.append((word, label,
                                         "https://en.wikipedia.org"
                                          "/wiki/New_York_City"))
                    else:
                        # TODO: use word ipv term?
                        term_ = "_".join(nltk.word_tokenize(term))
                        wiki_list.append((word, label,
                                         "https://en.wikipedia.org/wiki/" +
                                          term_))

    return wiki_list


def wikification_2(line):

    """This function takes a list and adds a wikipedia
    link if the list contains one of the NER tags.
    """
    if len(line) > 4:
        if line[5] == "ANI" or line[5] == "SPO":
            for term in wikipedia.search(line[3], results=1):
                if term != "":
                    line.append("https://en.wikipedia.org/wiki/" + str(term))
    return line


def check_non_name_tags(line):

    """This function takes input of a word and its information
    as formatted previously, and assigns it an ANI or SPO
    tag if the word is an animal or sport.
    """
    lemmatizer = WordNetLemmatizer()

    word = lemmatizer.lemmatize(line[3])
    w_syns = wordnet.synsets(word)
    if len(w_syns) > 0 and line[5] == " ":
        if hypernymOf(w_syns[0], wordnet.synsets('animal')[0]):
            line[5] = 'ANI'
        if hypernymOf(w_syns[0], wordnet.synsets('sport')[0]):
            line[5] = 'SPO'

    return line


def find_ner_bigrams(raw_text):

    """Takes a string of text, slides it into bigrams,
    searches for specific entities by looking at the
    hypernyms of each bigram and returns a list of all
    found bigrams and their entity tags.
    """

    lemmatizer = WordNetLemmatizer()

    bigrams_ner_list = []
    tokens = nltk.word_tokenize(raw_text)
    bigrams_list = list(nltk.bigrams(tokens))
    for bigram in bigrams_list:
        bigram_str = ' '.join(bigram)
        lemma = lemmatizer.lemmatize(bigram_str)
        lemma_list = lemma.split()
        bigram_synset = wordnet.synsets(lemma_list[0] + "_" + lemma_list[1])
        if len(bigram_synset) > 0:
            if hypernymOf(bigram_synset[0], wordnet.synsets('animal')[0]):
                bigrams_ner_list.append((bigram_str, 'ANI'))
            if hypernymOf(bigram_synset[0], wordnet.synsets('sport')[0]):
                bigrams_ner_list.append((bigram_str, 'SPO'))

    return bigrams_ner_list


def get_raw_file(file_list):

    """Opens a raw file in the same directory
    as used .pos file and returns the data as a string.
    """

    for filename in file_list:
        if filename == "en.raw":
            with open(filename, encoding="utf-8") as f:
                return f.read()


def hypernymOf(synset1, synset2):

    """Returns True if synset2 is a hypernym of
    synset1, or if they are the same synset.
    Returns False otherwise.
    """

    if synset1 == synset2:
        return True
    for hypernym in synset1.hypernyms():
        if synset2 == hypernym:
            return True
        if hypernymOf(hypernym, synset2):
            return True
    return False


def ner(raw_text):

    """Takes a str of raw text and by using SpaCy returns a list
    of tuples with words and given to them entity tags.
    """
    ner_spacy = spacy.load("en_core_web_sm")

    tags_list = ["PERSON", "GPE", "LOC", "ORG", "WORK_OF_ART"]
    text = ner_spacy(raw_text)
    entities_list = [(word.text, word.label_) for word in text.ents
                     if word.label_ in tags_list]

    return entities_list


def split_ner(entities_list):

    """Takes a list of tuples, goes through each tuple
    and if there are more than 1 word in a tuple tokenizes it
    and returns a list separated tuples with related entity tags.
    """

    new_ent_list = []
    for (word_phrase, label, link) in entities_list:
        if " " in word_phrase:
            word_list = nltk.word_tokenize(word_phrase)
            for word in word_list:
                if (word != "the" and word != "'s" and
                   word != "The" and word != "of"):
                    new_ent_list.append((word, label, link))
        else:
            new_ent_list.append((word_phrase, label, link))

    return new_ent_list


def main(argv):

    if len(argv) != 3:
        print("Error: incorrect amount of arguments", file=sys.stderr)
        exit(-1)

    if argv[1] != "dev" and argv[1] != "test":
        print("Error: head folder name is incorrect, "
              "please use 'dev' or 'test' as second console argument",
              file=sys.stderr)
        exit(-1)

    head_folder = argv[1]
    folder_name = argv[2]
    current = os.getcwd()
    data_list, raw_data = read_file(current, head_folder, folder_name)
    run_wikification(data_list, raw_data)


if __name__ == "__main__":
    main(sys.argv)

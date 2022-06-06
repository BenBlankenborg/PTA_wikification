# This program was made to test the working code on a single dir (d0208)

import os 
import spacy
import nltk
import wikipedia
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet
import random
lemmatizer = WordNetLemmatizer()

NER = spacy.load("en_core_web_sm")

def read_file(current):
    for ent in os.walk(current+ "/dev"):
        for elem in os.walk(ent[0]):
            for filename in elem[2]:

                pos_ent_data_list = []

                os.chdir(elem[0])
                if filename == "en.tok.off.pos":
                    with open(filename, encoding="utf-8") as f1:
                        data_list = f1.readlines()

                    raw_data = get_raw_file(elem[2])
                    entities_list = ner(raw_data)
                    ani_spo_ent_list = find_ner_bigrams(raw_data)
                    if len(ani_spo_ent_list) != 0:
                        entities_list += ani_spo_ent_list # list contains (word, tag) tuples
                    gpe_list = tags_correction(entities_list)

                    ent_wiki_list = wikification(gpe_list) # list contains (word, tag, link) tuples
                    # THIS BITCH EMPTY YEET
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
                                pos_ent_data_list.append(line_list + ["none"])
                        else:
                            # for lines that don't contain word and pos tag
                            pos_ent_data_list.append(line_list + ["bbb"])


                    checked_pos_ent_data_list = []  
                    for line in pos_ent_data_list:
                        checked_line = (check_non_name_tags(line))
                        wiki_line = wikification_2(checked_line)
                        checked_pos_ent_data_list.append(wiki_line)
                
                    for i in checked_pos_ent_data_list:
                        print(i)


def tags_correction(entities_list):
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
                    new_ent_list.append((ent[0], random.choice(["CIT", "COU"])))
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

    # TODO: for words that have no wikipedia page wiki suggests wrong stuff
    # Carolyn Weaver has no page => wiki suggests and prints Carolyn Jones
    wiki_list = []

    for (word, label) in entities_list:
        for term in wikipedia.search(word, results=1):
            if term != "":
                try:
                    wiki_list.append((word, label, wikipedia.page(term).url))
                except (wikipedia.exceptions.PageError,
                        wikipedia.exceptions.DisambiguationError):
                    # TODO: probably change to a more general exception
                    if term == "New York City":
                        wiki_list.append((word, label, "https://en.wikipedia.org/wiki/New_York_City"))
                    else:
                        # TODO: use word ipv term?
                        term_ = "_".join(nltk.word_tokenize(term))
                        wiki_list.append((word, label, "https://en.wikipedia.org/wiki/" + term_))
        
    return wiki_list


def wikification_2(line):

    """This function takes a list and adds a wikipedia
    link if the list contains one of the NER tags"""

    if line[5] == "ANI" or line[5] == "SPO":
        for term in wikipedia.search(line[3], results=1):
             if term != "":
                 line.append("https://en.wikipedia.org/wiki/" + str(term))
    return line


def check_non_name_tags(line):

    """This function takes input of a word and its information
    as formatted previously, and assigns it an ANI or SPO 
    tag if the word is an animal or sport."""
    word = lemmatizer.lemmatize(line[3])
    w_syns = wordnet.synsets(word)
    if len(w_syns) > 0 and line[5] == 'none':
        if hypernymOf(w_syns[0], wordnet.synsets('animal')[0]):
            line[5] = 'ANI'
        if hypernymOf(w_syns[0], wordnet.synsets('sport')[0]):
            line[5] = 'SPO'
    
    return line


def find_ner_bigrams(raw_text):

    # we do this to find tags that were not automatically given by spacy
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

    '''opens a raw file in the same directory
    and returns the text as a string'''

    for filename in file_list:
        if filename == "en.raw":
            with open(filename, encoding="utf-8") as f:
                return f.read()
                

def hypernymOf(synset1, synset2):
    """ Returns True if synset2 is a hypernym of
    synset1, or if they are the same synset.
    Returns False otherwise. """
    if synset1 == synset2:
         return True
    for hypernym in synset1.hypernyms():
         if synset2 == hypernym:
             return True
         if hypernymOf(hypernym, synset2):
            return True
    return False


def ner(raw_text):

    '''takes a str of raw text and by using SpaCy returns a list
    of tuples with words and given to them tags'''

    tags_list = ["PERSON", "GPE", "LOC", "ORG", "WORK_OF_ART"]
    text = NER(raw_text)
    entities_list = [(word.text, word.label_) for word in text.ents
                     if word.label_ in tags_list]
    
    return entities_list

def split_ner(entities_list):

    '''takes a list of tuples, goes through each tuple
    and if there are more than 1 word in a tuple tokenizes it
    and returns a list separated tuples with related tags'''

    new_ent_list = []
    for (word_phrase, label, link) in entities_list:
        if " " in word_phrase:
            word_list = nltk.word_tokenize(word_phrase)
            for word in word_list:
                if word != "the" and word != "The" and word != "'s" and word != "of" and word != "and": 
                    new_ent_list.append((word, label, link))
        else:
            new_ent_list.append((word_phrase, label, link))
    
    return new_ent_list


def main(): 
    current = os.getcwd()
    read_file(current)

       
   
if __name__ == "__main__": 
    main()

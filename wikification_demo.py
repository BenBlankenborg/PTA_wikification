# This program was made to test the working code on a single dir (d0021)

import os 
import spacy

NER = spacy.load("en_core_web_sm")

def read_file(current):
    for elem in os.walk(current + "/dev/d0021"):
        for filename in elem[2]:

            pos_ent_data_list = []

            os.chdir(elem[0])
            if filename == "en.tok.off.pos":
                with open(filename, encoding="utf-8") as f1:
                    data_list = f1.readlines()

                raw_data = get_raw_file(elem[2])
                entities_list = ner(raw_data)
                new_ent_list = split_ner(entities_list)

                for line in data_list:
                    line_list = line.split()
                    if len(line_list) == 5:
                        for (word, label) in new_ent_list:
                            ner_list = []
                            if word == line_list[3]:
                                ner_list = line_list + [label]
                                pos_ent_data_list.append(ner_list)
                                break
                        if not ner_list:
                            # for words that are not recognised by spacy
                            pos_ent_data_list.append(line_list + ["none"])
                    else:
                        # for lines that don't contain word and pos tag
                        pos_ent_data_list.append(line_list + ["bbb"])
                    
                for i in pos_ent_data_list:
                    print(i)


def get_raw_file(file_list):

    '''opens a raw file in the same directory
    and returns the text as a string'''

    for filename in file_list:
        if filename == "en.raw":
            with open(filename, encoding="utf-8") as f:
                return f.read()


def ner(raw_text):

    '''takes a str of raw text and by using SpaCy returns a list
    of tuples of group of words and tagged named entities'''

    text = NER(raw_text)
    entities_list = [(word.text, word.label_) for word in text.ents]
    
    return entities_list

def split_ner(entities_list):

    '''takes a list of tuples, goes through each tuple
    and if there are more than 1 word in a tuple splits them
    into different tuples with the same tags, returns a list
    of new tuples'''

    # TODO: add REGEX for special cases of word phrases ( i.e. "word's", "yo-yo")

    new_ent_list = []
    for (word_phrase, label) in entities_list:
        if " " in word_phrase:
            word_list = word_phrase.split()
            for word in word_list:
                new_ent_list.append((word, label))
        else:
            new_ent_list.append((word_phrase,label))
    
    return new_ent_list


def main(): 
    current = os.getcwd()
    read_file(current)

   
if __name__ == "__main__": 
    main()
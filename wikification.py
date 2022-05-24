#
#
#
#

import os 
import spacy
from spacy import displacy



def read_file(current):
    for ent in os.walk(current + "/dev"):
            # looping in a dir by choosing the right path
            for g in os.walk(ent[0]):
                # looping only through the files
                for fi in g[2]:
                     if fi == 'en.tok.off.pos':
                        os.chdir(g[0])
                        with open(fi, encoding="utf-8") as f:
                            t = [line.split() for line in f.readlines()]
                            raw_text = [item[3] for item in t if len(item) > 3 ]
                            raw_text = ' '.join(raw_text)
                            Named_Entity_Recognition(raw_text)


def Named_Entity_Recognition(raw_text):
    NER = spacy.load("en_core_web_sm")
    text= NER(raw_text)
    for word in text.ents:
        print(word.text,word.label_)

def main(): 
    current = os.getcwd()
    read_file(current)

   
if __name__ == "__main__": 
    main()

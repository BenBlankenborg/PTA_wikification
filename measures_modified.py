# Filename: measures_modified.py
# Authors: Katja Kamyshanova, Ben Blankenborg, Ben Blankenborg
# The code was adapted from the the template given by Tim Kreutz 
# Date: 23-05-2022
# This program uses NLTK module to compare annotated data located in 3 different
# directories


from collections import Counter
from nltk.metrics import ConfusionMatrix
import os
import sys

def get_data(words_list):

    '''Takes a list of lines and adds a NS tag
    if no annotations info was given'''

    entities_list = []
    for word in words_list:
        word = word.split()
        if len(word) < 6:
            # for non-interesting entities
            word.append('Non interest')
        if len(word) < 7:
            word.append('No link')
        entities_list.append(word)

    return entities_list
    
def re_classify(wl):

    '''takes a list of annotated tags and returns another
    list of tags that are interesing and not interesting
    for the analysis'''

    new_list = []
    for word in wl:
        if word != 'NS':
            new_list.append('I')
        else:
            new_list.append(word)
    return new_list
        
    
        
def read_files(current, head_folder, folder_name):

    """
    Takes in the current path name, head_folder name and the child folder name.
    Read the file en.tok.off.pos in this folder
    and returns list of data
    """
    found_it = False

    path = current + "/" + head_folder + "/" + folder_name
    for elem in os.walk(path):
        for filename in elem[2]:
            os.chdir(elem[0])
            if filename == "en.tok.off.pos":
                found_it = True
                with open(filename, encoding="utf-8") as f1:
                    data_list1 = get_data(f1.readlines())

    for el in os.walk(path + "/temp"):
         for fname in el[2]:
              os.chdir(elem[0])
              if fname == "en.tok.off.pos.ent":
                  with open(fname, encoding="utf-8") as f2:
                      data_list2 = get_data(f2.readlines())
              else:
                  print("Error: no file found. Have you run the wikification code yet?", file=sys.stderr)
                  exit(-1)

    if found_it == False:
        print("Error: working directory name is incorrect", file=sys.stderr)
        exit(-1)
    else:
        return data_list1, data_list2


def confusion_matrix(ref, tagged):
    '''returns a confusion metrix of 2 lists of tagged entities'''
    cm = ConfusionMatrix(ref, tagged)
    return cm

def evaluation_measures(labels, cm):

    '''takes a list of annotated entities tags and returns a list
    of 3 floats for each of the evaluation measures'''

    true_positives = Counter()
    false_negatives = Counter()
    false_positives = Counter()

    for i in labels:
        for j in labels:
            if i == j:
                true_positives[i] += cm[i, j]
            else:
                false_negatives[i] += cm[i, j]
                false_positives[j] += cm[i, j]

    
    return [true_positives, false_negatives, false_positives]
    

def f_score(labels, true_positives, false_negatives, false_positives):

    '''takes a list of annotated entities tags and evaluation measures
    and prints precision- , recall- and f-scores for each entity'''
    for i in sorted(labels):
        
        if true_positives[i] == 0:
            fscore = 0
        else:
            precision = true_positives[i] / float(true_positives[i] +
                                              false_positives[i])
            recall = true_positives[i] / float(true_positives[i] +
                                           false_negatives[i])
            fscore = 2 * (precision * recall) / float(precision + recall)
            print("The precision score of", i, "is", precision)
            print("The recall score of", i, "is", recall)
            print("The fscore of", i, "is", fscore)


def main(): 

    if len(sys.argv) != 3:
        print("Error: incorrect amount of arguments", file=sys.stderr)
        exit(-1)

    if sys.argv[1] != "dev" and sys.argv[1] != "test":
        print("Error: head folder name is incorrect, "
              "please use 'dev' or 'test' as second console argument",
              file=sys.stderr)
        exit(-1)

    head_folder = sys.argv[1]
    folder_name = sys.argv[2]
    current = os.getcwd()
    data_list1, data_list2 = read_files(current, head_folder, folder_name)
    #con_met = confusion_matrix(data_list1, data_list2)
    #print("The confusion matrix for all entities:\n", con_met)


    #in_con_met = confusion_matrix(re_classify(new_list[0]), re_classify(new_list[1]))
    #print(f"The confusion matrix for the interesting entities"
          #f"and non-interesting entities:\n", in_con_met)

    #entities = set('COU CIT NAT PER ORG ENT NS'.split())

    #entities_in = set('NS I'.split())
    #true_pos, false_neg, false_pos = evaluation_measures(entities, con_met)
    #print("\nPrecision, recall and f-score for all entities:")

    #f_score(entities, true_pos, false_neg, false_pos)
    #true_pos_in, false_neg_in, false_pos_in = evaluation_measures(entities_in, in_con_met)
    #print(f"\nPrecision, recall and f-score for interesting"
     #     f"(I) vs non-interesting entities (NS):")
    #f_score(entities_in, true_pos_in, false_neg_in, false_pos_in)
    

if __name__ == '__main__':
    main()

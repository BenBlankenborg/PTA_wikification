# Filename: measures.py
# Authors: Katja Kamyshanova, Ben Blankenborg, Myrthe van der Veen
# The code was adapted from a template given by Tim Kreutz
# Date: 23-05-2022
# This program uses NLTK module to compare annotated data located
# in 3 different directories


from collections import Counter
from nltk.metrics import ConfusionMatrix
import os


def get_data(words_list):

    '''Takes a list of lines and adds a NS tag
    if no annotations info was given'''

    entities_list = []
    for word in words_list:
        word_list = word.split()
        if len(word_list) >= 6:
            # for interesting entities
            entities_list.append(word_list[5])
        else:
            # for non-interesting entities
            entities_list.append("NS")

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


def open_dir():

    '''loops through 3 directories of annotated data and returns a list
    of entities tags taken from annotated files'''

    cur_path = os.getcwd()
    path_1 = cur_path + "/test"

    entities_gs = []
    entities_us = []

    entities_list = [entities_gs, entities_us]

    # looping through the paths of dirs, dirs and files in group5 dir
    for ent in os.walk(path_1):
        for dir_name in ent[1]:

            # looping in a dir by choosing the right path
            for g in os.walk(path_1 + "/" + dir_name):
                # looping only through the files
                for file in g[2]:
                    if file == "en.tok.off.pos.ent":
                        os.chdir(path_1 + "/" + dir_name)
                        with open(file, encoding="utf-8") as f:
                            entities_list[0].append(get_data(f.readlines()))
                        os.chdir(path_1 + "/" + dir_name + "/temp")
                        with open(file, encoding="utf-8") as f:
                            entities_list[1].append(get_data(f.readlines()))
                    break
            '''
            for file in g[2]:
                print(file)
                if file == "en.tok.off.pos.ent":
                    os.chdir(g[0])
                    print(g[0])
                    counter = 0
                    with open(file, encoding="utf-8") as f:
                        entities_list[0].append(get_data(f.readlines()))
                    print("a")
                    with open(file, encoding="utf-8") as f:
                        entities_list[1].append(get_data(f.readlines()))
                    break'''

    return entities_list


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
    ent_list = open_dir()
    new_list = [[], [], []]
    counter = 0
    for i in ent_list:
        for file in i:
            for ent in file:
                new_list[counter].append(ent)
        counter += 1

    con_met = confusion_matrix(new_list[0], new_list[1])
    print("The confusion matrix for all entities:\n", con_met)

    in_con_met = confusion_matrix(re_classify(new_list[0]),
                                  re_classify(new_list[1]))
    print(f"The confusion matrix for the interesting entities"
          f"and non-interesting entities:\n", in_con_met)

    entities = set('COU CIT NAT PER ORG ENT NS'.split())

    entities_in = set('NS I'.split())
    true_pos, false_neg, false_pos = evaluation_measures(entities, con_met)
    print("\nPrecision, recall and f-score for all entities:")

    f_score(entities, true_pos, false_neg, false_pos)
    true_pos_in, false_neg_in, false_pos_in = evaluation_measures(entities_in, in_con_met)
    print(f"\nPrecision, recall and f-score for interesting"
          f"(I) vs non-interesting entities (NS):")
    f_score(entities_in, true_pos_in, false_neg_in, false_pos_in)


if __name__ == '__main__':
    main()

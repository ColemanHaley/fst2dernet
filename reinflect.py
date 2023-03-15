# given a form and an analysis, generate all other inflectional forms
# for the same lemma

# does not work yet, yupik inflections are complicated.

import argparse
import re

SEP = '^'
# example basic regex

def strip_inflect(analysis):
    """Strip the inflectional features from an analysis"""
    return analysis.split('+')[0]

def paradigm(pos):


def get_pos(analysis):
    """Get the part of speech of a form"""
    # should be POS for last postbase
    # remove items that are in square brackets from the list
    # regex with groups for inflections, derivations, and clitics SLI Yupik

    # remove inflections and enclitics
    ders = [m for m in analysis.split(SEP) if m[0] != '[' and m[0] != '=']

    pos = re.findders[-1]

def paradigmize():
    """Given a form and an analysis, generate all other inflectional forms
    for the same lemma"""
    for 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('form', help='form to reinflect')
    parser.add_argument('analysis', help='analysis of the form')
    args = parser.parse_args()


    


if __name__ == '__main__':
    main()

noun_infl = ['[Abs.Sg]']
intrans_infl = ['[Ind.Intr]','[3Sg]']
trans_infl = ['[Ind.Trns]', '[3Sg.3Sg]']

import hfst
import re
import argparse

SEP = '^'
def generate(analysis):

def get_pos(affix):
    m = re.match(fr'([^{SEP}]+)(\([^\)]+\))', affix) # get POS group
    pos = m.group(2).strip('()')
    if '→' in pos:
        start, end = pos.split('→')
        pos = end
    return pos

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('form', help='form to underive')
    parser.add_argument('analysis', help='analysis of the form')
    args = parser.parse_args()
    print(args.form)

    analysis = args.analysis.split(SEP)
    # remove enclitics
    while analysis[-1][0] == '=':
        analysis = analysis[:-1]
        print(generate(SEP.join(analysis)))

    # find transitivity
    infls = SEP.join([m for m in analysis if m[0] == '['])
    transitive = 'Trns' in infls
    
    # remove inflections
    analysis = [m for m in analysis if m[0] != '[']
    while len(analysis) > 0:
        analysis = analysis[:-1]
        pos = get_pos(analysis[-1])
        if pos not in ['N', 'V']:
            print("Can't underive this form!")
            break
        if pos == 'N':
            print(generate(SEP.join(analysis+noun_infl)))
        elif transitive:
            print(generate(SEP.join(analysis+trans_infl)))
        else:
            print(generate(SEP.join(analysis+intrans_infl)))





if __name__ == '__main__':
    main()

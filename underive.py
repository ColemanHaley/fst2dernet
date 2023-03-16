noun_infl = ["[Abs.Sg]"]
intrans_infl = ["[Ind.Intr]", "[3Sg]"]
trans_infl = ["[Ind.Trns]", "[3Sg.3Sg]"]

from foma import FST
import sys
import re
from typing import Iterable
from dataclasses import dataclass, field
import argparse

SEP = "^"
fst = FST.load("fsts/ess-2.8/l2s.fomabin")


class FomaError(Exception):
    pass


def generate(analysis):
    try:
        return next(fst.apply_down(analysis))
    except StopIteration:
        raise FomaError(f"Could not generate form for {analysis}")


def normalizepos(pos):
    if pos in ["V", "CmpdVbl", "PTCL", "EMO"]:
        return "V"
    elif pos in ["N", "NUM", "WH", "AREA"]:
        return "N"
    else:
        return pos


def get_pos(affix):
    if affix == "ete":
        return "V"
    m = re.match(rf"([^{SEP}]+)(\([^\)]+\))", affix)  # get POS group
    pos = m.group(2).strip("()")
    if "→" in pos:
        start, end = pos.split("→")
        pos = end
    return normalizepos(pos)


def standardize(analysis):
    analysis = analysis.split(SEP)
    infls = SEP.join([m for m in analysis if m[0] == "["])
    transitive = "Trns" in infls

    analysis = [m for m in analysis if m[0] != "["]
    pos = get_pos(analysis[-1])
    if pos not in ["N", "V"]:
        infl = []  # should this be an error?
    elif pos == "N":
        infl = noun_infl
    elif transitive:
        infl = trans_infl
    else:
        infl = intrans_infl
    return SEP.join(analysis + infl), pos


def get_infl(analysis):
    return SEP.join([m for m in analysis.split("^") if m[0] == "["])


def underive(analysis):
    # parser = argparse.ArgumentParser()
    # parser.add_argument('form', help='form to underive')
    # parser.add_argument('analysis', help='analysis of the form')
    #
    # args = parser.parse_args()
    analysis = analysis.split("=")  # remove enclitics
    # print(analysis)
    entry = None
    while len(analysis) > 1:
        standard, pos = standardize(analysis[0])
        under = "=".join([standard] + analysis[1:])
        entry = [
            Entry(
                generate(under),
                under,
                get_infl(standard),
                pos,
                "=" + analysis[-1],
                entry,
            )
        ]
        analysis = analysis[:-1]
    analysis = analysis[0]

    # remove inflections
    analysis = analysis.split(SEP)

    analysis = [m for m in analysis if m[0] != "["]
    while len(analysis) > 1:
        standard, pos = standardize(SEP.join(analysis))
        entry = [
            Entry(
                generate(standard),
                standard,
                get_infl(standard),
                pos,
                analysis[-1],
                entry,
            )
        ]
        analysis = analysis[:-1]

    standard, pos = standardize(SEP.join(analysis))
    entry = Entry(generate(standard), standard, get_infl(standard), pos, "", entry)
    return entry


@dataclass
class Entry:
    """Entry in a derivational network"""

    surface: str
    underlying: str
    infl: str
    pos: str
    relation: str
    children: Iterable[str] = field(default_factory=list)

    def __eq__(self, other):
        return self.surface == other.surface and self.underlying == other.underlying


class DerNet:
    """Derivational network in Universal Derivations format"""

    def __init__(self):
        self.families = {}
        self.items = {}

    def add_derivation(self, entry):
        attach_point = None
        while entry.underlying in self.items:
            attach_point = entry.underlying
            if entry.children is None:  # the whole path is in the network
                return
            entry = entry.children[0]
        if attach_point is not None:
            self.items[attach_point].children.append(entry)
        else:
            self.families[entry.underlying] = entry
        while entry is not None and entry.children is not None:
            self.items[entry.underlying] = entry
            entry = entry.children[0]

    def __make_entry(self, node, parent_i, i):
        return (
            "\t".join(
                [
                    i,
                    "#".join([node.surface, node.pos]),
                    node.surface,
                    node.pos,
                    node.infl,
                    "",
                    parent_i,
                    node.relation,
                    "",
                    "{}",
                ]
            )
            + "\n"
        )

    def point(self, i, j):
        if j == 0:
            return str(i)
        else:
            return str(i) + "." + str(j)

    def __str__(self):
        result = ""
        for i, root in enumerate(self.families.values()):
            i += 1
            i = str(i)
            j = 0
            stack = [(root, "", i)]
            while len(stack) > 0:
                node, parent, idx = stack.pop(0)
                result += self.__make_entry(node, parent, idx)
                if node.children is None:
                    continue
                parent_i = self.point(i, j)
                for child in node.children:
                    j += 1
                    if child is not None:
                        stack.append((child, parent_i, self.point(i, j)))

            result += "\n"
        return result


def construct_der_net(words):
    net = DerNet()
    with open("analyses/ess.tsv") as f:
        for line in f:
            analysis, _ = line.split("\t")
            try:
                derivation = underive(analysis)
                net.add_derivation(derivation)
            except FomaError as e:
                print("No derivation found for", analysis, file=sys.stderr)
                print(e, file=sys.stderr)
    print(net)


if __name__ == "__main__":
    construct_der_net(["sa(N)^~:(ng)u(N→V)^[Intrg.Intr]^[3Sg]=lli"])

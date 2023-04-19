noun_infl = ["[Abs.Sg]"]
intrans_infl = ["[Ind.Intr]", "[3Sg]"]
trans_infl = ["[Ind.Trns]", "[3Sg.3Sg]"]

# from foma import FST
import hfst

# abstract base class
from abc import ABC, abstractmethod
import sys
import re
from typing import Iterable
from dataclasses import dataclass, field
import argparse


def remove_epsilons(string, epsilon="@_EPSILON_SYMBOL_@"):
    """Removes the epsilon transitions from the string along a path from hfst.
    Args:
        string (str): The string (e.g. input path, output form) from which the epsilons should be deleted.
        epsilon (str, optional):  The epsilon string to remove. Defaults to the default setting in hfst,
        '@_EPSILON_SYMBOL_@'. Pass this only if you've redefined the epsilon symbol string in hfst.
    Returns:
        str: The desired string, without epsilons
    """
    # remove strings surrounded by @
    return re.sub(r"@.*?@", "", string)


class GenerationError(Exception):
    pass


class Analysis:
    def __init__(self, analysis, sep):
        if isinstance(analysis, str):
            self.analysis = analysis.split(sep)
        else:
            self.analysis = list(analysis)
        self.SEP = sep

    def __str__(self):
        return self.SEP.join(self.analysis)

    def __iter__(self):
        return iter(self.analysis)

    def __getitem__(self, key):
        return self.analysis[key]

    def __len__(self):
        return len(self.analysis)

    def __eq__(self, other):
        return self.analysis == other.analysis

    def __slice__(self, start, stop, step):
        return Analysis(self.analysis[start:stop:step], self.SEP)

    def __contains__(self, item):
        return item in self.analysis

    def __add__(self, other):
        return Analysis(self.analysis + other.analysis, self.SEP)


class Underiver(ABC):
    def __init__(self):
        pass

    def makeAnalysis(self, analstring):
        return Analysis(analstring, self.SEP)

    @abstractmethod
    def generate(self, analysis):
        pass

    @abstractmethod
    def get_pos(self, analysis):
        pass

    def standardize(self, analysis):  # list
        infls = self.get_infl(analysis)

        pos = self.get_pos(analysis)

        analysis = self.strip_infl(analysis)
        if pos not in self.default_infl:
            infl = []  # should this be an error?
        else:
            infl = self.default_infl[pos]

        return analysis + self.makeAnalysis(infl), pos

    @abstractmethod
    def get_infl(self, analysis):
        pass

    def process_clitics(self, analysis):
        return analysis, None  # default for when no clitics

    @abstractmethod
    def strip_infl(self, analysis):
        pass

    def get_curr_der(self, analysis):  # list
        return self.strip_infl(analysis)[-1]

    def strip_deriv(self, analysis):  # list
        return self.strip_infl(analysis)[:-1]

    def underive(self, analysis):  # string
        try:
            analysis, entry = self.process_clitics(analysis)

            analysis = self.makeAnalysis(analysis)
            attested = True if entry is None else False
            while len(self.strip_infl(analysis)) > 1:
                standard, pos = self.standardize(analysis)
                entry = [
                    Entry(
                        self.generate(standard),
                        str(standard),
                        str(self.get_infl(standard)),
                        pos,
                        str(self.get_curr_der(analysis)),
                        entry,
                        attested=attested,
                    )
                ]
                if attested == True:
                    attested = False

                analysis = self.strip_deriv(analysis)

            standard, pos = self.standardize(analysis)
            entry = Entry(
                self.generate(standard),
                str(standard),
                str(self.get_infl(standard)),
                pos,
                "",
                entry,
            )
            print('££££££££££££SUCCESSS£££££££££££££', file=sys.stderr)
            return entry
        except GenerationError as e:
            try:
                if entry is None:
                    raise e
                elif isinstance(entry, list):
                    print("@@@@@@@@@HEY@@@@@@@", file=sys.stderr)
                    print(entry, file=sys.stderr)
                    return entry[0]
                else:
                    return entry
            except UnboundLocalError:
                raise e


class YupikUnderiver(Underiver):
    def __init__(self):
        self.SEP = "^"
        self.posmap = {
            "CmpdVbl": "V",
            "EMO": "V",
            "AREA": "N",
            "NAME": "N",
            "NUM": "N",
            "YUPIKALIZER": "N",
        }
        self.default_infl = {
            "V.Intr": ["[Ind.Intr]", "[3Sg]"],
            "V.Trns": ["[Ind.Trns]", "[3Sg.3Sg]"],
            "N": ["[Abs.Sg]"],
        }
        instr = hfst.HfstInputStream("ess.foma")
        self.fst = instr.read()
        instr.close()

    def get_pos(self, analysis):
        infl = self.get_infl(analysis)

        transitive = "Trns" if "Trns" in str(infl) else "Intr"
        affix = self.strip_infl(analysis)[-1]
        if affix == "ete":
            pos = "V"
        else:
            m = re.match(rf"([^{self.SEP}]+)(\([^\)]+\))", affix)  # get POS group
            if m is not None:
                pos = m.group(2).strip("()")
            else:
                pos = ""
            if "→" in pos:
                _, end = pos.split("→")
                pos = end
            if pos in self.posmap:
                pos = self.posmap[pos]
        if pos == "V":
            pos += "." + transitive
        return pos

    def generate(self, analysis):
        try:
            return remove_epsilons(self.fst.lookup(str(analysis))[0][0])
        except IndexError:
            raise GenerationError(f"Could not generate form for {analysis}")

    def strip_infl(self, analysis):
        return self.makeAnalysis([m for m in analysis if len(m) > 0 and m[0] != "["])

    def get_infl(self, analysis):
        return self.makeAnalysis([m for m in analysis if len(m) > 0 and m[0] == "["])

    def process_clitics(self, analysis):
        analysis = analysis.split("=")  # remove enclitics

        entry = None
        attested = True
        while len(analysis) > 1:
            standard, pos = self.standardize(self.makeAnalysis(analysis[0]))

            under = "=".join([str(standard)] + analysis[1:])
            entry = [
                Entry(
                    self.generate(under),
                    under,
                    str(self.get_infl(standard)),
                    pos,
                    "=" + analysis[-1],
                    entry,
                    attested=attested,
                )
            ]
            if attested:
                attested = False
            analysis = analysis[:-1]
        analysis = analysis[0]
        return analysis, entry


@dataclass
class Entry:
    """Entry in a derivational network"""

    surface: str
    underlying: str
    infl: str
    pos: str
    relation: str
    children: Iterable[str] = field(default_factory=list)
    attested: bool = False

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
                self.items[entry.underlying].attested = True
                return

            entry = entry.children[0]
        if attach_point is not None:
            if self.items[attach_point].children is None:
                self.items[attach_point].children = [entry]
            else:
                self.items[attach_point].children.append(entry)
        else:
            self.families[entry.underlying] = entry
        while entry is not None and entry.children is not None:
            self.items[entry.underlying] = entry
            entry = entry.children[0]
        if entry is not None:
            self.items[entry.underlying] = entry

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
                    node.relation,  # node.relation,
                    "",
                    f'{{ "attested":  {str(node.attested).lower()}, "underlying": {node.underlying} }}',
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
        result = "idx\tword\traw\tpos\tinfl\tlookup\tparent\tderi\tidk\tjs\n"
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
                parent_i = idx
                for child in node.children:
                    j += 1
                    if child is not None:
                        stack.append((child, parent_i, self.point(i, j)))

            result += "\n"
        return result


class KalUnderiver(Underiver):
    def __init__(self):
        self.SEP = "+"
        self.posmap = {
            "CmpdVbl": "V",
            "EMO": "V",
            "AREA": "N",
            "NAME": "N",
            "NUM": "N",
            "YUPIKALIZER": "N",
        }
        self.default_infl = {
            "V.Intr": ["Gram/IV", "V", "Ind", "3Sg"],
            "V.Trns": ["Gram/TV", "V", "Ind", "3Sg", "3SgO"],
            "V": ["V", "Ind", "3Sg"],
            "N": ["N", "Abs", "Sg"],
            "Num": ["Num", "Abs", "Sg"],
        }
        instr = hfst.HfstInputStream("fsts/lang-kal/src/generator-gt-desc.hfstol")
        self.fst = instr.read()
        instr.close()

    def get_pos(self, analysis):
        infl = self.get_infl(analysis)

        if "Gram/IV" in infl:
            return "V.Intr"
        elif "Gram/TV" in infl:
            return "V.Trns"
        elif "V" in infl:
            return "V"
        elif "N" in infl:
            return "N"
        elif "Num" in infl:
            return "Num"

        affix = self.strip_infl(analysis)[-1]
        if affix == "Der/vvUTE":
            return "V"
        elif affix.startswith("Der/"):
            return affix[-1].upper()
        return infl[0]

    def generate(self, analysis):
        try:
            return remove_epsilons(self.fst.lookup(str(analysis))[0][0])
        except IndexError:
            raise GenerationError(f"Could not generate form for {analysis}")

    def strip_infl(self, analysis):
        stripped = []
        found = False
        for m in reversed(analysis):
            if m.startswith("Der/") or len(m) == 0 or m[0].islower():
                found = True
            if found:
                stripped.append(m)
        if len(stripped) == 0:
            stripped = [analysis[0]]
        return self.makeAnalysis(reversed(stripped))

    def get_infl(self, analysis):
        stripped = []
        for m in reversed(analysis):
            stripped.append(m)
            if m.startswith("Der/") or m[0].islower():
                break
        if len(analysis) == 1:
            return self.makeAnalysis([])
        return self.makeAnalysis(reversed(stripped))

    def process_clitics(self, analysis):
        analysis = self.makeAnalysis(analysis)
        entry = None
        while (
            len(analysis) > 1 and analysis[-1].isupper()
        ):  # these tags are clitics lol
            standard, pos = self.standardize(analysis[:-1])
            under = self.SEP.join([str(analysis), analysis[-1]])
            entry = [
                Entry(
                    self.generate(under),
                    under,
                    str(self.get_infl(standard)),
                    pos,
                    analysis[-1],
                    entry,
                )
            ]
            analysis = analysis[:-1]
        return analysis, entry

    def get_curr_der(self, analysis):
        for i, m in enumerate(reversed(analysis)):
            if m.startswith("Der/"):
                return analysis[-i - 2] + self.SEP + m

    def strip_deriv(self, analysis):
        stripped = []
        found = 0
        # find last index starting with Der/ in analysis
        for i, m in enumerate(reversed(analysis)):
            if m.startswith("Der/"):
                theder = m
                found = i
                break
        for i, m in enumerate(reversed(analysis)):
            if i > found + 1:
                stripped.append(m)
        if len(stripped) == 1:
            return self.makeAnalysis(stripped + [theder[-2].upper()])

        return self.makeAnalysis(reversed(stripped))


def construct_der_net():

    parser = argparse.ArgumentParser()
    parser.add_argument("lang", help="language code")
    parser.add_argument("input", help="file to analyze")
    args = parser.parse_args()

    if args.lang == "kal":
        underiver = KalUnderiver()
    elif args.lang == "ess":
        underiver = YupikUnderiver()
    else:
        raise ValueError("Language not supported")

    net = DerNet()

    with open(args.input) as f:
        c = 0
        for line in f:

            if "PUNCT" in line or "CLB" in line:
                continue
            try:
                derivation = underiver.underive(line.strip())
                net.add_derivation(derivation)
            except GenerationError as e:
                c += 1
                print("No derivation found for", line.strip(), file=sys.stderr)
                print(e, file=sys.stderr)
    print(c, "derivations not found", file=sys.stderr)
    print(net)


if __name__ == "__main__":
    construct_der_net()

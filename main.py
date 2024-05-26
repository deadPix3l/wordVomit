#!/usr/bin/env python
import re
from collections import Counter
from functools import cache
import argparse
from math import ceil
from tabulate import tabulate
from collections import defaultdict

def run_length_decoding(encoded_string: str) -> Counter:
    counter = Counter()
    pattern = re.compile(r'([A-Za-z])(\d*)')

    for match in pattern.finditer(encoded_string.upper()):
        char = match.group(1)
        count = match.group(2)
        if count == '':
            count = 1
        else:
            count = int(count)
        counter[char] += count

    return counter

letter_values = {
    'A': 1, 'E': 1, 'I': 1, 'O': 1, 'N': 1, 'R': 1, 'T': 1, 'L': 1, 'S': 1, 'U': 1,
    'D': 2, 'G': 2,
    'B': 3, 'C': 3, 'M': 3, 'P': 3,
    'F': 4, 'H': 4, 'V': 4, 'W': 4, 'Y': 4,
    'K': 5,
    'J': 8, 'X': 8,
    'Q': 10, 'Z': 10
}

def match(pattern, wordlist) -> list:
    re_pattern = pattern.replace("_", "[A-Z]").upper()
    return [i for i in wordlist if re.match(re_pattern, i)]


@cache
def scoreWord(w: str) -> int:
    return sum(letter_values[letter.upper()] for letter in w)

def scoreWordNormalized(w: str) -> int:
    return scoreWord(w)/(len(w)-1)

def getWordChains():
    for i,v in enumerate(words):
        for other_word in words[i+1:]:
            if v in other_word:
                yield (v, other_word)

def hammingDistanceCounter(a: str, b: str) -> Counter:
    retval = Counter(b)
    retval.subtract(Counter(a))
    return retval

def missingLetters(myletters: str | Counter , word: str | Counter) -> list[tuple[str,int]]:
    dist = hammingDistanceCounter(myletters, word)
    return [i for i in dist.items() if i[1]>0]

def missingLettersCount(myletters: str | Counter, word: str | Counter) -> int:
    return sum(b for a,b in missingLetters(myletters, word))

def wordsMissingXLetters(myletters, wordlist, X: int = 0) -> list[str]:
    return filter(lambda word: missingLettersCount(myletters, word)<=X, wordlist)

def getReduced(word: str, reverse=False):
    for i,v in enumerate(word):
        if not reverse:
            if (x := word[:i]) in words:
                print(x)
                yield x

        else:
            if (x := word[i:]) in words:
                print(x)
                yield x

@cache
def reducedScore(word: str, reverse=False) -> int:
    return sum(scoreWord(i) for i in getReduced(word, reverse))

def reducedScoreAdjusted(word: str, reverse=False) -> int:
    return reducedScore(word, reverse)/(len(word)-1)

def sortWithMetric(f, iterable):
    return sorted(((i, f(i)) for i in iterable), key=lambda x: x[1])


# ------------------------------------------------ #
def find_word_chains(wordlist):
    wordlist = sorted(wordlist, key=len)  # Sort words by length
    chains = {}

    def is_extension(base_word, new_word):
        return new_word.startswith(base_word) and len(new_word) > len(base_word)

    for word in wordlist:
        for other_word in wordlist:
            if is_extension(word, other_word):
                if word not in chains:
                    chains[word] = []
                chains[word].append(other_word)
    
    return chains

def generateChains(wordlist: list[str], myletters):
    chains = defaultdict(list)
    for i,v in enumerate(wordlist):
        for new_word in wordlist[i+1:]:
            if v in new_word:
                chains[v].append(new_word)

    return chains

def processChains(chain):
    def inner(word: str, history=None):
        if history is None:
            history = []

        history += [word]
        if word not in chain:
            yield history
            return

        for i in chain[word]:
            yield from inner(i, history+[])
        return

    for k,v in list(chain.items()):
        for word in v:
            yield from (inner(word, history=[k]))



def scoreChain(chain):
    return sum(scoreWord(word) for word in chain) + len(chain)-1

def scoreChainNormalized(chain):
    return scoreChain(chain)/(len(chain[-1])-1)

def missingLetterChain(chain, myletters):
    first_word = chain[-1]
    return " ".join(a*b for a,b in missingLetters(myletters, first_word))

# ------------------------------------------------ #
banner = r"""
 _    _               _   _   _                 _ _   
| |  | |             | | | | | |               (_) |  
| |  | | ___  _ __ __| | | | | | ___  _ __ ___  _| |_ 
| |/\| |/ _ \| '__/ _` | | | | |/ _ \| '_ ` _ \| | __|
\  /\  / (_) | | | (_| | \ \_/ / (_) | | | | | | | |_ 
 \/  \/ \___/|_|  \__,_|  \___/ \___/|_| |_| |_|_|\__|
"""

def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument("myletters", type=run_length_decoding)
    parser.add_argument("-w", "--wordlist", type=argparse.FileType('r'), default="dictionary.txt")
    parser.add_argument("-p", "--points", type=float, default=0.21, help="Value per point")
    parser.add_argument("-c", "--cost", type=float, default=15, help="Cost to buy 7 letters")
    parser.add_argument("--actual-cost", type=float, default=None, help="Cost to buy 1 letter (overrides -c)")
    parser.add_argument("-s", "--sort-index", action="store", type=int, default=1, help="Which field to sort on (default: delta)")
    parser.add_argument("-b", "--breakeven", action="store", type=float, default=None, help="Manually override breakeven price")
    parser.add_argument("-t", "--top", action="store", default=25, type=int, help="Show top N words (default:25)")
    parser.add_argument("-m", "--missing", action="store", default=1, type=int, help="How many Letters are you allowed to not have (default: 1)")
    parser.add_argument("--all-words", action="store_true", help="show ALL words, even ones you cant make")
    parser.add_argument("--ignore-missing", action="store", type=str, default="", help="ignore certain missing letters (default:'', recommended: 'QWXZ')")
    return parser

def main():
    parser = setup()
    args = parser.parse_args()

    if args.actual_cost:
        args.cost = args.actual_cost*7

    if args.breakeven is None:
        args.breakeven = (args.cost/args.points)/7

    breakeven = args.breakeven


    print(banner)
    print("---------------------------------------------")
    print(f"       Cost: {args.cost}/7 letters ({args.cost/7:.3f}/letter)")
    print(f"       Points: {args.points}/letter")
    print(f"       breakeven: {breakeven} pts/letter ---")
    print("---------------------------------------------")

    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    myletters_str = " ".join(f"{c}{str(v).translate(SUP)}" for c,v in args.myletters.items())
    print(f"\nMy Letters: {myletters_str}\n")
# ---- Informational display over, lets get calculating! -----


    words = [i.strip().upper() for i in args.wordlist]
    myletters = args.myletters

    if args.all_words:
        wordsICanMake = words
    else:
        wordsICanMake = list(wordsMissingXLetters(myletters, wordlist=words, X=args.missing))

    profitableWords = [
            (
                scoreWord(word),
                scoreWordNormalized(word)-args.breakeven,
                ", ".join(a*b for a,b in missingLetters(myletters, word)),
                word
            )
            for word in wordsICanMake if scoreWordNormalized(word)-breakeven > 0]

    try:
        profitableWords.sort(key=lambda x: x[args.sort_index], reverse=True)

        print(f"  Top-{args.top} Most Profitable Words (One Shot):")
        print(tabulate(profitableWords[:args.top], headers=("pts", "delta (+/-)", "Missing Letters", "Word")))
        print()
    except IndexError:
        pass

    x = generateChains(wordsICanMake, myletters)

    scoresofChains= [ [scoreChain(i), scoreChainNormalized(i)-args.breakeven, missingLetterChain(i, myletters), " -> ".join(i), i[-1], scoreChain(i)-scoreWord(i[-1])] for i in processChains(x)]
    scoresofChains = [i for i in scoresofChains if not (i[2] not in i[4])]
    scoresofChains.sort(reverse=True, key=lambda x: x[args.sort_index])
    profitableChains = [i for i in scoresofChains if i[1]>=0]

    profitableChains = [i for i in profitableChains if (i[2]=="" or set(i[2])&set(i[3].partition(" ")[0]))]

    if args.ignore_missing:
        profitableChains = [i for i in profitableChains if not (set(i[2]) & set(args.ignore_missing)) ]

    print(tabulate(profitableChains[:args.top], headers=("pts","delta (+/-)", "Missing Letter", "Word Chains", "Final Word", "Bonus")))



if __name__ == "__main__":
    main()

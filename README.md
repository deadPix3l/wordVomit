![Logo](/assets/logo.png)

# WORD VOMIT

A strategy script for Words3 or other Scrabble-likes


This is a quick, dirty and small project.
The point isnt to make some finely tuned, nicely polished project to solve world hunger.
Its to write shit code to make money playing scrabble, and god damn it, it does that!
This code is not good, and it never will be. There is a place for clean, production-ready code
that follows PEPs and is tested and bug free, and a scrabble bot written in 2 days is not it.
PRs Welcome I guess?

## How to Use

```
./main.py abc3de4f
```

The first argument is your letters, using run-length-encoding (RLE)
If you want to tell the program you have 1 A, 2 B's, 3 C's, 1 D, and 4 E's,
you can either just repeat characters: `ABBCCCDEEEE` or follow each letter with a count `a1b2c3d1e4`
You can omit the count and it will be assumed to be 1. you can repeat letters: `a3...a4...a2` is equivilant to `a9`

Some options have been provided for specifying the cost of buying 7 letters, the cost one each letter (if you prefer to do the math that way), the point conversion ratio, and some overrides to tailor results if needed.

### What is Delta?

If you play a word like "southerners", thats worth a pretty decent amount of points! But it also uses a lot of letters!
Rather than raw word score, you need to normalize it with how many letters you used for a "per-letter-used" score.
By subtracting the breakeven from this, you get the delta. A positive delta means you are earning more ETH per letter than you paid.
Simply put: positive delta = profit, negative delta = loss.

### What is a word chain?

Instead of playing 'southerners' as one word, the turnless nature of words3 gives us an opportunity to expand this as:
```
so
sout
south
souther
southern
southerner
southerners
```
and get credit for each of those words! You spend the same letters and get massively more points and boost your delta!

### 2L, 3L, 2W, etc

We dont account for these. This is considered bonus points that shouldnt be relied on.


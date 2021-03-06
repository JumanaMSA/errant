from errant.alignment import Alignment
from errant.parsedToken import ParsedToken
from errant.edit import Edit
from spacy.tokens import Doc
import camel_tools.tokenizers.word


# Main ERRANT Annotator class
class Annotator:

    # Input 1: A string language id: e.g. "en"
    # Input 2: A spacy processing object for the language, None in case of Arabic language
    # Input 3: A merging module for the language
    # Input 4: A classifier module for the language
    def __init__(self, lang, nlp=None, merger=None, classifier=None):
        self.lang = lang
        self.nlp = nlp
        self.merger = merger
        self.classifier = classifier

    # Input 1: A text string
    # Input 2: A flag for word tokenisation
    # Output:  An array of ParsedToken objects
    def parse(self, text, tokenise=False):

        tokens = []
        
        if self.lang == "en":
            if tokenise:
                text = self.nlp(text)
            else:
                text = Doc(self.nlp.vocab, text.split())
                self.nlp.tagger(text)
                self.nlp.parser(text)

            for o in text:
                tokens.append(ParsedToken(o.text, o.lemma_, o.pos_, o.tag_, o.dep_)) # Spacy values
                                                                                     # dep_ is only needed in the Engliah classifier, never care if it doesn't exist in Arabic analyzer.
        
        if self.lang == "ar":

            # Parse the sentence by an Arbic morphological analyzer

            text = camel_tools.tokenizers.word.simple_word_tokenize(text)

            for o in text:
                # To analyze a word, we can use the analyze() method
                analyzedWord = self.nlp[0].analyze(o)
                # Handle the problem if the token is null
                if analyzedWord:
                    lemma = analyzedWord[0]["stem"]
                    pos = analyzedWord[0]["pos"]
                else:
                    lemma = ''
                    pos = ''
                tag = self.nlp[1].tag(o.split())[0]
                tokens.append(ParsedToken(o, lemma, pos, tag)) # Replace this by the values from an Arbic morphological analyzer 

        return tokens

    # Input 1: An array of ParsedToken objects of the original text
    # Input 2: An array of ParsedToken objects of the corrected text
    # Input 3: A flag for standard Levenshtein alignment
    # Output: An Alignment object
    def align(self, orig, cor, lev=False):
        return Alignment(orig, cor, lev)

    # Input 1: An Alignment object
    # Input 2: A flag for merging strategy
    # Output: A list of Edit objects
    def merge(self, alignment, merging="rules"):
        # rules: Rule-based merging
        if merging == "rules":
            edits = self.merger.get_rule_edits(alignment, self.lang)
        # all-split: Don't merge anything
        elif merging == "all-split":
            edits = alignment.get_all_split_edits()
        # all-merge: Merge all adjacent non-match ops
        elif merging == "all-merge":
            edits = alignment.get_all_merge_edits()
        # all-equal: Merge all edits of the same operation type
        elif merging == "all-equal":
            edits = alignment.get_all_equal_edits()
        # Unknown
        else:
            raise Exception("Unknown merging strategy. Choose from: "
                "rules, all-split, all-merge, all-equal.")
        return edits

    # Input: An Edit object
    # Output: The same Edit object with an updated error type
    def classify(self, edit):
        return self.classifier.classify(edit)

    # Input 1: An array of ParsedToken objects of the original text
    # Input 2: An array of ParsedToken objects of the corrected text
    # Input 3: A flag for standard Levenshtein alignment
    # Input 4: A flag for merging strategy
    # Output: A list of automatically extracted, typed Edit objects
    def annotate(self, orig, cor, lev=False, merging="rules"):
        alignment = self.align(orig, cor, lev)
        edits = self.merge(alignment, merging)
        for edit in edits:
            edit = self.classify(edit)
        return edits

    # Input 1: An array of ParsedToken objects of the original text
    # Input 2: An array of ParsedToken objects of the corrected text
    # Input 3: A token span edit list; [o_start, o_end, c_start, c_end, (cat)]
    # Input 4: A flag for gold edit minimisation; e.g. [a b -> a c] = [b -> c]
    # Input 5: A flag to preserve the old error category (i.e. turn off classifier)
    # Output: An Edit object
    def import_edit(self, orig, cor, edit, min=True, old_cat=False):
        # Undefined error type
        if len(edit) == 4:
            edit = Edit(orig, cor, edit)
        # Existing error type
        elif len(edit) == 5:
            edit = Edit(orig, cor, edit[:4], edit[4])
        # Unknown edit format
        else:
            raise Exception("Edit not of the form: "
                "[o_start, o_end, c_start, c_end, (cat)]")
        # Minimise edit
        if min: 
            edit = edit.minimise()
        # Classify edit
        if not old_cat: 
            edit = self.classify(edit)
        return edit

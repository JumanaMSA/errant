# ERRANT edit class
class Edit:

    # Input 1: An array of ParsedToken objects of the original text
    # Input 2: An array of ParsedToken objects of the corrected text
    # Input 3: A token span edit list: [o_start, o_end, c_start, c_end]
    # Input 4: An error type string, if known
    def __init__(self, orig, cor, edit, type="NA"):
        # Orig offsets, ParsedToken object and string
        self.o_start = edit[0]
        self.o_end = edit[1]
        self.o_toks = orig[self.o_start:self.o_end]
        self.o_str = ' '.join(o.text for o in self.o_toks) if self.o_toks else ""       # Change self.o_toks.text to  ' '.join(o.text for o in self.o_toks)
        # Cor offsets, ParsedToken object tokens and string
        self.c_start = edit[2]
        self.c_end = edit[3]
        self.c_toks = cor[self.c_start:self.c_end]
        self.c_str = ' '.join(c.text for c in self.c_toks) if self.c_toks else ""       # Change self.c_toks.text to  ' '.join(c.text for c in self.c_toks)
        # Error type
        self.type = type

    # Minimise the edit; e.g. [a b -> a c] = [b -> c]
    def minimise(self):
        # While the first token is the same on both sides
        while self.o_toks and self.c_toks and \
                self.o_toks[0].text == self.c_toks[0].text:
            # Remove that token from the span, and adjust the start offsets
            self.o_toks = self.o_toks[1:]
            self.c_toks = self.c_toks[1:]
            self.o_start += 1
            self.c_start += 1
        # Do the same for the last token
        while self.o_toks and self.c_toks and \
                self.o_toks[-1].text == self.c_toks[-1].text:
            self.o_toks = self.o_toks[:-1]
            self.c_toks = self.c_toks[:-1]
            self.o_end -= 1
            self.c_end -= 1
        # Update the strings
        self.o_str = ' '.join(o.text for o in self.o_toks) if self.o_toks else ""           # Change self.o_toks.text to  ' '.join(o.text for o in self.o_toks)
        self.c_str = ' '.join(c.text for c in self.c_toks) if self.c_toks else ""           # Change self.c_toks.text to  ' '.join(c.text for c in self.c_toks)
        return self

    # Input: An id for the annotator
    # Output: An edit string formatted for an M2 file
    def to_m2(self, id=0):
        span = " ".join(["A", str(self.o_start), str(self.o_end)])
        cor_toks_str = " ".join([tok.text for tok in self.c_toks])
        return "|||".join([span, self.type, cor_toks_str, "REQUIRED", "-NONE-", str(id)])

    # Edit object string representation
    def __str__(self):
        orig = "Orig: "+str([self.o_start, self.o_end, self.o_str])
        cor = "Cor: "+str([self.c_start, self.c_end, self.c_str])
        type = "Type: "+repr(self.type)
        return ", ".join([orig, cor, type])
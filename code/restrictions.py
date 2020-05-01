"""restrictions.py

Module to extract restrictions from frames and then link them to elements of
example sentences. 

There is a preprocess step that takes all example sentences and then creates a
resource with all the sentences plus their tokenized and tagged forms. To run
this set the PREPROCESS variable to True. The results of this preprocessing are
written to the standard output and should be stored in sentences.pos.txt, and
they are required for further processing.

The result of main processing is also written to standard output in the form of
a list of restirctions with for each of them a list of phrases from the examples
that should meet the restrictions. Here is a fragment of the output on just the
first five verbclasses in Verbet:

(+int_control)

   2  Steve
   1  The builders
   1  The Romans

The COUNT variable is used to determine how many classes to process. This is
used for both the preprocessing and the main processing. If you want to process
all verb classes set this to a sufficiently large number like 555.

The TREETAGGER_DIR variable needs to be set to reflect the location of the
TreeTagger.

The VerbNet location should be specified in confix.txt.

"""


from collections import Counter
import path
from tokenizer import Tokenizer
from treetagger import TreeTagger
import verbnetparser;

TREETAGGER_DIR = "/Applications/ADDED/nlp/treetagger"

VERBOSE = False
PREPROCESS = False
COUNT = 5


def preprocess_sentences():
    """Run a tokenizer and the TreeTagger on example sentences from VerbNet
    (number of classes used is determined by the COUNT variable) and write these
    sentences with tokenized and tagged form to the standard output."""
    # first get all the example sentences
    sentences = []
    for vc in verbnetparser.read_verbnet(max_count=COUNT):
        for frame in vc.frames:
            sentences.append(frame.examples[0])
    # then run the tagger over them
    tagger = TreeTagger(TREETAGGER_DIR)
    for sentence in sentences:
        tokenized = tokenize(sentence)
        tags = tag(tagger, tokenized)
        # and write the result to stdout
        print("%s\t%s\t%s" % (sentence.strip(), tokenized.strip(), ' '.join(tags)))


def tokenize(sentence):
    tokenizer = Tokenizer(sentence)
    tokenizer.tokenize_text()
    tokenized = tokenizer.get_tokenized_as_string()
    return tokenized


def tag(tagger, tokenized_string):
    vertical = "<s>\n" + tokenized_string.replace(" ", "\n")
    tagged = tagger.tag_text(vertical)
    tags = []
    for item in tagged:
        if not item == '<s>':
            (text, tag, lemma) = item.split("\t")
            tags.append(tag)
    return tags


class RestrictionFinder(object):

    def __init__(self, vnclasses):
        self.vnclasses = vnclasses
        self.lookup = load_lookup()
        self.vnclass = None;
        self.vnframe = None;
        self.alligned = []

    def process(self):
        self.not_parsed = 0
        self.parsed = 0
        for vc in self.vnclasses:
            self.process_class(vc)
        self.extract_restrictions()
        print("\nNOT PARSED: %d" % self.not_parsed)
        print("PARSED: %d\n" % self.parsed)

            
    def process_class(self, vc):
        self.vnclass = vc
        #print vc
        if VERBOSE: print(vc)
        for frame in vc.frames:
            self.process_frame(frame)

    def process_frame(self, frame):
        self.vnframe = frame
        example_sentence = frame.examples[0].strip()
        if VERBOSE:
            print()
            print(frame.description)
            print(example_sentence)
            for srole in frame.syntax:
                print("  ", srole)
        self.align(example_sentence, frame.syntax)

    def align(self, sentence, syntactic_roles):
        lexes = self.tag_sentence(sentence)
        if VERBOSE:
            print()
            print_lexes(lexes, 0, len(lexes))
        idx = 0
        alligned_pairs = []
        for role in syntactic_roles:
            new_idx = self.consume_tokens(role, lexes, idx)
            if new_idx == idx:
                #print_lexes(lexes, 0, len(lexes))
                #print_roles(syntactic_roles)
                next_lex = lexes[idx] if idx < len(lexes) else "END"
                #print "Could not consume %s at %d %s" % (role.pos, idx, next_lex),
                #print_lexes(lexes, idx, new_idx)
                #self.print_pairs(alligned_pairs)
                #print
                self.not_parsed += 1
                break
            alligned_pairs.append((self.vnclass, self.vnframe,
                                   role, idx, new_idx, lexes[idx:new_idx]))
            idx = new_idx
        # TODO: add check that idx is same as len(lexes)
        self.parsed += 1
        self.alligned.extend(alligned_pairs)
        if VERBOSE:
            self.print_pairs(alligned_pairs)
        
    def print_pairs(self, alligned_pairs):
        for (vc, frame, role, p1, p2, lexes) in alligned_pairs:
            print("  ", role.pos, p1, p2, end=' ')
            print_lexes(lexes, 0, len(lexes))

    def tag_sentence(self, sentence):
        tokens, tags = self.lookup[sentence]
        tokens = tokens.split()
        tags = tags.split()
        if tokens[-1] == "." and tags[-1] == "SENT":
            tokens = tokens[:-1]
            tags = tags[:-1]
        if len(tokens) != len(tags):
            print(tokens)
            print(tags)
            exit("WARNING - UNBALANCED LISTS")
        lexes = list(zip(tokens, tags))
        return lexes

    def consume_tokens(self, role, lexes, idx):
        if role.pos == "LEX":
            return slurp_LEX(lexes, idx)
        elif role.pos == "VERB":
            return slurp_VERB(lexes, idx)
        elif role.pos == "NP":
            return slurp_NP(lexes, idx)
        elif role.pos == "PP":
            return slurp_PP(lexes, idx)
        elif role.pos == "PREP":
            return slurp_PREP(lexes, idx)
        elif role.pos == "ADJ":
            return slurp_ADJ(lexes, idx)
        elif role.pos == "ADV":
            return slurp_ADV(lexes, idx)
        else:
            print("WARNING: cannot slurp a", role.pos)

    def extract_restrictions(self):
        #print len(self.alligned)
        self.restrictions = {}
        previous = None
        for (vc, frame, role, p1, p2, lexes) in self.alligned:
            header = "%s - %s" % (vc.ID, frame.description)
            if header != previous:
                #print header
                previous = header
            restrictions = role.get_restrictions()
            if restrictions is not None and not restrictions.is_empty():
                restrictions = "%s" % role.get_restrictions()
                phrase = ' '.join([w for w,t in lexes])
                self.restrictions.setdefault(restrictions, []).append(phrase)
            #print '  ', role.pos, role.value, restrictions, lexes
        for key, vals in list(self.restrictions.items()):
            print("\n%s\n" % key)
            for (phrase, count) in list(Counter(vals).items()):
                print("  %2d  %s" % (count, phrase))


def print_lexes(lexes, idx1, idx2):
    print(' '. join(["%s/%s" % (tok, tag) for tok, tag in lexes[idx1:idx2]]))

    
def print_roles(roles):
    print(' '.join([role.pos for role in roles]))
    
    
def load_lookup():
    lookup = {}
    for line in open('sentences.pos.txt'):
        (s, tokens, tags) = line.strip().split("\t")
        lookup[s] = (tokens, tags)
    return lookup


def slurp_LEX(lexes, idx):
    return idx


def slurp_NP(lexes, idx):
    return slurp(lexes, idx, 
                 ['VVG RB IN NN',  # coming back in time
                  'VVG DT NNS',  # dealing the cards
                  'CD CD NNS',
                  'DT JJ NN',
                  'DT NN NNS', 'DT NP NP',
                  'DT NNS', 'DT NN', 'DT NP', 'DT CD',
                  'NN NNS', 'CD NNS',
                  'PP$ NN', 'NP NP',
                  'PP$ VVG', # relies on [his helping]
                  'NN', 'NNS', 'PP', 'NP'])

def slurp_VERB(lexes, idx):
    return slurp(lexes, idx,
                 ['RB VH TO VV', # really have to empathize
                  'VVZ RB VV', 'VBZ VVG', 'VVD RP', 'RB VVP',
                  'MD VV', 'VVD', 'VVP', 'VVN', 'VVZ', 'VV'])


def slurp_PP(lexes, idx):
    return idx


def slurp_PREP(lexes, idx):
    return slurp(lexes, idx, ['DT IN', 'IN', 'TO'])


def slurp_ADJ(lexes, idx):
    return idx


def slurp_ADV(lexes, idx):
    return slurp(lexes, idx, ['RB'])


def slurp(lexes, idx, patterns):
    tags = [tag for token, tag in lexes[idx:]]
    for pattern in patterns:
        pattern = pattern.split()
        if pattern == tags[:len(pattern)]:
            return idx + len(pattern)
    return idx



if __name__ == '__main__':

    # Create a resource of all sentences in verbnet and its tags
    # as generated by the TreeTagger
    if PREPROCESS:
        preprocess_sentences()

    verb_classes = verbnetparser.read_verbnet(max_count=COUNT)
    rf = RestrictionFinder(verb_classes)
    rf.process()

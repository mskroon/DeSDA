from nltk.tokenize import TweetTokenizer

def tokenize_text(text, base_tknzr=TweetTokenizer(strip_handles=True, reduce_len=True, preserve_case=False)):
    tokens = base_tknzr.tokenize(text)
    # print('\t', tokens)
    sequences_to_change = {
        ('c', ':'): ['c:'],
        (':', '"', ')'): [':")'],
        (':', '"', '('): [':"('],
        ("'", 's'): ["'s"],
        ('^', '^'): ['^^'],
        ('d', '&', 'd'): ['D&D'],
        ('d', ':'): ['D:'],
        (':', '0'): [':0'],
        ('’', 'n'): ["'n"],
        (':', 'o'): [':o'],
        (':', 's'): [':s'],
        ('... ...',): ['...', '...'],

    }
    for sequence, correction in sequences_to_change.items():
        sequence = list(sequence)
        # print('\t', sequence)
        for i in range(len(tokens) - len(sequence) + 1):
            ngram = tokens[i:i + len(sequence)]
            # print('\t\t', ngram)
            if ngram == sequence:
                # print('\t\t\t', ngram == sequence)
                tokens[i:i + len(sequence)] = correction
                # print('\t\t\t', tokens)
                i -= len(sequence) - 1
    # print('\t', tokens)
    return tokens


# with open('whatsapp.txt', 'r', encoding='utf8') as f:
#     for line in f:
#         line = line.split(':', 2)[-1]
#         print(line)
#         print(tokenize_text(line))
#         input()
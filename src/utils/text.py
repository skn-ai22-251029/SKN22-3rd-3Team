from kiwipiepy import Kiwi

kiwi = Kiwi()

def tokenize_korean(text: str) -> str:
    """
    Tokenizes Korean text for BM25/keyword search.
    Extracts Nouns, Verbs, and Adjectives.
    """
    if not text:
        return ""
    # Extract only Nouns, Verbs, Adjectives (NNG, NNP, VV, VA)
    tokens = kiwi.tokenize(text)
    selected = [t.form for t in tokens if t.tag.startswith(('N', 'V'))]
    return " ".join(selected)

import os
import json
import ssl
from kiwipiepy import Kiwi

# SSL Context Fix for Kiwi Model Download (Corporate/Mac Networks)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Singleton Instances
_kiwi = None
_stopwords = set()
_synonyms = {}

def get_kiwi():
    global _kiwi
    if _kiwi is None:
        _kiwi = Kiwi()
        # Load User Dictionary
        paths = [
            "src/core/domain_dictionary.txt",
            "/Users/leemdo/Workspaces/SKN22-3rd-3Team/src/core/domain_dictionary.txt"
        ]
        for path in paths:
            if os.path.exists(path):
                print(f"📚 Loading User Dictionary from: {path}")
                _kiwi.load_user_dictionary(path)
                break
    return _kiwi

def load_resources():
    """Loads external resources (stopwords, synonyms) if not already loaded."""
    global _stopwords, _synonyms
    
    if not _stopwords:
        paths = [
            "src/core/stopwords.txt",
            "../core/stopwords.txt",
            "/Users/leemdo/Workspaces/SKN22-3rd-3Team/src/core/stopwords.txt"
        ]
        for path in paths:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    _stopwords = set(line.strip() for line in f if line.strip())
                print(f"🛑 Loaded {len(_stopwords)} stopwords from {path}")
                break
    
    if not _synonyms:
        paths = [
            "src/core/synonyms.json",
            "../core/synonyms.json",
            "/Users/leemdo/Workspaces/SKN22-3rd-3Team/src/core/synonyms.json"
        ]
        for path in paths:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    grouped_data = json.load(f)
                    
                # Flatten the structure: {Standard: [Alias1, Alias2]} -> {Alias1: Standard, Alias2: Standard}
                # Also handling backward compatibility if needed (but we just refactored it)
                for standard_name, aliases in grouped_data.items():
                    # Support both list and string (legacy safety)
                    if isinstance(aliases, list):
                        for alias in aliases:
                            _synonyms[alias] = standard_name
                    elif isinstance(aliases, str):
                        # Legacy format fallback: key was alias, val was standard? 
                        # No, new format key=Standard. 
                        # If file is legacy flat: key=Alias, val=Standard.
                        # Detection: aliases is string -> standard_name is Key.
                        # But wait, our refactor changed Key to Standard.
                        # If we load legacy file by mistake, Key(Alias): Value(Standard).
                        # Then _synonyms[Alias] = Standard. Correct.
                        _synonyms[standard_name] = aliases
                        
                print(f"🔄 Loaded {len(_synonyms)} flattened synonym mappings from {path}")
                break

# Initial Load (optional, or lazy load in tokenize)
# load_resources()

def tokenize_korean(text: str) -> str:
    """
    Tokenizes Korean text using Kiwi (with Domain Dictionary).
    Extracts Nouns (NN*), Verbs (VV), Adjectives (VA), Roots (XR).
    Removes Stopwords.
    Applies Synonyms.
    """
    if not text:
        return ""
        
    kiwi = get_kiwi()
    load_resources() # Ensure resources are loaded
    
    tokens = kiwi.tokenize(text)
    
    selected_tokens = []
    for t in tokens:
        # Filter tags: Noun, Verb, Adjective, Root
        if t.tag.startswith(('N', 'V', 'XR')):
            # Filter stopwords
            if t.form not in _stopwords:
                # Synonym Replacement
                token_form = t.form
                if token_form in _synonyms:
                    token_form = _synonyms[token_form]
                    
                selected_tokens.append(token_form)
    
    return " ".join(selected_tokens)

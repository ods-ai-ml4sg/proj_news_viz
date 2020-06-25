from sklearn.feature_extraction.text import TfidfVectorizer


def identity_tokenizer(text):
    return text


def make_feats(data):
    tfidf = TfidfVectorizer(tokenizer=identity_tokenizer, lowercase=False)    
    feats = tfidf.fit_transform(data)
    return feats

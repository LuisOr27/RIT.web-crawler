import re
import os
import nltk
import codecs
import nltk.tokenize as tokenize

from utils.pdf2txt import pdfparser
from nltk import word_tokenize
from nltk.corpus import wordnet
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords as stpwrds

"""
    Descargas necesarias para stopwards
    import nltk
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')
    nltk.download('wordnet')
    nltk.download('omw-1.4')
"""


def preprocess_documents(filename):
    """
        Preprocess a file using different methods of preprocessing, saves the result in a txt file
        Input: name of the file to be processed
    """
    text = pdfparser("original_files/" + filename)
    name = filename + ".txt"

    # ------- PREPROCESSING -------
    text = preprocess_text(text)

    mode = 'a' if os.path.exists("preprocessed_files/" + name) else 'w+'
    with codecs.open("preprocessed_files/" + name, mode,
                     encoding="utf-8", errors='replace') as text_file:
        print(text, file=text_file)


def preprocess_text(text):
    text = capitalLetters(text)
    text = accents(text)
    text = punctuation_marks(text)
    text = emoticons(text)
    text = line_breaks(text)
    text = numbers(text)
    text = url(text)
    text = stopwords(text)
    text = lemmatization(text)
    return text


def capitalLetters(text: str):
    """
        Convert capital letters from text into lowercase letters
        Input: text to be processed
        Output: text without capital letters
    """
    return text.lower()


def accents(text):
    """
        Convert accented letters from text
        Input: text to be processed
        Output: text without accented letters
    """
    a, b = 'áéíóúü', 'aeiouu'
    trans = str.maketrans(a, b)
    return text.translate(trans)


def emoticons(text):
    """
        Delete empticons from text
        Input: text to be processed
        Output: text without emoticons
    """
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # miscellaneous symbols and pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F900-\U0001F9FF"  # supplemental symbols & pictographs
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002600-\U000026FF"  # miscellaneous symbols 
                               u"\U00002B00-\U00002BFF"  # miscellaneous symbols and arrows
                               u"\U00002700-\U000027BF"  # dingbats
                               u"\U0001F650-\U0001F67F"  # ornamental dingbats
                               u"\U00002190–\U000021FF"  # arrows
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    clean_file = emoji_pattern.sub("", text)
    return clean_file


def line_breaks(text):
    """
        Convert line breaks
        Input: text to be processed
        Output: text without line breaks
    """
    escape_pattern = re.compile("(\\\\n)|(\\\\\")|(\")")
    result = escape_pattern.sub(" ", text)
    return result


def lemmatization(text):
    """
        Lemmatizate text
        Input: text to be processed
        Output: lemmatized text
    """
    stemmer = SnowballStemmer('spanish')

    return [stemmer.stem(i) for i in word_tokenize(text)]


def numbers(text):
    """
    Delete numbers from text
    Input: text to be processed
    Output: text without numbers
    """

    tokens = tokenize.word_tokenize(text, language="spanish")
    result = [token for token in tokens if not token.isnumeric()]
    result = " ".join(result)
    return result


def punctuation_marks(text):
    """
        Remove punctuation marks
        Input: text to be processed
        Output: text without punctuation marks
    """
    spanish_punctuation = r"""!¡"#$%&'()*+,-./:;<                = >¿?@[\]^_`{|}~¨´§«»¶\\’“”’"""
    pattern = re.compile(f"[{spanish_punctuation}]")
    clean_file = pattern.sub(" ", text)
    return clean_file


def stopwords(text):
    """
        Remove stopwords
        Input: text to be processed
        Output: text without stopwords
    """
    stop = set(stpwrds.words('spanish'))
    tokens = tokenize.word_tokenize(text, language="spanish")
    clean_file = filter(lambda x: x not in stop, tokens)
    return ' '.join(clean_file)


def url(text):
    """
        Remove url from text
        Input: text to be processed
        Output: text without url
    """
    pattern = re.compile(
        "(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})")
    result = pattern.sub("", text)
    return result


def thesaurus(word):
    """
        Apply thesaurus to text
        Input: text to be processed
    """
    synonyms = []
    antonyms = []
    hypernyms = []
    syn = wordnet.synsets(word)[0]
    hypernyms.append(syn.hypernyms()[0].hyponyms())
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.append(lemma.name())
            if lemma.antonyms():
                antonyms.append(lemma.antonyms()[0].name())

    print(set(synonyms))
    print(set(antonyms))
    print(hypernyms)


def lexical_analysis(content):
    """
        Remove aplly lexical analysis to text
        Input: text to be processed
    """
    tokens = nltk.word_tokenize(content)
    print(tokens)
    tagged = nltk.pos_tag(tokens)
    entities = nltk.chunk.ne_chunk(tagged)
    print(entities)

import pandas as pd
import numpy as np
from gensim.utils import simple_preprocess
from gensim.models import Word2Vec


def tokenize(corpus: pd.Series) -> pd.Series:
    """Converts each document of a corpus(list of documents) into a list of lowercase tokens using :func:`~gensim.utils.simple_preprocess`.
    Also checks if null documents are present and replaces them with an empty string('').

    Uses :func:`~pandas.Series.apply` to tokenize each document.

    Parameters
    ----------
    corpus : pandas.Series
        Input corpus or document list.

    Returns
    -------
    pd.Series
        Tokenized corpus with each document tokenized.

    """
    # handle null values if exist
    # replace null value with empty string
    if corpus.isna().sum() > 0:
        corpus = corpus.fillna('')

    # tokenize each document
    corpus = corpus.apply(simple_preprocess)

    return corpus


def get_word_vectors(model_load_path: str) -> pd.DataFrame:
    model: Word2Vec = None
    word_vectors: pd.DataFrame = None

    # load the model
    model = Word2Vec.load(model_load_path)

    # extract word vectors as dataframe from the model
    word_vectors = pd.DataFrame(
        [model.wv.get_vector(str(word)) for word in model.wv.key_to_index],
        index = model.wv.key_to_index
    )

    return word_vectors


def get_document_matrix(corpus: pd.Series, model_load_path: str) -> pd.DataFrame:
    model: Word2Vec = None
    document_vectors: list = []
    document_matrix: pd.DataFrame = None

    # load the model
    model = Word2Vec.load(model_load_path)

    # convert document vectors from word vectors
    for document in corpus:
        document_vector = np.zeros(model.vector_size)
        for word in document:
            if word in model.wv.index_to_key:
                document_vector += model.wv[word]
        document_vector = document_vector if len(document)==0 else (document_vector/len(document))
        document_vectors.append(document_vector)

    # extract document matrix as dataframe from document vectors
    document_matrix = pd.DataFrame(document_vectors)

    return document_matrix



def fit(corpus: pd.Series, model_save_path: str, params: dict, model_load_path: str = '') -> str:
    corpus: pd.Series = tokenize(corpus)
    model: Word2Vec = None

    # load a word2vec model from path if provided
    # else instantiate a model
    if model_load_path:
        model = Word2Vec.load(model_load_path)
    else:
        model = Word2Vec(window=params['window'], min_count=params['min_count'])
    
    # build vocabulary from corpus
    model.build_vocab(corpus, progress_per=1000)

    # train the model
    model.train(corpus, total_examples=model.corpus_count, epochs=params['epochs'])

    # save the model
    model.save(model_save_path)

    return model_save_path


def transform(corpus: pd.Series, model_load_path: str) -> tuple:
    corpus: pd.Series = tokenize(corpus)
    document_matrix: pd.DataFrame = None

    # extract document matrix
    document_matrix = get_document_matrix(corpus, model_load_path)

    return document_matrix, model_load_path


def fit_transform(corpus: pd.Series, model_save_path: str, params: dict, model_load_path: str = '') -> tuple:
    # trains a model, saves the model and returns the path of saved model
    fit(corpus, model_save_path, params, model_load_path)

    # transform uses the trained model
    # model_save_path is provided as model_load_path
    return transform(corpus, model_load_path=model_save_path)
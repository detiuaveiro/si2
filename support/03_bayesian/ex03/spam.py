import math
import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer


def np_log_fit(x, y):
    a, b = np.polyfit(np.log(x), y, 1)
    return a, b


def np_exp_fit(x, y):
    a, b = np.polyfit(x, np.log(y), 1, w=np.sqrt(y))
    return a, np.exp(b)


class NB:
    def __init__(self, k=1, m=2):
        self.k = k
        self.m = m
        self.lemmatizer = WordNetLemmatizer()

    def _nltk_pos_tagger(self, nltk_tag):
        if nltk_tag.startswith("J"):
            return nltk.corpus.wordnet.ADJ
        elif nltk_tag.startswith("V"):
            return nltk.corpus.wordnet.VERB
        elif nltk_tag.startswith("N"):
            return nltk.corpus.wordnet.NOUN
        elif nltk_tag.startswith("R"):
            return nltk.corpus.wordnet.ADV
        else:
            return None

    def _nltk_pos_lemmatizer(self, token, tag):
        if tag is None:
            return self.lemmatizer.lemmatize(token)
        else:
            return self.lemmatizer.lemmatize(token, tag)

    def _vocab(self, samples):
        vocab = [token for sample in samples for token in sample]
        # print(f'{samples}/{vocab}')
        return list(set(vocab))

    def _compute_likelihood(self, samples):
        likelihood = {}
        vocab = self._vocab(samples)

        for w in vocab:
            count = 0
            for sentence in samples:
                if w in sentence:
                    # print(w+":", sentence)
                    count += 1
            # print(f"Number of ham emails with the word '{w}': {count}")
            # prob = (count + self.k)/(len(samples) + 2.0*self.k) # smoothing
            # print(f"Probability of the word '{w}': {prob} ")
            likelihood[w.lower()] = count
        return likelihood

    def _p_word_spam(self, token):
        return (self.k + self.likelihood_spam.get(token, 0.0)) / (
            (2.0 * self.k) + self.num_spam_messages
        )

    def _p_word_ham(self, token):
        return (self.k + self.likelihood_ham.get(token, 0.0)) / (
            (2.0 * self.k) + self.num_ham_messages
        )

    def get_spam_vocab(self, n=10):
        vocab = []
        for k in self.likelihood_spam:
            prob = self._p_word_spam(k)
            vocab.append((k, prob))
        # Sort the vocab
        vocab.sort(reverse=True, key=lambda e: (e[1], e[0]))
        # Return
        return vocab[: min(n, len(vocab))]

    def get_ham_vocab(self, n=10):
        vocab = []
        for k in self.likelihood_ham:
            prob = self._p_word_ham(k)
            vocab.append((k, prob))
        # Sort the vocab
        vocab.sort(reverse=True, key=lambda e: (e[1], e[0]))
        # Return
        return vocab[: min(n, len(vocab))]

    def train(self, dataset):
        # compute priors
        dataset_total = len(dataset)
        spam_samples = [txt for txt, label in dataset if label == "spam"]
        ham_samples = [txt for txt, label in dataset if label == "ham"]

        # print(f'{spam_samples}')
        # print(f'{ham_samples}')

        self.ps = len(spam_samples) / dataset_total
        self.ph = len(ham_samples) / dataset_total

        # print(f'{self.ps} {self.ph}')

        # Pre-process text
        ## Tokenize the text and get the POS (Part Of Speech)
        spam_samples_nltk_tagged = [
            nltk.pos_tag(nltk.word_tokenize(sample)) for sample in spam_samples
        ]
        spam_samples = [
            [(t[0], self._nltk_pos_tagger(t[1])) for t in tokens]
            for tokens in spam_samples_nltk_tagged
        ]
        ham_samples_nltk_tagged = [
            nltk.pos_tag(nltk.word_tokenize(sample)) for sample in ham_samples
        ]
        ham_samples = [
            [(t[0], self._nltk_pos_tagger(t[1])) for t in tokens]
            for tokens in ham_samples_nltk_tagged
        ]

        ## Lemmatization with POS
        spam_samples = [
            [self._nltk_pos_lemmatizer(w, t).lower() for w, t in tokens]
            for tokens in spam_samples
        ]
        ham_samples = [
            [self._nltk_pos_lemmatizer(w, t).lower() for w, t in tokens]
            for tokens in ham_samples
        ]

        ## Filter out small words
        spam_samples = [
            [w for w in tokens if len(w) > self.m] for tokens in spam_samples
        ]
        ham_samples = [[w for w in tokens if len(w) > self.m] for tokens in ham_samples]

        # print(f'{spam_samples}')
        # print(f'{ham_samples}')

        # compute_likelihood
        self.likelihood_spam = self._compute_likelihood(spam_samples)
        self.num_spam_messages = len(spam_samples)
        self.likelihood_ham = self._compute_likelihood(ham_samples)
        self.num_ham_messages = len(ham_samples)

        # print(f'{self.likelihood_spam}')
        # print(f'{self.likelihood_ham}')

    def predict(self, txt):
        # Pre-process text (similar to the train)
        if txt is not None:
            tokens = nltk.pos_tag(nltk.word_tokenize(txt))
            tokens = [(t[0], self._nltk_pos_tagger(t[1])) for t in tokens]
            tokens = [self._nltk_pos_lemmatizer(w, t).lower() for w, t in tokens]
            tokens = [w for w in tokens if len(w) > self.m]
            # tokens = [self.lemmatizer.lemmatize(w).lower() for w in tokens if len(self.lemmatizer.lemmatize(w)) > 2]
        else:
            tokens = []
        # print(tokens)

        log_p_spam = math.log(self.ps)
        log_p_ham = math.log(self.ph)

        for t in tokens:
            log_p_spam += math.log(self._p_word_spam(t))
            log_p_ham += math.log(self._p_word_ham(t))

        try:
            prob_spam = 1 / (1 + math.exp(log_p_ham - log_p_spam))
        except OverflowError:
            prob_spam = 0.0
        
        return ('spam', prob_spam) if prob_spam >= 0.5 else ('ham', prob_spam)

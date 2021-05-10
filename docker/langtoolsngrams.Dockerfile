FROM silviof/docker-languagetool:latest@sha256:7337f7ec954e1e4302866c788ebf9049cf3a081ad069ab42a77a42d5dd996369

RUN mkdir /ngrams && wget https://languagetool.org/download/ngram-data/ngrams-en-20150817.zip \
    && (cd ngrams && unzip ../ngrams-en-20150817.zip) \
    && rm -f ngrams-en-20150817.zi
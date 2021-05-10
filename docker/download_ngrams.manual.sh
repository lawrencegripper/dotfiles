#!/bin/bash
mkdir $HOME/lanagugetools/ngrams
wget https://languagetool.org/download/ngram-data/ngrams-en-20150817.zip
(cd ngrams && unzip ../ngrams-en-20150817.zip)
rm -f ngrams-en-20150817.zip
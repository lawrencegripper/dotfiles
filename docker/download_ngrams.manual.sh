#!/bin/bash
mkdir -p $HOME/lanagugetools/ngrams
cd $HOME/lanagugetools/ngrams
wget --inet4-only https://languagetool.org/download/ngram-data/ngrams-en-20150817.zip
unzip ./ngrams-en-20150817.zip
#rm -f ngrams-en-20150817.zip
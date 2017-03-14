#!/bin/sh

./nltk-trainer-master/train_classifier.py ./data/comments --instances files --fraction 0.66 --classifier NaiveBayes --ngrams 1 2 --max_feats 1000 --show-most-informative 10 --filter-stopwords english --score_fn likelihood_ratio --filename ./comments_NaiveBayes.pickle 2>&1 > comments_NaiveBayes.out
./nltk-trainer-master/train_classifier.py ./data/comments --instances files --fraction 0.66 --classifier DecisionTree --ngrams 1 2 --max_feats 1000 --show-most-informative 10 --filter-stopwords english --score_fn likelihood_ratio --filename ./comments_DecisionTree.pickle 2>&1 > comments_DecisionTree.out

./nltk-trainer-master/train_classifier.py ./data/patches --instances files --fraction 0.66 --classifier NaiveBayes --ngrams 1 2 --max_feats 1000 --show-most-informative 10 --filter-stopwords english --score_fn likelihood_ratio --filename ./patches_NaiveBayes.pickle 2>&1 > patches_NaiveBayes.out
./nltk-trainer-master/train_classifier.py ./data/patches --instances files --fraction 0.66 --classifier DecisionTree --ngrams 1 2 --max_feats 1000 --show-most-informative 10 --filter-stopwords english --score_fn likelihood_ratio --filename ./patches_DecisionTree.pickle 2>&1 > patches_DecisionTree.out


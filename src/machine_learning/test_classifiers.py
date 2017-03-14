import pickle, functools, operator
from nltk.util import ngrams
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize

txt_test_vuln = "+++ // avoid possible buffer overflow that would allow a remote attacker ..."
txt_test_bug = "+++ // fix for showing calculation results in a better, more readalbe way ..."
max_ngrams = 2

for classifier in ("./comments_NaiveBayes.pickle", "./comments_DecisionTree.pickle", "./patches_NaiveBayes.pickle", "./patches_DecisionTree.pickle"):

	_classifier = pickle.load(open(classifier))

	words = wordpunct_tokenize(txt_test_vuln)
	stopset = set(stopwords.words("english"))
	words = [w.lower() for w in words if w.lower() not in stopset]
	feats = dict([(word, True) for word in words + ngrams(words, max_ngrams)])
	print "classifier: " + classifier
	print "############################################################"
	print "words: " + str(words)
	print "feats: " + str(feats)
	print "classified as: " + _classifier.classify(feats)
	print
	words = wordpunct_tokenize(txt_test_bug)
	stopset = set(stopwords.words("english"))
	words = [w.lower() for w in words if w.lower() not in stopset]
	feats = dict([(word, True) for word in words + ngrams(words, max_ngrams)])
	print "words: " + str(words)
	print "feats: " + str(feats)
	print "classified as: " + _classifier.classify(feats)
	print




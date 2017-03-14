import urllib2
import re
import os

ftmp = open('./dict.txt.tmp', 'w+')

##
## Glossaries
##

###############################################################################
FILTER = '([^<]+)'
###############################################################################
f = urllib2.urlopen('http://www.pgp.net/pgpnet/pgp-faq/pgp-faq-glossary.html')
html = f.read()
for match in re.finditer('><b>' + FILTER + '</b></a>', html):
    for tmp in match.groups():
        print >> ftmp, tmp.lower()
f.close()
ftmp.flush()
os.system('wc -l ./dict.txt.tmp')

###############################################################################
f = urllib2.urlopen('http://cryptnet.net/fdp/crypto/crypto-dict/en/crypto-dict.html')
html = f.read()
for match in re.finditer('<dt>' + FILTER + '</dt><dd><p>', html):
    for tmp in match.groups():
        print >> ftmp, tmp.lower()
f.close()
ftmp.flush()
os.system('wc -l ./dict.txt.tmp')

###############################################################################
f = urllib2.urlopen('http://www.ciphersbyritter.com/GLOSSARY.HTM')
html = f.read()
for match in re.finditer('<NOBR>' + FILTER + '</NOBR>', html):
    for tmp in match.groups():
        print >> ftmp, tmp.lower()
f.close()
ftmp.flush()
os.system('wc -l ./dict.txt.tmp')

###############################################################################
f = urllib2.urlopen('https://en.wikipedia.org/wiki/Outline_of_cryptography')
html = f.read()
for match in re.finditer('<li><a href.*?>' + FILTER + '</a>', html):
    for tmp in match.groups():
        print >> ftmp, tmp.lower()
f.close()
ftmp.flush()
os.system('wc -l ./dict.txt.tmp')


##
## OpenSSL
##

###############################################################################
FILTER = '<b>([a-zA-Z0-9_\.\-]+)</b>'
###############################################################################
f = urllib2.urlopen('https://www.openssl.org/docs/ssl/ssl.html')
html = f.read()
for match in re.finditer(FILTER, html):
    for tmp in match.groups():
        print >> ftmp, tmp.lower()
f.close()
ftmp.flush()
os.system('wc -l ./dict.txt.tmp')

###############################################################################
FILTER = '\s+\**([a-zA-Z0-9_\.\-]+)\('
###############################################################################
f = urllib2.urlopen('https://www.openssl.org/docs/crypto/rsa.html')
html = f.read()
for match in re.finditer(FILTER, html):
    for tmp in match.groups():
        print >> ftmp, tmp.lower()
f.close()
ftmp.flush()
os.system('wc -l ./dict.txt.tmp')

###############################################################################
f = urllib2.urlopen('https://www.openssl.org/docs/crypto/dsa.html')
html = f.read()
for match in re.finditer(FILTER, html):
    for tmp in match.groups():
        print >> ftmp, tmp.lower()
f.close()
ftmp.flush()
os.system('wc -l ./dict.txt.tmp')

###############################################################################
f = urllib2.urlopen('https://www.openssl.org/docs/crypto/hmac.html')
html = f.read()
for match in re.finditer(FILTER, html):
    for tmp in match.groups():
        print >> ftmp, tmp.lower()
f.close()
ftmp.flush()
os.system('wc -l ./dict.txt.tmp')

###############################################################################
f = urllib2.urlopen('https://www.openssl.org/docs/crypto/pem.html')
html = f.read()
for match in re.finditer(FILTER, html):
    for tmp in match.groups():
        print >> ftmp, tmp.lower()
f.close()
ftmp.flush()
os.system('wc -l ./dict.txt.tmp')


##
## Bouncy Castle
##

###############################################################################
FILTER = '">([a-zA-Z0-9_\-\.]+)</a></li>'
###############################################################################
f = urllib2.urlopen('https://www.bouncycastle.org/docs/docs1.5on/allclasses-frame.html')
html = f.read()
for match in re.finditer(FILTER, html):
    for tmp in match.groups():
        print >> ftmp, tmp.lower()
f.close()
ftmp.flush()
os.system('wc -l ./dict.txt.tmp')


##
## PHP
##

###############################################################################
FILTER = '(openssl_[a-zA-Z0-9_\.\-]+)'
###############################################################################
f = urllib2.urlopen('http://php.net/manual/en/ref.openssl.php')
html = f.read()
for match in re.finditer(FILTER, html):
    for tmp in match.groups():
        print >> ftmp, tmp.lower()
f.close()
ftmp.flush()
os.system('wc -l ./dict.txt.tmp')

##
## Constants
##

###############################################################################
FILTER = '(0[xX][a-fA-F0-9]{4,})'
###############################################################################
f = urllib2.urlopen('https://raw.githubusercontent.com/vlad902/findcrypt2-with-mmx/master/findcrypt2-with-mmx/consts.cpp')
html = f.read()
for match in re.finditer(FILTER, html):
    for tmp in match.groups():
        print >> ftmp, tmp.lower()
f.close()
ftmp.flush()
os.system('wc -l ./dict.txt.tmp')



###############################################################################
ftmp.close()
os.system('cat ./dict.txt.tmp | sort | uniq > ./dict.txt.raw')
os.system('/bin/rm ./dict.txt.tmp')
os.system('wc -l ./dict.txt.raw')


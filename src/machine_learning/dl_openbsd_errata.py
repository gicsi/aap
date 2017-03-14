import urllib2
import re
import os
import time


errata_url = 'http://www.openbsd.org/errataNN.html'

###############################################################################

bug_count = 0;
vuln_count = 0;

started = time.strftime("%c")
print "started: " + started

for pp in range(22, 58):

    url_pp = errata_url.replace("NN", str(pp))
    print url_pp
    f = urllib2.urlopen(url_pp)
    html = f.read()
    f.close()

    for match in re.finditer("<li id=\"(\w+)\".*?<strong>(.*?)</strong>.*?<br>\s+(.*?)\s+<p>", html, re.DOTALL):

        (txt_id, crit, txt) = match.groups()
        print "Bug # " + txt_id + "..."
        print "#/type/date: " + crit

        fn1 = None
        fn2 = None
        if crit.find("SECURITY FIX") >= 0:
            vuln_count = vuln_count + 1
            fn1 = './data/comments/vuln/ob_' + str(vuln_count)
            patch_url = ""
            for match2 in re.finditer("<a href=\"(.*\.patch.*?)\">", txt):
                patch_url = match2.groups()[0]
            if patch_url:
                fn2 = './data/patches/vuln/ob_' + str(vuln_count)
        else:
            bug_count = bug_count + 1
            fn1 = './data/comments/bug/ob_' + str(bug_count)
            patch_url = ""
            for match2 in re.finditer("<a href=\"(.*\.patch.*?)\">", txt):
                patch_url = match2.groups()[0]
            if patch_url:
                fn2 = './data/patches/bug/ob_' + str(vuln_count)

        if fn1:
            ftmp = open(fn1, 'a+')
            print >> ftmp, txt
            ftmp.close()
        if fn2:
            f2 = urllib2.urlopen(patch_url)
            patch = f2.read()
            f2.close()
            if ("+++ " in patch or "--- " in patch) and "@@ " in patch: # xxx
                ftmp = open(fn2, 'a+')
                print >> ftmp, patch
                ftmp.close()

ended = time.strftime("%c")
print "started: " + started
print "ended: " + ended
print
print "total bug count: " + str(bug_count)
print "total vuln count: " + str(vuln_count)
print "total count: " + str(bug_count + vuln_count)
print




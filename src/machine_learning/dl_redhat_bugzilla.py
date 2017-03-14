import urllib2
import re
import os
import time
from xml.dom import minidom


rh_list_url = 'https://bugzilla.redhat.com/buglist.cgi?bug_status=CLOSED&f1=attachments.ispatch&order=bug_id%20DESC&query_based_on=&query_format=advanced'
rh_det_url = 'https://bugzilla.redhat.com/show_bug.cgi?ctype=xml&id='
rh_list_filter = 'href="show\_bug\.cgi\?id\=(\d+)">\d+<\/a>'


###############################################################################


def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

bug_count = 0;
vuln_count = 0;

started = time.strftime("%c")
print "started: " + started

f = urllib2.urlopen(rh_list_url)
html = f.read()
f.close()
for match in re.finditer(rh_list_filter, html):
    for bug_id in match.groups():
        
        print "Bug # " + bug_id + "..."
        f2 = urllib2.urlopen(rh_det_url + bug_id)
        xml = f2.read()
        f2.close

        parsed = minidom.parseString(xml)

        priority = getText(parsed.getElementsByTagName("priority")[0].childNodes)
        bug_severity = getText(parsed.getElementsByTagName("bug_severity")[0].childNodes)
        print "priority: " + priority + " / bug_severity: " + bug_severity

        fn1 = None
        fn2 = None
        if priority == "urgent" or bug_severity == "urgent" or priority == "high" or bug_severity == "high": # xxx
            vuln_count = vuln_count + 1
            fn1 = './data/comments/vuln/rh_' + str(vuln_count)
            try:
                getText(parsed.getElementsByTagName("data")[0].childNodes)
                fn2 = './data/patches/vuln/rh_' + str(vuln_count)
            except:
                pass
        else:
            bug_count = bug_count + 1
            fn1 = './data/comments/bug/rh_' + str(bug_count)
            try:
                getText(parsed.getElementsByTagName("data")[0].childNodes)
                fn2 = './data/patches/bug/rh_' + str(bug_count)
            except:
                pass

        if fn1:
            for thetext in parsed.getElementsByTagName("thetext"):
                comment = getText(thetext.childNodes).encode('utf-8').strip()
                if comment != '': # xxx
                    ftmp = open(fn1, 'a+')
                    print >> ftmp, comment
                    ftmp.close()
        if fn2:
            for data in parsed.getElementsByTagName("data"):
                patch = getText(data.childNodes).decode('base64', 'strict')
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


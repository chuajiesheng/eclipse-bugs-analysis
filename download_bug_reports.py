import urllib2
import sys
import time

START = 193701
STOP = 491000
# STOP = 194000
STEP = 100

URL = 'https://bugs.eclipse.org/bugs/show_bug.cgi'
CONTENT_TYPE = 'application/x-www-form-urlencoded'

PRE_BODY = 'ctype=xml'
POST_BODY = 'excludefield=attachmentdata'

FILENAME = 'data/huge-eclipse-xml-reports/bugs{}-{}.xml'

for i in range(START, STOP, STEP):
    ids = 'id=' + '&id='.join([str(x) for x in range(i, i + STEP, 1)])
    data = PRE_BODY + '&' + ids + '&' + POST_BODY

    req = urllib2.Request(URL, data)
    response = urllib2.urlopen(req)

    f = open(FILENAME.format(str(i), str(i + STEP - 1)), 'w+')
    f.write(response.read())

    sys.stdout.write('.')
    sys.stdout.flush()

    time.sleep(5)

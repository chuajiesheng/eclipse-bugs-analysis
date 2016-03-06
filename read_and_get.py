import sys
import urllib
import csv


def download_bug(id):
    url = 'https://bugs.eclipse.org/bugs/show_bug.cgi?ctype=xml&id=%s' % id
    filename = 'eclipse-bug-reports/%s.xml' % id
    print 'Downloading', url, 'into', filename
    urllib.urlretrieve (url, filename)


def main():
    input_file = sys.argv[1]
    print 'Reading', input_file

    with open(input_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            bug_id = row['Bug ID']
            download_bug(bug_id)


if __name__ == '__main__':
    main()

from os import listdir
from os.path import isfile, join
from xml.dom import minidom
from xml import parsers
import threading
import bug
import sys
import numpy as np
import scipy.sparse as sps

DATA_DIRECTORY = 'data/huge-eclipse-xml-reports'
bugs = []

class NodeUtil:
    @staticmethod
    def getText(nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)


def parse_file(file_path):
    xmldoc = None

    try:
        xmldoc = minidom.parse(file_path)
    except parsers.expat.ExpatError as e:
        str = '{} - {}'.format(file_path, e)
        print >> sys.stderr, str
        return

    itemlist = xmldoc.getElementsByTagName('bug')
    for item in itemlist:
        b = bug.Bug(item)
        if b is not None:
            bugs.append(b)
            # print b.to_csv()
            # print b.to_short_desc_csv()


def multithread_parse_file(file_path):
    t = threading.Thread(target=parse_file, args=(file_path,))
    t.start()


if __name__ == '__main__':
    files = [f for f in listdir(DATA_DIRECTORY) if isfile(join(DATA_DIRECTORY, f))]
    files = ['bugs000101-000200.xml']
    for f in files:
        file_path = join(DATA_DIRECTORY, f)
        parse_file(file_path)

    # row = all bugs length
    # column = features
    features = sps.lil_matrix((len(bugs), 43), dtype=np.longdouble)

    bug_severity_list = [(b.bug_severity, b.creation_ts) for b in bugs]

    for i in range(len(bugs)):
        print 'processing', i, 'of', len(bugs)
        col_index = 0
        b = bugs[i]

        features[i, col_index] = b.num_of_comments(5)
        col_index += 1

        features[i, col_index] = b.num_of_bugs(bug_severity_list, 7)
        col_index += 1

        features[i, col_index] = b.num_of_bugs_with_severity(bug_severity_list, 7)
        col_index += 1

        features[i, col_index] = b.num_of_bugs_with_same_or_higher_severity(bug_severity_list, 5)
        col_index += 1

        # TODO: Textual Factor

        features[i, col_index] = b.mean_priority_of_author(bugs)
        col_index += 1

        features[i, col_index] = b.median_priority_of_author(bugs)
        col_index += 1

        features[i, col_index] = b.mean_priority_of_bug_by_author_prior(bugs)
        col_index += 1

        features[i, col_index] = b.median_priority_of_bug_by_author_prior(bugs)
        col_index += 1

        features[i, col_index] = b.num_of_bug_by_author_prior(bugs)
        col_index += 1

        features[i, col_index + b.os()] = 1
        col_index += len(bug.Bug.OS_SYS) + 1

        # TODO: cosine similarity

        features[i, col_index] = b.mean_priority_of_top20
        col_index += 1

        features[i, col_index] = b.median_priority_of_top20
        col_index += 1

        features[i, col_index] = b.mean_priority_of_top10
        col_index += 1

        features[i, col_index] = b.median_priority_of_top10
        col_index += 1

        features[i, col_index] = b.mean_priority_of_top5
        col_index += 1

        features[i, col_index] = b.median_priority_of_top5
        col_index += 1

        features[i, col_index] = b.mean_priority_of_top3
        col_index += 1

        features[i, col_index] = b.median_priority_of_top3
        col_index += 1

        features[i, col_index] = b.mean_priority_of_top1
        col_index += 1

        features[i, col_index] = b.median_priority_of_top1
        col_index += 1

        # TODO: end cosine similarity

        features[i, col_index + b.severity_index()] = 1
        col_index += len(bug.Bug.SEVERITY_LIST) + 1

        features[i, col_index + b.product_feature()] = 1
        col_index += len(bug.Bug.PRODUCTS) + 1

        features[i, col_index] = b.num_of_bug_for_same_product_prior(bugs)
        col_index += 1

        features[i, col_index] = b.num_of_bug_for_same_product_and_severity_prior(bugs)
        col_index += 1

        features[i, col_index] = b.num_of_bug_for_same_product_and_same_or_higher_severity_prior(bugs)
        col_index += 1

        features[i, col_index] = b.pro_of_p1_bug_with_same_priority_and_prior(bugs)
        col_index += 1

        features[i, col_index] = b.pro_of_p2_bug_with_same_priority_and_prior(bugs)
        col_index += 1

        features[i, col_index] = b.pro_of_p3_bug_with_same_priority_and_prior(bugs)
        col_index += 1

        features[i, col_index] = b.pro_of_p4_bug_with_same_priority_and_prior(bugs)
        col_index += 1

        features[i, col_index] = b.pro_of_p5_bug_with_same_priority_and_prior(bugs)
        col_index += 1

        features[i, col_index] = b.mean_priority_of_bug_for_same_product_prior(bugs)
        col_index += 1

        features[i, col_index] = b.median_priority_of_bug_for_same_product_prior(bugs)
        col_index += 1

        features[i, col_index + b.component_feature()] = 1
        col_index += len(bug.Bug.COMPONENTS) + 1

        features[i, col_index] = b.num_of_bug_for_same_component_prior(bugs)
        col_index += 1

        features[i, col_index] = b.num_of_bug_for_same_component_and_severity_prior(bugs)
        col_index += 1

        features[i, col_index] = b.num_of_bug_for_same_component_and_same_or_higher_severity_prior(bugs)
        col_index += 1

        features[i, col_index] = b.pro_of_p1_bug_with_same_priority_and_prior_for_component(bugs)
        col_index += 1

        features[i, col_index] = b.pro_of_p2_bug_with_same_priority_and_prior_for_component(bugs)
        col_index += 1

        features[i, col_index] = b.pro_of_p3_bug_with_same_priority_and_prior_for_component(bugs)
        col_index += 1

        features[i, col_index] = b.pro_of_p4_bug_with_same_priority_and_prior_for_component(bugs)
        col_index += 1

        features[i, col_index] = b.pro_of_p5_bug_with_same_priority_and_prior_for_component(bugs)
        col_index += 1

        features[i, col_index] = b.mean_priority_of_bug_for_same_component_prior(bugs)
        col_index += 1

        features[i, col_index] = b.median_priority_of_bug_for_same_component_prior(bugs)
        col_index += 1

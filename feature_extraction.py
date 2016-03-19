from os import listdir
from os.path import isfile, join
from xml.dom import minidom
from xml import parsers
import threading
import bug
import sys
import numpy as np
import scipy.sparse as sps
import code
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
        if b is not None and not b.error:
            bugs.append(b)
            # print b.to_csv()
            # print b.to_short_desc_csv()


def multithread_parse_file(file_path):
    t = threading.Thread(target=parse_file, args=(file_path,))
    t.start()


if __name__ == '__main__':
    files = [f for f in listdir(DATA_DIRECTORY) if isfile(join(DATA_DIRECTORY, f))]
    # files = ['bugs000001-000100.xml']
    for f in files:
        print 'read', f
        file_path = join(DATA_DIRECTORY, f)
        parse_file(file_path)

    print 'parse completed'

    documents = [item.to_short_desc() for item in bugs]
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

    # row = all bugs length
    # column = features
    columns = 52 + len(bug.Bug.OS_SYS) + len(bug.Bug.SEVERITY_LIST) + len(bug.Bug.PRODUCTS) + len(bug.Bug.COMPONENTS)
    features = sps.lil_matrix((len(bugs), columns), dtype=np.longdouble)

    bug_severity_list = [(b.bug_severity, b.creation_ts) for b in bugs]

    for i in range(len(bugs)):
        print 'processing', i, 'of', len(bugs)
        col_index = 0
        b = bugs[i]

        features[i, col_index] = b.num_of_comments(5)
        col_index += 1

        days_before = 7
        features[i, col_index] = b.num_of_bugs(bug_severity_list, days_before)
        col_index += 1
        features[i, col_index] = b.num_of_bugs_with_severity(bug_severity_list, days_before)
        col_index += 1
        features[i, col_index] = b.num_of_bugs_with_same_or_higher_severity(bug_severity_list, days_before)
        col_index += 1

        days_before = 30
        features[i, col_index] = b.num_of_bugs(bug_severity_list, days_before)
        col_index += 1
        features[i, col_index] = b.num_of_bugs_with_severity(bug_severity_list, days_before)
        col_index += 1
        features[i, col_index] = b.num_of_bugs_with_same_or_higher_severity(bug_severity_list, days_before)
        col_index += 1

        days_before = 1
        features[i, col_index] = b.num_of_bugs(bug_severity_list, days_before)
        col_index += 1
        features[i, col_index] = b.num_of_bugs_with_severity(bug_severity_list, days_before)
        col_index += 1
        features[i, col_index] = b.num_of_bugs_with_same_or_higher_severity(bug_severity_list, days_before)
        col_index += 1

        days_before = 3
        features[i, col_index] = b.num_of_bugs(bug_severity_list, days_before)
        col_index += 1
        features[i, col_index] = b.num_of_bugs_with_severity(bug_severity_list, days_before)
        col_index += 1
        features[i, col_index] = b.num_of_bugs_with_same_or_higher_severity(bug_severity_list, days_before)
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

        cosine_similarities = cosine_similarity(tfidf_matrix[i:i+1], tfidf_matrix).flatten()
        related_docs_indices = cosine_similarities.argsort()[:-21:-1]
        priorities = [bugs[item].translated_priority() for item in related_docs_indices]
        b.mean_priority_of_top20 = np.mean(np.array(priorities))
        b.median_priority_of_top20 = np.median(np.array(priorities))

        related_docs_indices = cosine_similarities.argsort()[:-11:-1]
        priorities = [bugs[item].translated_priority() for item in related_docs_indices]
        b.mean_priority_of_top10 = np.mean(np.array(priorities))
        b.median_priority_of_top10 = np.median(np.array(priorities))

        related_docs_indices = cosine_similarities.argsort()[:-6:-1]
        priorities = [bugs[item].translated_priority() for item in related_docs_indices]
        b.mean_priority_of_top5 = np.mean(np.array(priorities))
        b.median_priority_of_top5 = np.median(np.array(priorities))

        related_docs_indices = cosine_similarities.argsort()[:-4:-1]
        priorities = [bugs[item].translated_priority() for item in related_docs_indices]
        b.mean_priority_of_top3 = np.mean(np.array(priorities))
        b.median_priority_of_top3 = np.median(np.array(priorities))

        related_docs_indices = cosine_similarities.argsort()[:-2:-1]
        priorities = [bugs[item].translated_priority() for item in related_docs_indices]
        b.mean_priority_of_top1 = np.mean(np.array(priorities))
        b.median_priority_of_top1 = np.median(np.array(priorities))

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

    # code.interact(local=locals())
    output_file = open('features.txt', 'w')

    for i in range(features.shape[0]):
        output_file.write('{} '.format(bugs[i].translated_priority()))
        for j in range(features.shape[1]):
            output_file.write('{}:{} '.format(j, features[i, j]))
        output_file.write('\n')

from os import listdir
from os.path import isfile, join
from xml.dom import minidom
from xml import parsers
from multiprocessing import Process
import threading
import bug
import sys
import numpy as np
import scipy.sparse as sps
import code
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sets import Set

DATA_DIRECTORY = 'data/huge-eclipse-xml-reports'
run_id = '20160320-0057'
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


def compute_feature(all_bugs, features, row, current_bug, bug_severity_list, tfidf_matrix):
    col_index = 0

    features[row, col_index] = current_bug.num_of_comments(5)
    col_index += 1

    days_before = 7
    features[row, col_index] = current_bug.num_of_bugs(bug_severity_list, days_before)
    col_index += 1
    features[row, col_index] = current_bug.num_of_bugs_with_severity(bug_severity_list, days_before)
    col_index += 1
    features[row, col_index] = current_bug.num_of_bugs_with_same_or_higher_severity(bug_severity_list, days_before)
    col_index += 1

    days_before = 30
    features[row, col_index] = current_bug.num_of_bugs(bug_severity_list, days_before)
    col_index += 1
    features[row, col_index] = current_bug.num_of_bugs_with_severity(bug_severity_list, days_before)
    col_index += 1
    features[row, col_index] = current_bug.num_of_bugs_with_same_or_higher_severity(bug_severity_list, days_before)
    col_index += 1

    days_before = 1
    features[row, col_index] = current_bug.num_of_bugs(bug_severity_list, days_before)
    col_index += 1
    features[row, col_index] = current_bug.num_of_bugs_with_severity(bug_severity_list, days_before)
    col_index += 1
    features[row, col_index] = current_bug.num_of_bugs_with_same_or_higher_severity(bug_severity_list, days_before)
    col_index += 1

    days_before = 3
    features[row, col_index] = current_bug.num_of_bugs(bug_severity_list, days_before)
    col_index += 1
    features[row, col_index] = current_bug.num_of_bugs_with_severity(bug_severity_list, days_before)
    col_index += 1
    features[row, col_index] = current_bug.num_of_bugs_with_same_or_higher_severity(bug_severity_list, days_before)
    col_index += 1

    # TODO: Textual Factor

    features[row, col_index] = current_bug.mean_priority_of_author(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.median_priority_of_author(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.mean_priority_of_bug_by_author_prior(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.median_priority_of_bug_by_author_prior(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.num_of_bug_by_author_prior(all_bugs)
    col_index += 1

    features[row, col_index + current_bug.os()] = 1
    col_index += len(bug.Bug.OS_SYS) + 1

    cosine_similarities = cosine_similarity(tfidf_matrix[row:row + 1], tfidf_matrix).flatten()
    related_docs_indices = cosine_similarities.argsort()[:-21:-1]
    priorities = [all_bugs[item].translated_priority() for item in related_docs_indices]
    current_bug.mean_priority_of_top20 = np.mean(np.array(priorities))
    current_bug.median_priority_of_top20 = np.median(np.array(priorities))

    related_docs_indices = cosine_similarities.argsort()[:-11:-1]
    priorities = [all_bugs[item].translated_priority() for item in related_docs_indices]
    current_bug.mean_priority_of_top10 = np.mean(np.array(priorities))
    current_bug.median_priority_of_top10 = np.median(np.array(priorities))

    related_docs_indices = cosine_similarities.argsort()[:-6:-1]
    priorities = [all_bugs[item].translated_priority() for item in related_docs_indices]
    current_bug.mean_priority_of_top5 = np.mean(np.array(priorities))
    current_bug.median_priority_of_top5 = np.median(np.array(priorities))

    related_docs_indices = cosine_similarities.argsort()[:-4:-1]
    priorities = [all_bugs[item].translated_priority() for item in related_docs_indices]
    current_bug.mean_priority_of_top3 = np.mean(np.array(priorities))
    current_bug.median_priority_of_top3 = np.median(np.array(priorities))

    related_docs_indices = cosine_similarities.argsort()[:-2:-1]
    priorities = [all_bugs[item].translated_priority() for item in related_docs_indices]
    current_bug.mean_priority_of_top1 = np.mean(np.array(priorities))
    current_bug.median_priority_of_top1 = np.median(np.array(priorities))

    features[row, col_index] = current_bug.mean_priority_of_top20
    col_index += 1

    features[row, col_index] = current_bug.median_priority_of_top20
    col_index += 1

    features[row, col_index] = current_bug.mean_priority_of_top10
    col_index += 1

    features[row, col_index] = current_bug.median_priority_of_top10
    col_index += 1

    features[row, col_index] = current_bug.mean_priority_of_top5
    col_index += 1

    features[row, col_index] = current_bug.median_priority_of_top5
    col_index += 1

    features[row, col_index] = current_bug.mean_priority_of_top3
    col_index += 1

    features[row, col_index] = current_bug.median_priority_of_top3
    col_index += 1

    features[row, col_index] = current_bug.mean_priority_of_top1
    col_index += 1

    features[row, col_index] = current_bug.median_priority_of_top1
    col_index += 1

    features[row, col_index + current_bug.severity_index()] = 1
    col_index += len(bug.Bug.SEVERITY_LIST) + 1

    features[row, col_index + current_bug.product_feature()] = 1
    col_index += len(bug.Bug.PRODUCTS) + 1

    features[row, col_index] = current_bug.num_of_bug_for_same_product_prior(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.num_of_bug_for_same_product_and_severity_prior(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.num_of_bug_for_same_product_and_same_or_higher_severity_prior(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.pro_of_p1_bug_with_same_priority_and_prior(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.pro_of_p2_bug_with_same_priority_and_prior(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.pro_of_p3_bug_with_same_priority_and_prior(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.pro_of_p4_bug_with_same_priority_and_prior(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.pro_of_p5_bug_with_same_priority_and_prior(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.mean_priority_of_bug_for_same_product_prior(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.median_priority_of_bug_for_same_product_prior(all_bugs)
    col_index += 1

    features[row, col_index + current_bug.component_feature()] = 1
    col_index += len(bug.Bug.COMPONENTS) + 1

    features[row, col_index] = current_bug.num_of_bug_for_same_component_prior(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.num_of_bug_for_same_component_and_severity_prior(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.num_of_bug_for_same_component_and_same_or_higher_severity_prior(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.pro_of_p1_bug_with_same_priority_and_prior_for_component(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.pro_of_p2_bug_with_same_priority_and_prior_for_component(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.pro_of_p3_bug_with_same_priority_and_prior_for_component(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.pro_of_p4_bug_with_same_priority_and_prior_for_component(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.pro_of_p5_bug_with_same_priority_and_prior_for_component(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.mean_priority_of_bug_for_same_component_prior(all_bugs)
    col_index += 1

    features[row, col_index] = current_bug.median_priority_of_bug_for_same_component_prior(all_bugs)
    col_index += 1


def process_feature(start, end):
    print 'process_feature', start, 'to', end
    documents = [item.to_short_desc() for item in bugs]
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

    # row = all bugs length
    # column = features
    columns = 52 + len(bug.Bug.OS_SYS) + len(bug.Bug.SEVERITY_LIST) + len(bug.Bug.PRODUCTS) + len(bug.Bug.COMPONENTS)
    features = sps.lil_matrix((len(bugs), columns), dtype=np.longdouble)

    bug_severity_list = [(b.bug_severity, b.creation_ts) for b in bugs]
    output_file = open('run/features_{}_{}to{}.txt'.format(run_id, start, end), 'w')

    for i in range(start, end):
        print 'processing\t\t{} to\t{}'.format(i, end),
        # print 'processing\t', i, '\tto', len(bugs),
        b = bugs[i]
        compute_feature(bugs, features, i, b, bug_severity_list, tfidf_matrix)

        output_file.write('{} '.format(bugs[i].translated_priority()))
        for j in range(features.shape[1]):
            output_file.write('{}:{} '.format(j, features[i, j]))
        output_file.write('\n')
        print '\tprinted'

    print 'run {}\t{} to\t{}\tcompleted'.format(run_id, start, end)


def generate_stats(bugs):
    priorities = {
        'P1': 0,
        'P2': 0,
        'P3': 0,
        'P4': 0,
        'P5': 0,
    }

    for b in bugs:
        priorities[b.priority] += 1

    output_file = open('run/all_bugs_stats.txt', 'w')
    output_file.write(str(priorities))
    output_file.write('\n')
    output_file.close()

    print priorities


def get_all_assigned_to(bugs):
    s = Set()

    for b in bugs:
        person = b.assigned_to
        if person is not None:
            s.add(person)

    return sorted(list(s))


def generate_assigned_to(people):
    with open('run/assigned_to_people_index.txt', 'w') as f:
        for i, v in enumerate(people):
            index = i + 1
            f.write('{}, {}\n'.format(str(index), v))


def generate_bugs_assigned_to(people, bugs):
    with open('run/bugs_assigned_to.txt', 'w') as f:
        for i, b in enumerate(bugs):
            b_index = i + 1
            v_index = people.index(b.assigned_to)
            f.write('{}, {}\n'.format(str(b_index), str(v_index)))

if __name__ == '__main__':
    files = [f for f in listdir(DATA_DIRECTORY) if isfile(join(DATA_DIRECTORY, f))]
    # files = ['bugs000001-000100.xml']
    files = sorted(files)

    for f in files:
        print 'read', f
        file_path = join(DATA_DIRECTORY, f)
        parse_file(file_path)

    print 'parse completed'

    generate_stats(bugs)
    print 'stats generated'

    all_assigned_to_users = get_all_assigned_to(bugs)
    generate_assigned_to(all_assigned_to_users)
    generate_bugs_assigned_to(all_assigned_to_users, bugs)

    start = 0
    step = 15000
    end = len(bugs)

    p = None
    for start_point in range(start, end, step):
        end_point = start_point + step
        if end_point > len(bugs):
            end_point = len(bugs)

        p = Process(target=process_feature, args=(start_point, end_point))
        p.start()

    if p is not None:
        p.join()






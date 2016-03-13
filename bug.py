from dateutil.parser import parse
import string
from feature_extraction import NodeUtil
from long_desc import LongDesc
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import numpy


class Bug(object):
    FIELDS = ['bug_id', 'creation_ts', 'short_desc', 'delta_ts', 'reporter_accessible', 'cclist_accessible',
              'classification_id', 'classification', 'product', 'component', 'version', 'rep_platform', 'op_sys',
              'bug_status', 'resolution', 'priority', 'bug_severity', 'target_milestone', 'blocked', 'dependson',
              'everconfirmed', 'reporter', 'assigned_to', 'cc', 'qa_contact', 'long_des']
    CSV_STRING = "{},{},\"{}\",{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}"
    SEVERITY_LIST = [
            'enhancement',
            'trivial',
            'minor',
            'normal',
            'major',
            'critical',
            'blocker',
        ]
    PRIORITIES = {'P1': 1, 'P2': 2, 'P3': 3, 'P4': 4, 'P5': 5, 'P6': 6}
    OS_SYS = {
        'AIX Motif': 1,
        'All': 2,
        'HP-UX': 3,
        'Linux': 4,
        'Linux-GTK': 5,
        'Linux-Motif': 6,
        'Mac OS X': 7,
        'Neutrino': 8,
        'None': 9,
        'other': 10,
        'Other': 10,
        'QNX-Photon': 11,
        'Solaris': 12,
        'Solaris-GTK': 13,
        'Solaris-Motif': 14,
        'SymbianOS-Series 80': 15,
        'Unix All': 16,
        'Windows 95': 17,
        'Windows 98': 18,
        'Windows 2000': 19,
        'Windows 2003 Server': 20,
        'Windows All': 21,
        'Windows CE': 22,
        'Windows ME': 23,
        'Windows Mobile 5.0': 24,
        'Windows Mobile 2003': 25,
        'Windows NT': 26,
        'Windows Vista': 27,
        'Windows Vista-WPF': 28,
        'Windows XP': 29

    }

    bug_id = None
    creation_ts = None
    short_desc = None
    delta_ts = None
    reporter_accessible = None
    cclist_accessible = None
    classification_id = None
    classification = None
    product = None
    component = None
    version = None
    rep_platform = None
    op_sys = None
    bug_status = None
    resolution = None
    priority = None
    bug_severity = None
    target_milestone = None
    blocked = []
    dependson = []
    everconfirmed = None
    reporter = None
    assigned_to = None
    cc = []
    qa_contact = None

    long_desc = []

    def __init__(self, item):
        if item is None:
            return None

        self.bug_id = NodeUtil.getText(item.getElementsByTagName('bug_id')[0].childNodes)

        if len(item.attributes) > 0 and 'error' in item.attributes.keys():
            error = item.attributes['error']
            if error is not None and (error.value == 'NotFound' or error.value == 'NotPermitted'):
                return None

        self.creation_ts = parse(NodeUtil.getText(item.getElementsByTagName('creation_ts')[0].childNodes))

        short_desc_element = item.getElementsByTagName('short_desc')
        if short_desc_element is not None and len(short_desc_element) > 0:
            self.short_desc = self.clean_string(NodeUtil.getText(short_desc_element[0].childNodes))

        self.delta_ts = parse(NodeUtil.getText(item.getElementsByTagName('delta_ts')[0].childNodes))
        self.reporter_accessible = NodeUtil.getText(item.getElementsByTagName('reporter_accessible')[0].childNodes)
        self.cclist_accessible = NodeUtil.getText(item.getElementsByTagName('cclist_accessible')[0].childNodes)
        self.classification_id = NodeUtil.getText(item.getElementsByTagName('classification_id')[0].childNodes)
        self.classification = NodeUtil.getText(item.getElementsByTagName('classification')[0].childNodes)
        self.product = NodeUtil.getText(item.getElementsByTagName('product')[0].childNodes)
        self.component = NodeUtil.getText(item.getElementsByTagName('component')[0].childNodes)
        self.version = NodeUtil.getText(item.getElementsByTagName('version')[0].childNodes)
        self.rep_platform = NodeUtil.getText(item.getElementsByTagName('rep_platform')[0].childNodes)
        self.op_sys = NodeUtil.getText(item.getElementsByTagName('op_sys')[0].childNodes)
        self.bug_status = NodeUtil.getText(item.getElementsByTagName('bug_status')[0].childNodes)

        resolution_element = item.getElementsByTagName('resolution')
        if resolution_element is not None and len(resolution_element) > 0:
            self.resolution = NodeUtil.getText(resolution_element[0].childNodes)

        self.priority = NodeUtil.getText(item.getElementsByTagName('priority')[0].childNodes)
        self.bug_severity = NodeUtil.getText(item.getElementsByTagName('bug_severity')[0].childNodes)
        self.target_milestone = NodeUtil.getText(item.getElementsByTagName('target_milestone')[0].childNodes)

        blocked_elements = item.getElementsByTagName('blocked')
        self.blocked = []
        if blocked_elements is not None and len(blocked_elements) > 0:
            for blocked_element in blocked_elements:
                self.blocked.append(NodeUtil.getText(blocked_element.childNodes))

        dependson_elements = item.getElementsByTagName('dependson')
        self.dependson = []
        if dependson_elements is not None and len(dependson_elements) > 0:
            for dependson_element in dependson_elements:
                self.dependson.append(NodeUtil.getText(dependson_element.childNodes))

        self.everconfirmed = NodeUtil.getText(item.getElementsByTagName('everconfirmed')[0].childNodes)
        self.reporter = NodeUtil.getText(item.getElementsByTagName('reporter')[0].childNodes)
        self.assigned_to = NodeUtil.getText(item.getElementsByTagName('assigned_to')[0].childNodes)

        cc_elements = item.getElementsByTagName('cc')
        if cc_elements is not None and len(cc_elements) > 0:
            self.cc = []
            for cc in cc_elements:
                self.cc.append(NodeUtil.getText(cc.childNodes))

        qa_contact_element = item.getElementsByTagName('qa_contact')
        if qa_contact_element is not None and len(qa_contact_element) > 0:
            self.qa_contact = NodeUtil.getText(qa_contact_element[0].childNodes)

        self.long_desc = []
        for desc in item.getElementsByTagName('long_desc'):
            self.long_desc.append(LongDesc(desc))

    def format_cc(self):
        return len(self.cc)

    def format_blocked(self):
        return len(self.blocked)

    def format_dependson(self):
        return len(self.dependson)

    def format_long_desc(self):
        length = len(self.long_desc)
        comments = [item for item in self.long_desc if self.within_day(self.creation_ts, parse(item.bug_when), 5)]
        if len(comments) == 0:
            return "{},{},{},{},".format(length, 0, 0, 0)

        all_bug_when_values = [parse(ld.bug_when) for ld in comments]
        all_bug_when_values.sort()

        longest_gap = (all_bug_when_values[-1] - self.creation_ts).total_seconds()
        total_gap = 0
        for bug_when in all_bug_when_values:
            total_gap += (bug_when - self.creation_ts).total_seconds()

        average_gap = total_gap / len(all_bug_when_values)

        str = "{},{},{},{},{}".format(length, total_gap, average_gap, longest_gap, self.num_of_comments(5))
        return str

    def csv_title(self):
        fields = self.FIELDS
        fields.extend(['total_gap', 'average_gap', 'longest_gap', '5_days_long_desc'])
        return fields.join(', ')

    @staticmethod
    def clean_string(str):
        if str is None:
            return ''

        printable = set(string.printable)
        return filter(lambda s: s in printable, str).replace(',', ';')

    def to_csv(self):
        creation_ts_strftime = self.creation_ts.strftime('%Y-%m-%d %H:%M:%S') if self.creation_ts is not None else None
        delta_ts_strftime = self.delta_ts.strftime('%Y-%m-%d %H:%M:%S') if self.delta_ts is not None else None
        return self.CSV_STRING.format(self.bug_id,
                                      creation_ts_strftime,
                                      self.clean_string(self.short_desc),
                                      delta_ts_strftime,
                                      self.reporter_accessible,
                                      self.cclist_accessible,
                                      self.classification_id,
                                      self.classification,
                                      self.product,
                                      self.component,
                                      self.version,
                                      self.rep_platform,
                                      self.op_sys,
                                      self.bug_status,
                                      self.resolution,
                                      self.priority,
                                      self.bug_severity,
                                      self.target_milestone,
                                      self.format_blocked(),
                                      self.format_dependson(),
                                      self.everconfirmed,
                                      self.reporter,
                                      self.assigned_to,
                                      self.format_cc(),
                                      self.qa_contact,
                                      self.format_long_desc())

    # # Temporal Factor
    # Resolution time of each bug (time difference between delta timestamp and creation timestamp)
    # Total time difference between each of the comments in the bug report
    # Mean time difference of the comments in the bug report
    # Number of comments within 5 days from reported date
    @staticmethod
    def within_day(start, end, num_of_days):
        ONE_DAY = 60 * 60 * 24
        diff_in_secs = (end - start).total_seconds()
        return abs(diff_in_secs) < (num_of_days * ONE_DAY)

    def num_of_comments(self, days):
        comments = [item for item in self.long_desc if self.within_day(self.creation_ts, parse(item.bug_when), days)]
        return len(comments)

    # Number of bugs reported within 7 days before the reporting of BR
    def num_of_bugs(self, bug_severity_list, days):
        if not isinstance(bug_severity_list, list):
            return 0

        num_of_related_bugs = 0
        for _, bug_creation_date in bug_severity_list:
            within_time_period = self.within_day(bug_creation_date, self.creation_ts, days)

            if within_time_period:
                num_of_related_bugs += 1

        return num_of_related_bugs

    # Number of bugs reported with the same severity within 7 days before the reporting of BR
    def num_of_bugs_with_severity(self, bug_severity_list, days):
        if not isinstance(bug_severity_list, list):
            return 0

        num_of_related_bugs = 0
        for bug_severity, bug_creation_date in bug_severity_list:
            same_severity = bug_severity == self.bug_severity
            within_time_period = self.within_day(bug_creation_date, self.creation_ts, days)

            if same_severity and within_time_period:
                num_of_related_bugs += 1

        return num_of_related_bugs

    # Number of bugs reported with the same or higher severity within 7 days before the reporting of BR
    def same_or_higher_severity(self):
        if self.bug_severity not in Bug.SEVERITY_LIST:
            return Bug.SEVERITY_LIST

        return Bug.SEVERITY_LIST[Bug.SEVERITY_LIST.index(self.bug_severity):]

    def num_of_bugs_with_same_or_higher_severity(self, bug_severity_list, days):
        if not isinstance(bug_severity_list, list):
            return 0

        num_of_related_bugs = 0
        for bug_severity, bug_creation_date in bug_severity_list:
            same_or_higher_severity = bug_severity in self.same_or_higher_severity()
            within_time_period = self.within_day(bug_creation_date, self.creation_ts, days)

            if same_or_higher_severity and within_time_period:
                num_of_related_bugs += 1

        return num_of_related_bugs

    # The same as (i, ii, iii) except the time duration is 30 days
    # The same as (i, ii, iii) except the time duration is 1 day
    # The same as (i, ii, iii) except the time duration is 3 days

    # # Textual Factor
    # Specific words and phrases from the description field of BR
    def short_desc_without_stop_words(self):
        if self.short_desc is None:
            return []

        tokenizer = RegexpTokenizer(r'\w+')
        words = tokenizer.tokenize(self.short_desc)

        return [word for word in words if word not in stopwords.words('english')]

    def to_short_desc_csv(self):
        words = self.short_desc_without_stop_words()
        return '{},{}'.format(self.priority, ','.join(words))

    # # Author Factor
    # Mean priority of bugs the author fixed
    def bugs_assigned_to_author(self, all_bugs, include_source_bug=False):
        return [item for item in all_bugs if (self.assigned_to == item.assigned_to and (include_source_bug or self.bug_id != item.bug_id))]

    def translated_priority(self):
        if self.priority is None:
            return 0

        return self.PRIORITIES[self.priority]

    def mean_priority_of_author(self, all_bugs):
        bugs_by_author = self.bugs_assigned_to_author(all_bugs, include_source_bug=True)
        all_priorities = [item.translated_priority() for item in bugs_by_author]

        if len(all_priorities) == 0:
            return 0

        return sum(all_priorities) / float(len(all_priorities))

    # Median priority of bugs the author fixed
    @staticmethod
    def median(lst):
        if len(lst) == 0:
            return 0.0

        return numpy.median(numpy.array(lst))

    def median_priority_of_author(self, all_bugs):
        bugs_by_author = self.bugs_assigned_to_author(all_bugs, include_source_bug=True)
        all_priorities = [item.translated_priority() for item in bugs_by_author]
        return self.median(all_priorities)

    # Mean priority of all bug reports made by the author of BR prior to the reporting of BR
    def bugs_reported_by_author(self, all_bugs, include_source_bug=False):
        return [item for item in all_bugs if (self.reporter == item.reporter and (include_source_bug or self.bug_id != item.bug_id))]

    def bugs_reported_prior(self, all_bugs):
        bugs_by_author = self.bugs_reported_by_author(all_bugs)
        return [item for item in bugs_by_author if item.creation_ts < self.creation_ts]

    def mean_priority_of_bug_by_author_prior(self, all_bugs):
        bugs_prior = self.bugs_reported_prior(all_bugs)
        all_priorities = [item.translated_priority() for item in bugs_prior]

        if len(all_priorities) == 0:
            return 0

        return reduce(lambda x, y: x + y, all_priorities) / float(len(all_priorities))

    # Median priority of all bug reports made by the author of BR prior to the reporting of BR
    def median_priority_of_bug_by_author_prior(self, all_bugs):
        bugs_prior = self.bugs_reported_prior(all_bugs)
        all_priorities = [item.translated_priority() for item in bugs_prior]
        return self.median(all_priorities)

    # The number of bug reports made by the author of BR prior to the reporting of BR
    def num_of_bug_by_author_prior(self, all_bugs):
        bugs_prior = self.bugs_reported_prior(all_bugs)
        return len(bugs_prior)

    # # Related-Report Factor
    # Operating system
    def os(self):
        if self.op_sys is None:
            return 9

        return self.OS_SYS[self.op_sys]

    # Mean priority of the top-20 most similar bug reports to BR as measured using REP - prior to the reporting of BR
    mean_priority_of_top20 = 0
    # Median priority of the top-20 most similar bug reports to BR as measured using REP - prior to the reporting of BR
    median_priority_of_top20 = 0
    # The same as (i, ii) except only the top 10 bug reports are considered
    mean_priority_of_top10 = 0
    median_priority_of_top10 = 0
    # The same as (i, ii) except only the top 5 bug reports are considered
    mean_priority_of_top5 = 0
    median_priority_of_top5 = 0
    # The same as (i, ii) except only the top 3 bug reports are considered
    mean_priority_of_top3 = 0
    median_priority_of_top3 = 0
    # The same as (i, ii) except only the top 1 bug report is considered
    mean_priority_of_top1 = 0
    median_priority_of_top1 = 0

    #
    # # Severity Factor
    # SEV BR's severity field.
    def severity_index(self):
        if self.bug_severity not in self.SEVERITY_LIST:
            return -1

        return self.SEVERITY_LIST.index(self.bug_severity)
    #
    # # Product Factor
    # BR's product field. This categorical feature is translated into multiple binary features.
    PRODUCTS = {'AJDT': 1, 'ALF': 2, 'Aperi': 3, 'AspectJ': 4, 'ATF': 5, 'BIRT': 6,
                'BPEL': 7, 'Buckminster': 8, 'CDT': 9, 'Cobol': 10,
                'Community': 11, 'Corona': 12, 'Cosmos': 13, 'Dali JPA Tools': 14,
                'Dash': 15, 'Data Tools': 16, 'DD': 17, 'DLTK': 18,
                'DSDP': 19, 'ECF': 20, 'EMF': 21, 'EMFT': 22, 'EPF': 23, 'EPP': 24, 'Equinox': 25,
                'ERCP': 26, 'gEclipse': 27, 'GEF': 28, 'GMF': 29, 'GMT': 30, 'Higgins': 31,
                'Hyades': 32, 'Java Server Faces': 33, 'JDT': 34,
                'Linux Distros': 35, 'M2M': 36, 'M2T': 37, 'Maynstall': 38, 'MDDi': 39, 'MDT': 40, 'Modeling': 41,
                'MTJ': 42, 'Mylyn': 43, 'NAB': 44, 'Nebula': 45, 'None': 46, 'OHF': 47, 'Orbit': 48, 'PDE': 49,
                'PDT': 50, 'Phoenix': 51, 'Photran': 52, 'Platform': 53, 'PTP': 54,
                'RAP': 55, 'SOA': 56, 'SOC': 57, 'Subversive': 58,
                'Target Management': 59, 'TPTP Agent Controller': 60, 'TPTP ASF': 61, 'TPTP Build to Manage': 62,
                'TPTP Common Logging': 63, 'TPTP GLA': 64, 'TPTP Line Coverage': 65, 'TPTP Log Analyzer': 66,
                'TPTP Probe Instrumentation': 67,
                'TPTP Profiling': 68, 'TPTP Release Engineering': 69, 'TPTP Resource Monitoring': 70,
                'TPTP Static Analysis': 71, 'TPTP Testing': 72, 'VE': 73, 'VTP': 74, 'Web Tools': 75, 'z_Archived': 76}

    def product_feature(self):
        if self.product not in self.PRODUCTS.keys():
            return 0
        return self.PRODUCTS[self.product]

    # Number of bug reports made for the same product as that of BR prior to the reporting of BR
    def num_of_bug_for_same_product_prior(self, all_bugs):
        num_of_bug = 0
        for item in all_bugs:
            same_product = self.product == item.product
            created_prior = item.creation_ts < self.creation_ts
            if same_product and created_prior:
                num_of_bug += 1

        return num_of_bug

    # Number of bug reports made for the same product of the same severity as that of BR prior to the reporting of BR
    def num_of_bug_for_same_product_and_severity_prior(self, all_bugs):
        num_of_bug = 0
        for item in all_bugs:
            same_product = self.product == item.product
            same_severity = self.bug_severity == item.bug_severity
            created_prior = item.creation_ts < self.creation_ts
            if same_product and same_severity and created_prior:
                num_of_bug += 1

        return num_of_bug

    # Number of bug reports made for the same product of the same or higher severity as those of BR prior to the # reporting of BR
    def num_of_bug_for_same_product_and_same_or_higher_severity_prior(self, all_bugs):
        num_of_bug = 0
        for item in all_bugs:
            same_product = self.product == item.product
            same_or_higher_severity = self.bug_severity in self.same_or_higher_severity()
            created_prior = item.creation_ts < self.creation_ts
            if same_product and same_or_higher_severity and created_prior:
                num_of_bug += 1

        return num_of_bug

    # Proportion of bug reports made for the same product as that of BR prior to the reporting of BR that are assigned priority P1.
    def num_of_p_bug_with_same_priority_and_prior(self, priority, all_bugs):
        num_of_bug = 0
        for item in all_bugs:
            same_product = self.product == item.product
            created_prior = item.creation_ts < self.creation_ts
            p1 = self.priority == priority
            if same_product and p1 and created_prior:
                num_of_bug += 1

        return num_of_bug

    def pro_of_p1_bug_with_same_priority_and_prior(self, all_bugs):
        return self.num_of_p_bug_with_same_priority_and_prior('P1', all_bugs) / float(len(all_bugs))

    # The same as num_of_p1_bug_with_same_priority_and_prior except they are for priority P2, P3, P4, P5 respectively.
    def pro_of_p2_bug_with_same_priority_and_prior(self, all_bugs):
        return self.num_of_p_bug_with_same_priority_and_prior('P2', all_bugs) / float(len(all_bugs))

    def pro_of_p3_bug_with_same_priority_and_prior(self, all_bugs):
        return self.num_of_p_bug_with_same_priority_and_prior('P3', all_bugs) / float(len(all_bugs))

    def pro_of_p4_bug_with_same_priority_and_prior(self, all_bugs):
        return self.num_of_p_bug_with_same_priority_and_prior('P4', all_bugs) / float(len(all_bugs))

    def pro_of_p5_bug_with_same_priority_and_prior(self, all_bugs):
        return self.num_of_p_bug_with_same_priority_and_prior('P5', all_bugs) / float(len(all_bugs))

    # Mean priority of bug reports made for the same product as that of BR prior to the reporting of BR
    def mean_priority_of_bug_for_same_product_prior(self, all_bugs):
        total_priority = 0
        num_of_bugs = 0
        for item in all_bugs:
            same_product = self.product == item.product
            created_prior = item.creation_ts < self.creation_ts
            if same_product and created_prior:
                total_priority += item.translated_priority()
                num_of_bugs += 1

        if num_of_bugs == 0:
            return 0

        return total_priority / float(num_of_bugs)

    # Median priority of bug reports made for the same product as that of BR prior to the reporting of BR
    def median_priority_of_bug_for_same_product_prior(self, all_bugs):
        bugs = [item.translated_priority() for item in all_bugs if (self.product == item.product and item.creation_ts < self.creation_ts)]
        return self.median(bugs)

    # The same as (i, ii, iii, iv, v, vi, vii, viii) except they are for the component field of BR.
    COMPONENTS = {'Component': 1, 'AJBrowser': 2, 'AJDoc': 3, 'alf-commonServices': 4, 'alf-core': 5, 'alf-plugins': 6,
                  'alf-sso': 7, 'alf-test': 8,
                  'alf-vocabulary': 9, 'AM3': 10, 'AMW': 11, 'Annotations': 12, 'Ant': 13,
                  'Apache Derby Conn Profile': 14, 'Aperi': 15, 'aperi.agent': 16, 'aperi.data': 17, 'aperi.db': 18,
                  'aperi.device': 19, 'aperi.gui': 20, 'aperi.reporting': 21, 'App': 22, 'apps.eclipse.org': 23,
                  'APT': 24, 'Articles': 25, 'ASF.Runtime': 26, 'ATL': 27, 'ATL-Engine': 28,
                  'ATL-UI': 29, 'ATNA': 30, 'Auto Insertion': 31, 'Automated Builds': 32, 'Blogs': 33, 'bridge': 34,
                  'Bugzilla': 35, 'Build': 36, 'bundles': 37, 'Bundles': 38,
                  'CDateTime': 39, 'CDE': 40, 'CDO': 41, 'cdt-build': 42, 'CDT-Contrib': 43, 'cdt-core': 44,
                  'cdt-cppunit': 45, 'cdt-debug': 46, 'cdt-doc': 47, 'cdt-launch': 48,
                  'CDT-parser': 49, 'cdt-releng': 50, 'ChangeLog': 51, 'Chart': 52, 'CME': 53, 'Code Assist': 54,
                  'Code Folding': 55, 'Code Formatter': 56, 'collaboration': 57, 'Commits Explorer': 58,
                  'CommitterTools': 59, 'Common': 60, 'Compare': 61, 'Compiler': 62, 'CompositeTable': 63,
                  'Connection Mgt Framework': 64, 'Connectivity': 65, 'container': 66, 'Content': 67,
                  'Content Translation': 68,
                  'Context Provider': 69, 'Contexts': 70, 'Converters': 71, 'Core': 72, 'core': 73, 'cosmos.build': 74,
                  'cosmos.web': 75, 'Cpp-Extensions': 76, 'Cross-Project': 77, 'CTableTree': 78,
                  'CVS': 79, 'Dashboard': 80, 'Data': 81, 'Data Access': 82, 'Data Source Explorer': 83,
                  'DataCollection': 84, 'DataCollection&Control': 85, 'DataReporting': 86, 'DateChooser': 87,
                  'DB Definition Model': 88,
                  'DDL Generation': 89, 'Debug': 90, 'Debug Core': 91, 'Debug SDM': 92, 'Debug UI': 93,
                  'Debug-core': 94, 'Debug-MI': 95, 'Debug-UI': 96, 'Debugger & Console View': 97, 'Definition': 98,
                  'Demo': 99, 'design': 100, 'DeviceKit': 101, 'DevTools': 102, 'doc': 103, 'Doc': 104, 'Docs': 105,
                  'documentation': 106, 'Documentation': 107, 'draw2d': 108,
                  'Driver Mgt Framework': 109, 'DSE Data Actions': 110, 'DSF': 111, 'ecf.core': 112, 'ecf.doc': 113,
                  'ecf.examples': 114, 'ecf.protocols': 115, 'ecf.providers': 116, 'ecf.test': 117, 'ecf.ui': 118,
                  'Eclipse monkey': 119, 'EclipseCon': 120, 'EclipseLIVE': 121, 'eCore': 122, 'Edit': 123,
                  'Editor': 124, 'Editor & Outline View': 125, 'editors': 126, 'eJFace': 127, 'Enablement': 128,
                  'Enablement:ODA': 129, 'EODM': 130, 'EPIC': 131, 'eSWT': 132, 'eUpdate': 133, 'eWorkbench': 134,
                  'Examples': 135, 'Exec': 136, 'Exec.correlation': 137, 'Exec.harness': 138,
                  'Exec.JVMPI': 139, 'Exec.logging': 140, 'Exec.OSMonitor': 141, 'FAQ': 142, 'For Internal Use': 143,
                  'FormattedText': 144, 'Framework': 145, 'Gallery': 146, 'GDB': 147, 'geclipse': 148,
                  'GEF': 149, 'General': 150, 'General UI': 151, 'Generation': 152, 'Generation - Lite': 153,
                  'Generic-Extensions': 154, 'Grid': 155, 'H3ET': 156, 'HBX': 157, 'HBX SUPPORT': 158,
                  'HL7V2': 159, 'Hover Help': 160, 'Hyades': 161, 'I-Card Broker': 162, 'I-Card Provider': 163,
                  'I-CARD REGISTRY': 164, 'IdAS': 165, 'IDE': 166, 'ihe.ui': 167, 'incubator': 168,
                  'Incubator': 169, 'Incubators': 170, 'Installer': 171, 'IntegratedAgentController': 172,
                  'IP-XACT': 173, 'IPZilla': 174, 'ISS': 175, 'ISS WEB UI': 176, 'J2EE Standard Tools': 177,
                  'Java': 178,
                  'Java Core': 179, 'javascript': 180, 'JCR Management': 181, 'JDBC Conn Profile': 182, 'Jet': 183,
                  'Jet Editor': 184, 'JFace': 185, 'JFC/Swing': 186, 'Jira': 187, 'JSF Tools': 188,
                  'JSR220orm': 189, 'jst.ejb': 190, 'jst.j2ee': 191, 'jst.jem': 192, 'jst.jsp': 193, 'jst.server': 194,
                  'jst.servlet': 195, 'jst.ws': 196, 'kb': 197, 'Lang': 198,
                  'Laszlo': 199, 'Lepido': 200, 'Library': 201, 'LinuxDistros': 202, 'Log.Model': 203,
                  'LogAnalyzer.Doc': 204, 'LTWeaving': 205, 'Mail': 206, 'MailingLists': 207, 'manage': 208,
                  'Managed Make': 209, 'Mapping': 210, 'MI': 211, 'microXML': 212, 'middleware': 213, 'Misc': 214,
                  'Mobile': 215, 'Model': 216, 'ModelBase': 217, 'ModelBus': 218,
                  'Models': 219, 'Models - Generation': 220, 'Models - Graphical': 221, 'Models - Mapping': 222,
                  'Models - Tooling': 223, 'Models.log': 224, 'Models.sdb': 225, 'Models.statistical': 226,
                  'Models.test': 227, 'Models.trace': 228,
                  'MOFScript': 229, 'Monitor': 230, 'Monitor.Agents': 231, 'Monitor.Analysis': 232,
                  'Monitor.Execution': 233, 'Monitor.UI': 234, 'Monitor.UI.CustomizedStatsView': 235,
                  'Monitor.UI.GLARules': 236, 'Monitor.UI.ManagedResourcesExplorer': 237, 'Monitor.UI.Reporting': 238,
                  'Monitor.UI.SDBEditor': 239, 'Monitor.UI.WSDMTooling': 240, 'mozide': 241,
                  'MPI Development Tools': 242, 'MTJ projects': 243, 'NET4J': 244, 'Newsgroups': 245, 'None': 246,
                  'OAW': 247, 'oAW-check': 248,
                  'oAW-classic': 249, 'oAW-default': 250, 'oAW-docs': 251, 'oAW-emf': 252, 'oAW-expressions': 253,
                  'oAW-extend': 254, 'oAW-gmf': 255, 'oaw-plugins': 256, 'oAW-recipe': 257, 'oAW-samples': 258,
                  'oAW-uml2': 259, 'oAW-utilities': 260, 'oAW-workflow': 261, 'oAW-xtext': 262, 'OCL': 263,
                  'Open Data Access': 264, 'Open PHP Element': 265, 'OProfile': 266, 'org.eclipse.stp.b2j': 267,
                  'org.eclipse.stp.bpmn': 268,
                  'org.eclipse.stp.core': 269, 'org.eclipse.stp.servicecreation': 270, 'org.eclipse.stp.soas': 271,
                  'Outline Views': 272, 'package content': 273, 'Packager': 274, 'PackagingTools': 275,
                  'PDE support': 276, 'pdq.consumer': 277, 'personality': 278,
                  'PHP Explorer View': 279, 'PHP Functions View': 280, 'PHP Manual': 281, 'PHP Search': 282,
                  'pix.consumer': 283, 'pix.source': 284, 'PlanetEclipse.org': 285, 'Platform.Agents': 286,
                  'Platform.Agents.JVMPI': 287, 'Platform.Agents.JVMTI': 288,
                  'Platform.Agents.Logging': 289, 'Platform.Analysis': 290, 'Platform.Collection': 291,
                  'Platform.Communication': 292, 'Platform.Doc': 293, 'Platform.Execution': 294,
                  'Platform.Execution.CBELogging': 295, 'Platform.Execution.Choreography': 296,
                  'Platform.Execution.CorrelationEngine': 297, 'Platform.Execution.Framework': 298,
                  'Platform.Execution.Instrumentation': 299, 'Platform.Execution.ProbekitBCI': 300,
                  'Platform.LineCoverage.Runtime': 301, 'Platform.LineCoverage.UI': 302, 'Platform.Model': 303,
                  'Platform.UI': 304, 'Platform.UI.Charting': 305, 'Platform.UI.LogView': 306,
                  'Platform.UI.ProbeEditor': 307, 'Platform.UI.ProfilingPerspective': 308,
                  'Platform.UI.Reporting': 309, 'Platform.UI.SequenceDiagram': 310, 'Platform.UI.StatsPerfViewers': 311,
                  'PLDT': 312, 'Pollinate': 313, 'Portal': 314, 'Probekit': 315, 'Problems view': 316, 'Process': 317,
                  'Project Builder': 318,
                  'Project Management': 319, 'providers': 320, 'PShelf': 321, 'Python': 322, 'Query': 323,
                  'Reconciler': 324, 'releng': 325, 'Releng': 326, 'Relying Party': 327, 'Report': 328,
                  'Report Designer': 329, 'Report Engine': 330, 'Report Viewer': 331, 'ResourceModeling': 332,
                  'Resources': 333, 'RM': 334, 'RPM': 335, 'RSE': 336, 'RSS-SSE RP TEST APP': 337, 'Ruby': 338,
                  'Runtime': 339, 'runtime': 340, 'Runtime Common': 341, 'Runtime Diagram': 342, 'Runtime EMF': 343,
                  'RWT': 344, 'Samples': 345, 'SAT': 346, 'Scripting': 347, 'SDK Management': 348,
                  'SDO': 349, 'Search': 350, 'Security Management': 351, 'Server': 352, 'Servers': 353, 'Signing': 354,
                  'simdebug': 355, 'soa': 356, 'SQL Debug Framework': 357, 'SQL Debugger Framework': 358,
                  'SQL Editor Framework': 359, 'SQL Execution Plan': 360, 'SQL Model': 361, 'SQL Query Builder': 362,
                  'SQL Query Model': 363, 'SQL Query Parser': 364, 'SQL Results View': 365, 'SQLDevTools': 366,
                  'Stellation': 367, 'STEM': 368,
                  'STS': 369, 'Subversion': 370, 'SWT': 371, 'Syntax Coloring': 372, 'Table Data Editor': 373,
                  'Tasks': 374, 'Tcl': 375, 'Team': 376, 'Templates': 377, 'Teneo': 378,
                  'Terminal': 379, 'Test': 380, 'Test Suite': 381, 'Test.Agents': 382, 'Test.Agents.ComptestAgent': 383,
                  'Test.Agents.Recorder': 384, 'Test.common': 385, 'Test.Doc': 386, 'Test.Execution': 387,
                  'Test.Execution.AutoGUIRunner': 388,
                  'Test.Execution.CommonRunner': 389, 'Test.Execution.ExecutionHarness': 390,
                  'Test.Execution.JUnitRunner': 391, 'Test.Execution.ManualRunner': 392,
                  'Test.Execution.URLRunner': 393, 'Test.http': 394, 'Test.java': 395, 'Test.Model': 396,
                  'Test.UI': 397, 'Test.UI.AutoGUIUI': 398,
                  'Test.UI.ConfigEditors': 399, 'Test.UI.DatapoolEditor': 400, 'Test.UI.FrameworkEditors': 401,
                  'Test.UI.JUnit': 402, 'Test.UI.Manual': 403, 'Test.UI.ManualTestClient': 404,
                  'Test.UI.Reporting': 405, 'Test.UI.TestPerspective': 406, 'Test.UI.URLTest': 407, 'TestHarness': 408,
                  'Testing': 409, 'Text': 410, 'Token Provider': 411, 'Tool': 412, 'Tools': 413, 'tools': 414,
                  'TPTP.Reports': 415, 'TPTP.Testing': 416, 'TPTP.Web': 417, 'Trac': 418,
                  'Trace.Execution': 419, 'Trace.UI': 420, 'Transaction': 421, 'UI': 422, 'UI - Wizards': 423,
                  'UI Guidelines': 424, 'UI.deployment_editor': 425, 'UI.execution_editor': 426, 'UI.log_view': 427,
                  'UI.memory': 428,
                  'UI.performance': 429, 'UI.probe_editor': 430, 'UI.seq_diagram': 431, 'UI.statistical_view': 432,
                  'UI.test_framework_editor': 433, 'UI.testsuite_editor': 434, 'UI.text_editors': 435, 'UML2': 436,
                  'UML2Tools': 437, 'UMLX': 438,
                  'Unknown': 439, 'Update': 440, 'Updater': 441, 'User': 442, 'User Assistance': 443,
                  'User Interface': 444, 'Validation': 445, 'vservers': 446, 'w4t': 447, 'WADO': 448,
                  'Web': 449, 'Web Server (Apache)': 450, 'Web Site': 451, 'Web Standard Tools': 452, 'WebDAV': 453,
                  'Website': 454, 'website': 455, 'Wiki': 456, 'wiki': 457, 'WindowsService': 458,
                  'wizards': 459, 'Workbench': 460, 'wst.command': 461, 'wst.common': 462, 'wst.css': 463,
                  'wst.dtd': 464, 'wst.html': 465, 'wst.internet': 466, 'wst.javascript': 467, 'wst.jsdt': 468,
                  'wst.rdb': 469, 'wst.server': 470, 'wst.sse': 471, 'wst.validation': 472, 'wst.web': 473,
                  'wst.ws': 474, 'wst.wsdl': 475, 'wst.wsi': 476, 'wst.xml': 477, 'wst.xsd': 478,
                  'WSVT': 479, 'xds.consumer': 480, 'xds.metadata': 481, 'xds.source': 482, 'XML': 483, 'XML/XMI': 484,
                  'XPlanner': 485, 'XSD': 486, 'Zest': 487,}

    def component_feature(self):
        if self.component not in self.COMPONENTS.keys():
            return 0
        return self.COMPONENTS[self.component]

    # Number of bug reports made for the same component as that of BR prior to the reporting of BR
    def num_of_bug_for_same_component_prior(self, all_bugs):
        num_of_bug = 0
        for item in all_bugs:
            same_component = self.component == item.component
            created_prior = item.creation_ts < self.creation_ts
            if same_component and created_prior:
                num_of_bug += 1

        return num_of_bug

    # Number of bug reports made for the same component of the same severity as that of BR prior to the reporting of BR
    def num_of_bug_for_same_component_and_severity_prior(self, all_bugs):
        num_of_bug = 0
        for item in all_bugs:
            same_component = self.component == item.component
            same_severity = self.bug_severity == item.bug_severity
            created_prior = item.creation_ts < self.creation_ts
            if same_component and same_severity and created_prior:
                num_of_bug += 1

        return num_of_bug

    # Number of bug reports made for the same component of the same or higher severity as those of BR prior to the # reporting of BR
    def num_of_bug_for_same_component_and_same_or_higher_severity_prior(self, all_bugs):
        num_of_bug = 0
        for item in all_bugs:
            same_component = self.component == item.component
            same_or_higher_severity = self.bug_severity in self.same_or_higher_severity()
            created_prior = item.creation_ts < self.creation_ts
            if same_component and same_or_higher_severity and created_prior:
                num_of_bug += 1

        return num_of_bug

    # Proportion of bug reports made for the same component as that of BR prior to the reporting of BR that are assigned priority P1.
    def num_of_p_bug_with_same_priority_and_prior_for_component(self, priority, all_bugs):
        num_of_bug = 0
        for item in all_bugs:
            same_component = self.component == item.component
            created_prior = item.creation_ts < self.creation_ts
            p1 = self.priority == priority
            if same_component and p1 and created_prior:
                num_of_bug += 1

        return num_of_bug

    def pro_of_p1_bug_with_same_priority_and_prior_for_component(self, all_bugs):
        return self.num_of_p_bug_with_same_priority_and_prior_for_component('P1', all_bugs) / float(len(all_bugs))

    # The same as num_of_p1_bug_with_same_priority_and_prior except they are for priority P2, P3, P4, P5 respectively.
    def pro_of_p2_bug_with_same_priority_and_prior_for_component(self, all_bugs):
        return self.num_of_p_bug_with_same_priority_and_prior_for_component('P2', all_bugs) / float(len(all_bugs))

    def pro_of_p3_bug_with_same_priority_and_prior_for_component(self, all_bugs):
        return self.num_of_p_bug_with_same_priority_and_prior_for_component('P3', all_bugs) / float(len(all_bugs))

    def pro_of_p4_bug_with_same_priority_and_prior_for_component(self, all_bugs):
        return self.num_of_p_bug_with_same_priority_and_prior_for_component('P4', all_bugs) / float(len(all_bugs))

    def pro_of_p5_bug_with_same_priority_and_prior_for_component(self, all_bugs):
        return self.num_of_p_bug_with_same_priority_and_prior_for_component('P5', all_bugs) / float(len(all_bugs))

    # Mean priority of bug reports made for the same component as that of BR prior to the reporting of BR
    def mean_priority_of_bug_for_same_component_prior(self, all_bugs):
        total_priority = 0
        num_of_bugs = 0
        for item in all_bugs:
            same_component = self.component == item.component
            created_prior = item.creation_ts < self.creation_ts
            if same_component and created_prior:
                total_priority += item.translated_priority()
                num_of_bugs += 1

        if num_of_bugs == 0:
            return 0

        return total_priority / float(num_of_bugs)

    # Median priority of bug reports made for the same component as that of BR prior to the reporting of BR
    def median_priority_of_bug_for_same_component_prior(self, all_bugs):
        bugs = [item.translated_priority() for item in all_bugs if (self.component == item.component and item.creation_ts < self.creation_ts)]
        return self.median(bugs)

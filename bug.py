from dateutil.parser import parse
import string
from feature_extraction import NodeUtil
from long_desc import LongDesc
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer


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
    def priority_of_author(self, author_list):
        if self.reporter not in author_list.keys():
            return 0

        return author_list[self.reporter]


    # Median priority of bugs the author fixed
    # Mean priority of all bug reports made by the author of BR prior to the reporting of BR
    # Median priority of all bug reports made by the author of BR prior to the reporting of BR
    # The number of bug reports made by the author of BR prior to the reporting of BR
    #
    # # Related-Report Factor
    # Number of comments in the bug report
    # Operating system
    # Mean priority of the top-20 most similar bug reports to BR as measured using REP - prior to the reporting of BR
    # Median priority of the top-20 most similar bug reports to BR as measured using REP - prior to the reporting of BR
    # The same as (i, ii) except only the top 10 bug reports are considered
    # The same as (i, ii) except only the top 5 bug reports are considered
    # The same as (i, ii) except only the top 3 bug reports are considered
    # The same as (i, ii) except only the top 1 bug report is considered
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
    # Number of bug reports made for the same product as that of BR prior to the reporting of BR
    # Number of bug reports made for the same product of the same severity as that of BR prior to the reporting of BR
    # Number of bug reports made for the same product of the same or higher severity as those of BR prior to the # reporting of BR
    # Proportion of bug reports made for the same product as that of BR prior to the reporting of BR that are assigned # priority P1.
    # The same as PRO5 except they are for priority (ii, iii, iv, v) respectively.
    # Mean priority of bug reports made for the same product as that of BR prior to the reporting of BR
    # Median priority of bug reports made for the same product as that of BR prior to the reporting of BR
    # The same as (i, ii, iii, iv, v, vi, vii, viii) except they are for the component field of BR.

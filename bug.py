from dateutil.parser import parse
import string
from feature_extraction import NodeUtil
from long_desc import LongDesc
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import time

cachedStopWords = stopwords.words("english")


class Bug(object):
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
    error = False
    creation_ts = 0
    short_desc = None
    delta_ts = 0
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
            self.error = True
            return None

        self.bug_id = NodeUtil.getText(item.getElementsByTagName('bug_id')[0].childNodes)

        if len(item.attributes) > 0 and 'error' in item.attributes.keys():
            error = item.attributes['error']
            if error is not None and (error.value == 'NotFound' or error.value == 'NotPermitted'):
                self.error = True
                return None

        self.creation_ts = parse(NodeUtil.getText(item.getElementsByTagName('creation_ts')[0].childNodes))

        short_desc_element = item.getElementsByTagName('short_desc')
        if short_desc_element is not None and len(short_desc_element) > 0:
            desc = self.clean_string(NodeUtil.getText(short_desc_element[0].childNodes))
            tokenizer = RegexpTokenizer(r'\w+')
            self.short_desc = tokenizer.tokenize(desc)

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

    @staticmethod
    def clean_string(str):
        if str is None:
            return ''

        printable = set(string.printable)
        return filter(lambda s: s in printable, str).replace(',', ';')

    def generate_dict(self):
        base = {
            'creation_ts': time.mktime(self.creation_ts.timetuple()),
            'delta_ts': time.mktime(self.delta_ts.timetuple()),
            'reporter_accessible': self.reporter_accessible,
            'cclist_accessible': self.cclist_accessible,
            'classification_id': self.classification_id,
            'classification': self.classification,
            'product': self.product,
            'component': self.component,
            'version': self.version,
            'rep_platform': self.rep_platform,
            'op_sys': self.op_sys,
            'bug_status': self.bug_status,
            'resolution': self.resolution,
            'priority': int(self.priority[1:]),
            'bug_severity': self.SEVERITY_LIST.index(self.bug_severity),
            'target_milestone': self.target_milestone,
            'everconfirmed': self.everconfirmed,
            'reporter': self.reporter,
            'assigned_to': self.assigned_to,
            'qa_contact': self.qa_contact
        }

        short_desc = self.generate_array_dict('short_desc', self.short_desc)
        blocked = self.generate_array_dict('blocked', self.blocked)
        dependson = self.generate_array_dict('dependson', self.dependson)
        cc = self.generate_array_dict('cc', self.cc)

        return self.merge_dicts(base, short_desc, blocked, dependson, cc)

    @staticmethod
    def generate_array_dict(key, l):
        if l is None:
            return dict()

        d = dict()
        for e in l:
            d['{}={}'.format(key, e)] = True
        return d

    @staticmethod
    def merge_dicts(*dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result
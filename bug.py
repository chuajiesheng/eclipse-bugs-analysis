from dateutil.parser import parse
import string
from feature_extraction import NodeUtil
from long_desc import LongDesc


class Bug(object):
    FIELDS = ['bug_id', 'creation_ts', 'short_desc', 'delta_ts', 'reporter_accessible', 'cclist_accessible',
              'classification_id', 'classification', 'product', 'component', 'version', 'rep_platform', 'op_sys',
              'bug_status', 'resolution', 'priority', 'bug_severity', 'target_milestone', 'blocked', 'dependson',
              'everconfirmed', 'reporter', 'assigned_to', 'cc', 'qa_contact', 'long_des']
    CSV_STRING = "{},{},\"{}\",{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}"

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
            self.short_desc = NodeUtil.getText(short_desc_element[0].childNodes)

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
        if length == 0:
            return "{},{},{},{},".format(length, 0, 0, 0)

        all_bug_when_values = [parse(ld.bug_when) for ld in self.long_desc]
        all_bug_when_values.sort()

        longest_gap = (all_bug_when_values[-1] - self.creation_ts).total_seconds()
        total_gap = 0
        for bug_when in all_bug_when_values:
            total_gap += (bug_when - self.creation_ts).total_seconds()

        average_gap = total_gap / len(all_bug_when_values)

        str = "{},{},{},{},".format(length, total_gap, average_gap, longest_gap)
        return str

    def csv_title(self):
        fields = self.FIELDS
        fields.extend(['total_gap', 'average_gap', 'longest_gap'])
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
from feature_extraction import NodeUtil

class LongDesc:
    who = None
    bug_when = None
    thetext = None

    def __init__(self, item):
        if item is None:
            return None

        self.who = NodeUtil.getText(item.getElementsByTagName('who')[0].childNodes)
        self.bug_when = NodeUtil.getText(item.getElementsByTagName('bug_when')[0].childNodes)

        thetext_element = item.getElementsByTagName('thetext')
        self.thetext = NodeUtil.getText(thetext_element[0].childNodes)
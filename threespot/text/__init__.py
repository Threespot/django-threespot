def unescape(text):
    """
    Convert HTML entities to unicode equivalents.
    By Frederick Lundh: effbot.org/zone/re-sub.html#unescape-html
    """
    import re, htmlentitydefs
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character ref
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1],1))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            #named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text
    return re.sub("&#?\w+;", fixup, text)
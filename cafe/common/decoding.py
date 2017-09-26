import six


def safe_decode(text, incoming='utf-8', errors='replace'):
    """Decodes incoming text/bytes string using `incoming`
        if they're not already unicode.

    :param incoming: Text's current encoding
    :param errors: Errors handling policy. See here for valid
        values http://docs.python.org/2/library/codecs.html
    :returns: text or a unicode `incoming` encoded
                representation of it.
    """
    if isinstance(text, six.text_type):
        return text

    return text.decode(incoming, errors)

# Copyright 2015 Rackspace
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""
.. seealso:: http://en.wikipedia.org/wiki/Unicode#Architecture_and_terminology

Usage Examples:
::

    # Print all the characters in the "Thai" unicode block
    for c in UNICODE_BLOCKS.get_range(BLOCK_NAMES.thai).encoded_codepoints():
        print c

    # Iterate through all the integer codepoints in the "Thai" unicode block
    for i in UNICODE_BLOCKS.get_range(BLOCK_NAMES.thai).codepoints():
        do_something(i)

    # Get a list of the names of all the characters in the "Thai" unicode block
        [n for n in UNICODE_BLOCKS.get_range(
            BLOCK_NAMES.thai).codepoint_names()]
"""

import six
import unicodedata

#: Integer denoting the first unicode codepoint
UNICODE_STARTING_CODEPOINT = 0x0

#: Integer denoting the last unicode codepoint
UNICODE_ENDING_CODEPOINT = 0x10FFFD

# list-like object that iterates through named ranges of unicode codepoints
# Instantiated at runtime (when imported) near the bottom of this file
UNICODE_BLOCKS = None

# list-like object that iterates through ranges of ranges of unicode codepoints
# Instantiated at runtime (when imported) near the bottom of this file
UNICODE_PLANES = None


class PLANE_NAMES(object):
    """
    Namespace that defines all standard Unicode Plane names

    A list-like object (UnicodeRangeList) made up of UnicodeRange
    objects.  It covers the same total range as UNICODE_BLOCKS, but is
    instead organized by plane names instead of block names, which
    results in fewer but larger ranges.
    """
    basic_multilingual_plane = 'Basic Multilingual Plane'
    supplementary_multilingual_plane = 'Supplementary Multilingual Plane'
    supplementary_ideographic_plane = 'Supplementary Ideographic Plane'
    unassigned = 'Unassigned'
    supplementary_special_purpose_plane = 'Supplementary Special-purpose Plane'
    supplementary_private_use_area = 'Supplementary Private Use Area'


class BLOCK_NAMES(object):
    """
    Namespace that defines all standard Unicode Block names

    A list-like object (UnicodeRangeList) made up of
    UnicodeRange objects.  Each UnicodeRange object in the list
    corresponds to a named Unicode Block, and contains the start
    and end integer for that Block.
    """
    basic_latin = "Basic Latin"
    c1_controls_and_latin_1_supplement = "C1 Controls and Latin-1 Supplement"
    latin_extended_a = "Latin Extended-A"
    latin_extended_b = "Latin Extended-B"
    ipa_extensions = "IPA Extensions"
    spacing_modifier_letters = "Spacing Modifier Letters"
    combining_diacritical_marks = "Combining Diacritical Marks"
    greek_coptic = "Greek_Coptic"
    cyrillic = "Cyrillic"
    cyrillic_supplement = "Cyrillic Supplement"
    armenian = "Armenian"
    hebrew = "Hebrew"
    arabic = "Arabic"
    syriac = "Syriac"
    undefined = "Undefined"
    thaana = "Thaana"
    devanagari = "Devanagari"
    bengali_assamese = "Bengali_Assamese"
    gurmukhi = "Gurmukhi"
    gujarati = "Gujarati"
    oriya = "Oriya"
    tamil = "Tamil"
    telugu = "Telugu"
    kannada = "Kannada"
    malayalam = "Malayalam"
    sinhala = "Sinhala"
    thai = "Thai"
    lao = "Lao"
    tibetan = "Tibetan"
    myanmar = "Myanmar"
    georgian = "Georgian"
    hangul_jamo = "Hangul Jamo"
    ethiopic = "Ethiopic"
    cherokee = "Cherokee"
    unified_canadian_aboriginal_syllabics = (
        "Unified Canadian Aboriginal Syllabics")
    ogham = "Ogham"
    runic = "Runic"
    tagalog = "Tagalog"
    hanunoo = "Hanunoo"
    buhid = "Buhid"
    tagbanwa = "Tagbanwa"
    khmer = "Khmer"
    mongolian = "Mongolian"
    limbu = "Limbu"
    tai_le = "Tai Le"
    khmer_symbols = "Khmer Symbols"
    phonetic_extensions = "Phonetic Extensions"
    latin_extended_additional = "Latin Extended Additional"
    greek_extended = "Greek Extended"
    general_punctuation = "General Punctuation"
    superscripts_and_subscripts = "Superscripts and Subscripts"
    currency_symbols = "Currency Symbols"
    combining_diacritical_marks_for_symbols = (
        "Combining Diacritical Marks for Symbols")
    letterlike_symbols = "Letterlike Symbols"
    number_forms = "Number Forms"
    arrows = "Arrows"
    mathematical_operators = "Mathematical Operators"
    miscellaneous_technical = "Miscellaneous Technical"
    control_pictures = "Control Pictures"
    optical_character_recognition = "Optical Character Recognition"
    enclosed_alphanumerics = "Enclosed Alphanumerics"
    box_drawing = "Box Drawing"
    block_elements = "Block Elements"
    geometric_shapes = "Geometric Shapes"
    miscellaneous_symbols = "Miscellaneous Symbols"
    dingbats = "Dingbats"
    miscellaneous_mathematical_symbols_a = (
        "Miscellaneous Mathematical Symbols-A")
    supplemental_arrows_a = "Supplemental Arrows-A"
    braille_patterns = "Braille Patterns"
    supplemental_arrows_b = "Supplemental Arrows-B"
    miscellaneous_mathematical_symbols_b = (
        "Miscellaneous Mathematical Symbols-B")
    supplemental_mathematical_operators = "Supplemental Mathematical Operators"
    miscellaneous_symbols_and_arrows = "Miscellaneous Symbols and Arrows"
    cjk_radicals_supplement = "CJK Radicals Supplement"
    kangxi_radicals = "Kangxi Radicals"
    ideographic_description_characters = "Ideographic Description Characters"
    cjk_symbols_and_punctuation = "CJK Symbols and Punctuation"
    hiragana = "Hiragana"
    katakana = "Katakana"
    bopomofo = "Bopomofo"
    hangul_compatibility_jamo = "Hangul Compatibility Jamo"
    kanbun_kunten = "Kanbun (Kunten)"
    bopomofo_extended = "Bopomofo Extended"
    katakana_phonetic_extensions = "Katakana Phonetic Extensions"
    enclosed_cjk_letters_and_months = "Enclosed CJK Letters and Months"
    cjk_compatibility = "CJK Compatibility"
    cjk_unified_ideographs_extension_a = "CJK Unified Ideographs Extension A"
    yijing_hexagram_symbols = "Yijing Hexagram Symbols"
    cjk_unified_ideographs = "CJK Unified Ideographs"
    yi_syllables = "Yi Syllables"
    yi_radicals = "Yi Radicals"
    hangul_syllables = "Hangul Syllables"
    high_surrogate_area = "High Surrogate Area"
    low_surrogate_area = "Low Surrogate Area"
    private_use_area = "Private Use Area"
    cjk_compatibility_ideographs = "CJK Compatibility Ideographs"
    alphabetic_presentation_forms = "Alphabetic Presentation Forms"
    arabic_presentation_forms_a = "Arabic Presentation Forms-A"
    variation_selectors = "Variation Selectors"
    combining_half_marks = "Combining Half Marks"
    cjk_compatibility_forms = "CJK Compatibility Forms"
    small_form_variants = "Small Form Variants"
    arabic_presentation_forms_b = "Arabic Presentation Forms-B"
    halfwidth_and_fullwidth_forms = "Halfwidth and Fullwidth Forms"
    specials = "Specials"
    linear_b_syllabary = "Linear B Syllabary"
    linear_b_ideograms = "Linear B Ideograms"
    aegean_numbers = "Aegean Numbers"
    old_italic = "Old Italic"
    gothic = "Gothic"
    ugaritic = "Ugaritic"
    deseret = "Deseret"
    shavian = "Shavian"
    osmanya = "Osmanya"
    cypriot_syllabary = "Cypriot Syllabary"
    byzantine_musical_symbols = "Byzantine Musical Symbols"
    musical_symbols = "Musical Symbols"
    tai_xuan_jing_symbols = "Tai Xuan Jing Symbols"
    mathematical_alphanumeric_symbols = "Mathematical Alphanumeric Symbols"
    cjk_unified_ideographs_extension_b = "CJK Unified Ideographs Extension B"
    cjk_compatibility_ideographs_supplement = (
        "CJK Compatibility Ideographs Supplement")
    unused = "Unused"
    tags = "Tags"
    variation_selectors_supplement = "Variation Selectors Supplement"
    supplementary_private_use_area_a = "Supplementary Private Use Area-A"
    supplementary_private_use_area_b = "Supplementary Private Use Area-B"

_unicode_planes = (
    (0x0, 0xffff, PLANE_NAMES.basic_multilingual_plane),
    (0x10000, 0x1ffff, PLANE_NAMES.supplementary_multilingual_plane),
    (0x20000, 0x2ffff, PLANE_NAMES.supplementary_ideographic_plane),
    (0x30000, 0xdffff, PLANE_NAMES.unassigned),
    (0xe0000, 0xeffff, PLANE_NAMES.supplementary_special_purpose_plane),
    (0xf0000, 0x10ffff, PLANE_NAMES.supplementary_private_use_area))

_unicode_blocks = (
    (0x0, 0x7f, BLOCK_NAMES.basic_latin),
    (0x80, 0xff, BLOCK_NAMES.c1_controls_and_latin_1_supplement),
    (0x100, 0x17f, BLOCK_NAMES.latin_extended_a),
    (0x180, 0x24f, BLOCK_NAMES.latin_extended_b),
    (0x250, 0x2af, BLOCK_NAMES.ipa_extensions),
    (0x2b0, 0x2ff, BLOCK_NAMES.spacing_modifier_letters),
    (0x300, 0x36f, BLOCK_NAMES.combining_diacritical_marks),
    (0x370, 0x3ff, BLOCK_NAMES.greek_coptic),
    (0x400, 0x4ff, BLOCK_NAMES.cyrillic),
    (0x500, 0x52f, BLOCK_NAMES.cyrillic_supplement),
    (0x530, 0x58f, BLOCK_NAMES.armenian),
    (0x590, 0x5ff, BLOCK_NAMES.hebrew),
    (0x600, 0x6ff, BLOCK_NAMES.arabic),
    (0x700, 0x74f, BLOCK_NAMES.syriac),
    (0x750, 0x77f, BLOCK_NAMES.undefined),
    (0x780, 0x7bf, BLOCK_NAMES.thaana),
    (0x7c0, 0x8ff, BLOCK_NAMES.undefined),
    (0x900, 0x97f, BLOCK_NAMES.devanagari),
    (0x980, 0x9ff, BLOCK_NAMES.bengali_assamese),
    (0xa00, 0xa7f, BLOCK_NAMES.gurmukhi),
    (0xa80, 0xaff, BLOCK_NAMES.gujarati),
    (0xb00, 0xb7f, BLOCK_NAMES.oriya),
    (0xb80, 0xbff, BLOCK_NAMES.tamil),
    (0xc00, 0xc7f, BLOCK_NAMES.telugu),
    (0xc80, 0xcff, BLOCK_NAMES.kannada),
    (0xd00, 0xdff, BLOCK_NAMES.malayalam),
    (0xd80, 0xdff, BLOCK_NAMES.sinhala),
    (0xe00, 0xe7f, BLOCK_NAMES.thai),
    (0xe80, 0xeff, BLOCK_NAMES.lao),
    (0xf00, 0xfff, BLOCK_NAMES.tibetan),
    (0x1000, 0x109f, BLOCK_NAMES.myanmar),
    (0x10a0, 0x10ff, BLOCK_NAMES.georgian),
    (0x1100, 0x11ff, BLOCK_NAMES.hangul_jamo),
    (0x1200, 0x137f, BLOCK_NAMES.ethiopic),
    (0x1380, 0x139f, BLOCK_NAMES.undefined),
    (0x13a0, 0x13ff, BLOCK_NAMES.cherokee),
    (0x1400, 0x167f,
        BLOCK_NAMES.unified_canadian_aboriginal_syllabics),
    (0x1680, 0x169f, BLOCK_NAMES.ogham),
    (0x16a0, 0x16ff, BLOCK_NAMES.runic),
    (0x1700, 0x171f, BLOCK_NAMES.tagalog),
    (0x1720, 0x173f, BLOCK_NAMES.hanunoo),
    (0x1740, 0x175f, BLOCK_NAMES.buhid),
    (0x1760, 0x177f, BLOCK_NAMES.tagbanwa),
    (0x1780, 0x17ff, BLOCK_NAMES.khmer),
    (0x1800, 0x18af, BLOCK_NAMES.mongolian),
    (0x18b0, 0x18ff, BLOCK_NAMES.undefined),
    (0x1900, 0x194f, BLOCK_NAMES.limbu),
    (0x1950, 0x197f, BLOCK_NAMES.tai_le),
    (0x1980, 0x19df, BLOCK_NAMES.undefined),
    (0x19e0, 0x19ff, BLOCK_NAMES.khmer_symbols),
    (0x1a00, 0x1cff, BLOCK_NAMES.undefined),
    (0x1d00, 0x1d7f, BLOCK_NAMES.phonetic_extensions),
    (0x1d80, 0x1dff, BLOCK_NAMES.undefined),
    (0x1e00, 0x1eff, BLOCK_NAMES.latin_extended_additional),
    (0x1f00, 0x1fff, BLOCK_NAMES.greek_extended),
    (0x2000, 0x206f, BLOCK_NAMES.general_punctuation),
    (0x2070, 0x209f, BLOCK_NAMES.superscripts_and_subscripts),
    (0x20a0, 0x20cf, BLOCK_NAMES.currency_symbols),
    (0x20d0, 0x20ff,
        BLOCK_NAMES.combining_diacritical_marks_for_symbols),
    (0x2100, 0x214f, BLOCK_NAMES.letterlike_symbols),
    (0x2150, 0x218f, BLOCK_NAMES.number_forms),
    (0x2190, 0x21ff, BLOCK_NAMES.arrows),
    (0x2200, 0x22ff, BLOCK_NAMES.mathematical_operators),
    (0x2300, 0x23ff, BLOCK_NAMES.miscellaneous_technical),
    (0x2400, 0x243f, BLOCK_NAMES.control_pictures),
    (0x2440, 0x245f, BLOCK_NAMES.optical_character_recognition),
    (0x2460, 0x24ff, BLOCK_NAMES.enclosed_alphanumerics),
    (0x2500, 0x257f, BLOCK_NAMES.box_drawing),
    (0x2580, 0x259f, BLOCK_NAMES.block_elements),
    (0x25a0, 0x25ff, BLOCK_NAMES.geometric_shapes),
    (0x2600, 0x26ff, BLOCK_NAMES.miscellaneous_symbols),
    (0x2700, 0x27bf, BLOCK_NAMES.dingbats),
    (0x27c0, 0x27ef, BLOCK_NAMES.miscellaneous_mathematical_symbols_a),
    (0x27f0, 0x27ff, BLOCK_NAMES.supplemental_arrows_a),
    (0x2800, 0x28ff, BLOCK_NAMES.braille_patterns),
    (0x2900, 0x297f, BLOCK_NAMES.supplemental_arrows_b),
    (0x2980, 0x29ff, BLOCK_NAMES.miscellaneous_mathematical_symbols_b),
    (0x2a00, 0x2aff, BLOCK_NAMES.supplemental_mathematical_operators),
    (0x2b00, 0x2bff, BLOCK_NAMES.miscellaneous_symbols_and_arrows),
    (0x2c00, 0x2e7f, BLOCK_NAMES.undefined),
    (0x2e80, 0x2eff, BLOCK_NAMES.cjk_radicals_supplement),
    (0x2f00, 0x2fdf, BLOCK_NAMES.kangxi_radicals),
    (0x2fe0, 0x2fef, BLOCK_NAMES.undefined),
    (0x2ff0, 0x2fff, BLOCK_NAMES.ideographic_description_characters),
    (0x3000, 0x303f, BLOCK_NAMES.cjk_symbols_and_punctuation),
    (0x3040, 0x309f, BLOCK_NAMES.hiragana),
    (0x30a0, 0x30ff, BLOCK_NAMES.katakana),
    (0x3100, 0x312f, BLOCK_NAMES.bopomofo),
    (0x3130, 0x318f, BLOCK_NAMES.hangul_compatibility_jamo),
    (0x3190, 0x319f, BLOCK_NAMES.kanbun_kunten),
    (0x31a0, 0x31bf, BLOCK_NAMES.bopomofo_extended),
    (0x31c0, 0x31ef, BLOCK_NAMES.undefined),
    (0x31f0, 0x31ff, BLOCK_NAMES.katakana_phonetic_extensions),
    (0x3200, 0x32ff, BLOCK_NAMES.enclosed_cjk_letters_and_months),
    (0x3300, 0x33ff, BLOCK_NAMES.cjk_compatibility),
    (0x3400, 0x4dbf, BLOCK_NAMES.cjk_unified_ideographs_extension_a),
    (0x4dc0, 0x4dff, BLOCK_NAMES.yijing_hexagram_symbols),
    (0x4e00, 0x9faf, BLOCK_NAMES.cjk_unified_ideographs),
    (0x9fb0, 0x9fff, BLOCK_NAMES.undefined),
    (0xa000, 0xa48f, BLOCK_NAMES.yi_syllables),
    (0xa490, 0xa4cf, BLOCK_NAMES.yi_radicals),
    (0xa4d0, 0xabff, BLOCK_NAMES.undefined),
    (0xac00, 0xd7af, BLOCK_NAMES.hangul_syllables),
    (0xd7b0, 0xd7ff, BLOCK_NAMES.undefined),
    (0xd800, 0xdbff, BLOCK_NAMES.high_surrogate_area),
    (0xdc00, 0xdfff, BLOCK_NAMES.low_surrogate_area),
    (0xe000, 0xf8ff, BLOCK_NAMES.private_use_area),
    (0xf900, 0xfaff, BLOCK_NAMES.cjk_compatibility_ideographs),
    (0xfb00, 0xfb4f, BLOCK_NAMES.alphabetic_presentation_forms),
    (0xfb50, 0xfdff, BLOCK_NAMES.arabic_presentation_forms_a),
    (0xfe00, 0xfe0f, BLOCK_NAMES.variation_selectors),
    (0xfe10, 0xfe1f, BLOCK_NAMES.undefined),
    (0xfe20, 0xfe2f, BLOCK_NAMES.combining_half_marks),
    (0xfe30, 0xfe4f, BLOCK_NAMES.cjk_compatibility_forms),
    (0xfe50, 0xfe6f, BLOCK_NAMES.small_form_variants),
    (0xfe70, 0xfeff, BLOCK_NAMES.arabic_presentation_forms_b),
    (0xff00, 0xffef, BLOCK_NAMES.halfwidth_and_fullwidth_forms),
    (0xfff0, 0xffff, BLOCK_NAMES.specials),
    (0x10000, 0x1007f, BLOCK_NAMES.linear_b_syllabary),
    (0x10080, 0x100ff, BLOCK_NAMES.linear_b_ideograms),
    (0x10100, 0x1013f, BLOCK_NAMES.aegean_numbers),
    (0x10140, 0x102ff, BLOCK_NAMES.undefined),
    (0x10300, 0x1032f, BLOCK_NAMES.old_italic),
    (0x10330, 0x1034f, BLOCK_NAMES.gothic),
    (0x10380, 0x1039f, BLOCK_NAMES.ugaritic),
    (0x10400, 0x1044f, BLOCK_NAMES.deseret),
    (0x10450, 0x1047f, BLOCK_NAMES.shavian),
    (0x10480, 0x104af, BLOCK_NAMES.osmanya),
    (0x104b0, 0x107ff, BLOCK_NAMES.undefined),
    (0x10800, 0x1083f, BLOCK_NAMES.cypriot_syllabary),
    (0x10840, 0x1cfff, BLOCK_NAMES.undefined),
    (0x1d000, 0x1d0ff, BLOCK_NAMES.byzantine_musical_symbols),
    (0x1d100, 0x1d1ff, BLOCK_NAMES.musical_symbols),
    (0x1d200, 0x1d2ff, BLOCK_NAMES.undefined),
    (0x1d300, 0x1d35f, BLOCK_NAMES.tai_xuan_jing_symbols),
    (0x1d360, 0x1d3ff, BLOCK_NAMES.undefined),
    (0x1d400, 0x1d7ff, BLOCK_NAMES.mathematical_alphanumeric_symbols),
    (0x1d800, 0x1ffff, BLOCK_NAMES.undefined),
    (0x20000, 0x2a6df, BLOCK_NAMES.cjk_unified_ideographs_extension_b),
    (0x2a6e0, 0x2f7ff, BLOCK_NAMES.undefined),
    (0x2f800, 0x2fa1f,
        BLOCK_NAMES.cjk_compatibility_ideographs_supplement),
    (0x2fab0, 0xdffff, BLOCK_NAMES.unused),
    (0xe0000, 0xe007f, BLOCK_NAMES.tags),
    (0xe0080, 0xe00ff, BLOCK_NAMES.unused),
    (0xe0100, 0xe01ef, BLOCK_NAMES.variation_selectors_supplement),
    (0xe01f0, 0xeffff, BLOCK_NAMES.unused),
    (0xf0000, 0xffffd, BLOCK_NAMES.supplementary_private_use_area_a),
    (0xffffe, 0xfffff, BLOCK_NAMES.unused),
    (0x100000, 0x10fffd, BLOCK_NAMES.supplementary_private_use_area_b))


class UnicodeRange(object):
    """
    Iterable representation of a range of unicode codepoints.
    This can represent a standard Unicode Block, a standard Unicode Plane, or
    even a custom range.

    A UnicodeRange object contains a start, end, and name attribute
    which normally corresponds to the start and end integer for a
    range of Unicode codepoints.

    Each UnicodeRange object includes generators for performing common
    functions on the codepoints in that integer range.
    """
    def __init__(self, start, end, name):
        self.name = name
        self.start = start
        self.end = end

    def __str__(self):
        return '{0} {1} {2}'.format(
            hex(self.start), hex(self.end), str(self.name))

    def codepoints(self):
        """
        Generator that yields each codepoint in range as an integer.

        :rtype: generator, returns ints
        """
        for codepoint in range(self.start, self.end + 1):
            yield codepoint

    def codepoint_names(self):
        """
        Generator that yields the name of each codepoint in range as a string.

        If a name cannot be found, the codepoint's integer value is
        returned in hexidecimal format as a string.

        :rtype: generator, returns strings
        """
        for codepoint in self.codepoints():
            yield codepoint_name(codepoint)

    def encoded_codepoints(self, encoding='utf-8'):
        """
        Generator that yields each codepoint name in range, encoded.

        :param encoding: the encoding to use on the string
        :type encoding: string
        :rtype: generator, returns unicode strings
        """
        for codepoint in self.codepoints():
            yield six.unichr(codepoint).encode(encoding)


class UnicodeRangeList(list):
    """
    A list-like for containing collections of UnicodeRange objects.

    Allows iteration through all codepoins in collected ranged, even if the
    ranges are disjointed. Useful for for creating custom ranges for
    specialized testing.
    """

    def __str__(self):
        ret_str = '['
        for unicode_range in self:
            ret_str = '{0}<{1}>, '.format(ret_str, str(unicode_range))
        return '{0}]'.format(ret_str)

    def codepoints(self):
        """
        Generator that yields each codepoint in all ranges as an integer.

        :rtype: generator, returns ints
        """

        for unicode_range in self:
            for codepoint in unicode_range.codepoints():
                yield codepoint

    def codepoint_names(self):
        """
        Generator that yields the name of each codepoint in range as a string.

        If a name cannot be found, the codepoint's integer value is
        returned in hexidecimal format as a string.

        :rtype: generator, returns strings
        """

        for codepoint in self.codepoints():
            yield codepoint_name(codepoint)

    def encoded_codepoints(self, encoding='utf-8'):
        """
        Generator that yields each codepoint name in range, encoded.

        :param encoding: the encoding to use on the string
        :type encoding: string
        :rtype: generator, returns unicode strings
        """

        for codepoint in self.codepoints():
            yield six.unichr(codepoint).encode(encoding)

    def get_range(self, range_name):
        """
        Get a range of unicode codepoints by block name.

        Returns a single :class:`UnicodeRange` object representing the
        codepoints in the unicode block range named by :attr:`range_name`,
        if such a range exists in the instance of :class:`UnicodeRangeList`
        that :attr:`get_range` is being called from.

        :param range_name: name of the requested unicode block range.
        :type range_name: string
        :rtype: :class:`UnicodeRange` class instance, or None
        """

        for unicode_range in self:
            if unicode_range.name == range_name:
                return unicode_range

    def get_range_list(self, range_name_list):
        """
        Get a list of ranges of unicode codepoints by block names.

        Returns a single :class:`UnicodeRangeList` object representing the
        codepoints in the unicode block ranges named by
        :attr:`range_name_list`, if such ranges exists in the instance of
        :class:`UnicodeRangeList` that :attr:`get_range_list` is being called
        from.

        :param range_name_list: name(s) of requested unicode block ranges.
        :type range_name_list: list of strings
        :rtype: :class:`UnicodeRangeList` class instance, or :const:`None`
        """

        range_list = UnicodeRangeList()
        for unicode_range in self:
            if unicode_range.name in range_name_list:
                range_list.append(unicode_range)
        return range_list


# Initialize UNICODE_BLOCKS 'constant'
UNICODE_BLOCKS = UnicodeRangeList()
for _start, _end, _name in _unicode_blocks:
    UNICODE_BLOCKS.append(UnicodeRange(_start, _end, _name))

# Initialize UNICODE_PLANES 'constant'
UNICODE_PLANES = UnicodeRangeList()
for _start, _end, _name in _unicode_planes:
    UNICODE_PLANES.append(UnicodeRange(_start, _end, _name))


def codepoint_parent_plane(codepoint_integer):
    """
    Expects a Unicode codepoint as an integer.

    Return a UnicodeRangeList of UnicodeRange objects representing the
    unicode plane that codepoint_integer belongs to.
    """
    for plane in UNICODE_PLANES:
        if codepoint_integer >= plane.start and codepoint_integer <= plane.end:
            return plane


def codepoint_parent_block(codepoint_integer):
    """
    Expects a Unicode codepoint as an integer.

    Return a UnicodeRange object representing the unicode block that
    codepoint_integer belongs to.
    """
    for block in UNICODE_BLOCKS:
        if codepoint_integer >= block.start and codepoint_integer <= block.end:
            return block


def codepoint_name(codepoint_integer):
    """
    Expects a Unicode codepoint as an integer.

    Returns the unicode name of codepoint_integer if valid unicode codepoint,
    None otherwise

    If a name cannot be found, the codepoint's integer value is
    returned in hexidecimal format as a string.
    """

    if (codepoint_integer < UNICODE_STARTING_CODEPOINT) or\
            (codepoint_integer > (UNICODE_ENDING_CODEPOINT + 1)):
        return None

    return unicodedata.name(
        six.unichr(codepoint_integer), hex(codepoint_integer))

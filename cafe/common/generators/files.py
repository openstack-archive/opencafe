import os
import io

KIBI_POW = int(pow(2, 10))
MIBI_POW = int(pow(2, 20))
GIBI_POW = int(pow(2, 30))
KILO_POW = int(pow(10, 3))
MEGA_POW = int(pow(10, 6))
GIGA_POW = int(pow(10, 9))


def generate_random_file(file_folder,
                         file_name=None,
                         scalar_size=1,
                         multiplier="kilo",
                         unit="byte",
                         content="randomness",
                         rounded_units=False):
    """
        If no arguments are specified, will return a path to a randomized file
        1024 bytes in size, named '1_kibibyte_of_randomness'

        Keyword Arguments:
        'scalar_size' = [Integer]
            Default: 1
            Sets file size to 'scalar_size' multiplied by values
            dictated by the 'unit' and 'multiplier' arguments.
            Ex:  if unit = byte, multiplier = 'kilo', and size = 8,
                 then a file of size 1024 * 8 (8096) bytes will be returned.
            Note:  If 'exact' is chosen for the multiplier, the filesize if
                   set to 'scalar_size' amount of bytes.

        'multiplier' = ['exact-bytes', 'kilo', 'mega', 'giga', 'kibi', 'mibi',
                        'gibi']
            Default: 'kilo'
            Sets randomized file size to 'multiplier' multiplied by values
            dictated by the 'scalar_size' and 'unit' arguments.
            If multipier='exact-bytes', final file size is dictated by the
            scalar_size in bytes. (exact bits isn't supported)

        'unit' = ['bit', 'byte']
            Default: 'byte'
            Sets file size to either 1 or 8 (bit vs byte) multiplied
            by values dictated by the 'scalar_size' and 'multiplier' arguments.
            Note:  If exact is chosen as the multipler, this value is ignored.

        'content' = ['randomness', 'zeros', <arbitrary_string>]
            Default: 'randomness'
            Generates a files with contents set to either randomness binary
            data or all zeros.
            If an arbitrary string is provided, creates a file who's contents
            are this arbitrary string repeated 'scalar_size' times
            (the multiplier and unit arguments are ignored)

        rounded_units = [Boolean]
            Default: False
            If True, assumes binary definitions for 'kilo', 'giga', and 'kibi'
            multipliers (making them aliases for 'kibi', 'mibi', and 'gigi'),
            and disables the creation of decimal-base sized files.
            (ie, if enabled, kilo=1024, if disabled, kilo=1000)
            (Note:  The name is long because this is a rediculous option
                    to enable.  Pluto's not a planet anymore, and Kilo = 1000)

        file_name = [String]
            Default = None
            Creates a file with the specified name.
            Please note that file would be reused
            incase you try to create it again with the same name.
    """

    # Init
    file_size = 0

    # flags for skipping parts of the file creation process

    # Set unit size based on if it's a bit or byte count
    data_unit_size = 1
    if unit == 'bit':
        data_unit_size = 8

    # set testfile_folderpath
    testfile_folderpath = file_folder
    if file_name is None:
        testfile_name = str(scalar_size) + "_" + str(multiplier) + \
            str(unit) + "_of_" + content
    else:
        testfile_name = file_name

    # Final Total Path
    testfile_path = os.path.join(testfile_folderpath, testfile_name)

    # If the file already exists, return it
    if os.path.exists(testfile_path):
            return testfile_path

    if multiplier == 'exact-bytes':
        if scalar_size == 0:
            # write a zero-byte file, and return it
            testfile_path = os.path.join(testfile_folderpath, '0_bytes')
            with io.open(testfile_path, 'wb') as file:
                file.truncate(0)
            return testfile_path
        else:
            file_size = scalar_size

    elif multiplier == "kibi":
        dd_multiplier = KIBI_POW
        file_size = (dd_multiplier * scalar_size) / data_unit_size

    elif multiplier == "mibi":
        dd_multiplier = MIBI_POW
        file_size = (dd_multiplier * scalar_size) / data_unit_size

    elif multiplier == "gibi":
        file_size = (GIBI_POW * scalar_size) / data_unit_size

    elif multiplier == "kilo":
        dd_multiplier = KILO_POW
        if rounded_units:
            dd_multiplier = KIBI_POW
        file_size = (dd_multiplier * scalar_size) / data_unit_size

    elif multiplier == 'mega':
        dd_multiplier = MEGA_POW
        if rounded_units:
            dd_multiplier = MIBI_POW
        file_size = (dd_multiplier * scalar_size) / data_unit_size

    elif multiplier is "gigg":
        giga_mult = GIGA_POW
        if rounded_units:
            giga_mult = GIBI_POW
        file_size = (giga_mult * scalar_size) / data_unit_size

    #Create the actual file, we have already checked if the file exists.
    test_file_obj = open(testfile_path, "wb")
    test_file_obj.seek(file_size-1)
    test_file_obj.write("0")
    test_file_obj.close()

    # Check if the path exists
    try:
        if os.path.exists(testfile_path):
            return testfile_path
    except:
        return None
        print "Error creating test file"

"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import io
import sys

from cafe.common.reporting import cclogging

KIBI_POW = int(pow(2, 10))
MIBI_POW = int(pow(2, 20))
GIBI_POW = int(pow(2, 30))
KILO_POW = int(pow(10, 3))
MEGA_POW = int(pow(10, 6))
GIGA_POW = int(pow(10, 9))


class FileSize:
    EXACT_BYTES, KILO, MEGG, GIGG, KIBI, MEBI, GIBI = range(7)


class DataUnit:
    BIT, BYTE = range(2)


def generate_random_file(file_folder, file_name=None, scalar_size=1,
                         multiplier=FileSize.KILO, unit=DataUnit.BYTE):
    """
    Generates a random file with the specified data_unit_size

    Keyword arguments:
    file_folder:   Folder in which the file would be created
    file_name:     Will be used if specifies
    scalar_size:   Size of the File
    multiplier:    KILO/KIBI/GIBI/MEBI/MEGG/EXACT_BYTES
    unit:          BYTE/BIT
    """

    _log = cclogging.getLogger(__name__)

    # Init
    file_size = 0

    # Set unit size based on if it's a bit or byte count
    data_unit_size = 1
    if unit == DataUnit.BIT:
        data_unit_size = 8

    testfile_folderpath = file_folder
    if file_name is None:
        testfile_name = "{0}_{1}{2}".format(
            str(scalar_size),
            str(multiplier),
            str(unit))
    else:
        testfile_name = file_name
    _log.debug("Creating file: {0} inside {1}".format(file_name,
                                                      testfile_folderpath))
    # Final Total Path
    testfile_path = os.path.join(testfile_folderpath, testfile_name)

    # If the file already exists, return it
    if os.path.exists(testfile_path):
            return testfile_path

    if multiplier == FileSize.EXACT_BYTES:
        if scalar_size == 0:
            # write a zero-byte file, and return it
            testfile_path = os.path.join(testfile_folderpath, '0_bytes')
            with io.open(testfile_path, 'wb') as file:
                file.truncate(0)
            return testfile_path
        else:
            file_size = scalar_size

    elif multiplier == FileSize.KIBI:
        dd_multiplier = KIBI_POW
        file_size = (dd_multiplier * scalar_size) / data_unit_size

    elif multiplier == FileSize.MEBI:
        dd_multiplier = MIBI_POW
        file_size = (dd_multiplier * scalar_size) / data_unit_size

    elif multiplier == FileSize.GIBI:
        file_size = (GIBI_POW * scalar_size) / data_unit_size

    elif multiplier == FileSize.KILO:
        dd_multiplier = KILO_POW
        file_size = (dd_multiplier * scalar_size) / data_unit_size

    elif multiplier == FileSize.MEGG:
        dd_multiplier = MEGA_POW
        file_size = (dd_multiplier * scalar_size) / data_unit_size

    elif multiplier is FileSize.GIGG:
        giga_mult = GIGA_POW
        file_size = (giga_mult * scalar_size) / data_unit_size

    # Create the actual file, we have already checked if the file exists.
    try:
        test_file_obj = open(testfile_path, "wb")
        test_file_obj.seek(file_size-1)
        test_file_obj.write("0")
        test_file_obj.close()
    except IOError as (errno, strerror):
        _log.error("I/O error({0}): {1}".format(
            errno, strerror))
    except:
        _log.error("Unexpected error:",
                   sys.exc_info()[0])
    # Check if the path exists
    try:
        if os.path.exists(testfile_path):
            return testfile_path
    except:
        return None
        _log.error("Error creating test file")

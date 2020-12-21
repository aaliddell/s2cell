# Copyright 2020 Adam Liddell
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import csv
import gzip
import pathlib
import re
import sys

import numpy as np
import pytest
import s2cell


def test_invalid_cell_id_to_token():
    with pytest.raises(TypeError, match=re.escape("Cannot convert S2 cell ID from type: <class 'float'>")):
        s2cell.cell_id_to_token(1.0)


def test_cell_id_to_token_compat():
    # Check against generated S2 tests
    encode_file = pathlib.Path(__file__).parent / 's2_encode_corpus.csv.gz'
    with gzip.open(str(encode_file), 'rt') as f:
        for row in csv.DictReader(f):
            assert s2cell.cell_id_to_token(int(row['cell_id'])) == row['token']


def test_zero_token_to_cell_id():
    assert s2cell.token_to_cell_id('x') == 0
    assert s2cell.token_to_cell_id('X') == 0


def test_invalid_token_to_cell_id():
    with pytest.raises(TypeError, match=re.escape("Cannot convert S2 token from type: <class 'float'>")):
        s2cell.token_to_cell_id(1.0)


def test_token_to_cell_id_compat():
    # Check against generated S2 tests
    encode_file = pathlib.Path(__file__).parent / 's2_encode_corpus.csv.gz'
    with gzip.open(str(encode_file), 'rt') as f:
        for row in csv.DictReader(f):
            assert s2cell.token_to_cell_id(row['token']) == int(row['cell_id'])


def test_invalid_lat_lon_to_cell_id():
    # Invalid level
    with pytest.raises(ValueError, match=re.escape('S2 level must be integer >= 0 and <= 30')):
        s2cell.lat_lon_to_cell_id(0, 0, level=-1)

    with pytest.raises(ValueError, match=re.escape('S2 level must be integer >= 0 and <= 30')):
        s2cell.lat_lon_to_cell_id(0, 0, level=31)

    with pytest.raises(ValueError, match=re.escape('S2 level must be integer >= 0 and <= 30')):
        s2cell.lat_lon_to_cell_id(0, 0, level='a')


def test_lat_lon_to_cell_id_compat():
    # Check against generated S2 tests
    encode_file = pathlib.Path(__file__).parent / 's2_encode_corpus.csv.gz'
    with gzip.open(str(encode_file), 'rt') as f:
        for row in csv.DictReader(f):
            assert s2cell.lat_lon_to_cell_id(
                float(row['lat']), float(row['lon']), int(row['level'])
            ) == int(row['cell_id'])


def test_invalid_lat_lon_to_token():
    # Invalid level
    with pytest.raises(ValueError, match=re.escape('S2 level must be integer >= 0 and <= 30')):
        s2cell.lat_lon_to_token(0, 0, level=-1)

    with pytest.raises(ValueError, match=re.escape('S2 level must be integer >= 0 and <= 30')):
        s2cell.lat_lon_to_token(0, 0, level=31)

    with pytest.raises(ValueError, match=re.escape('S2 level must be integer >= 0 and <= 30')):
        s2cell.lat_lon_to_token(0, 0, level='a')


def test_lat_lon_to_token_compat():
    # Check against generated S2 tests
    encode_file = pathlib.Path(__file__).parent / 's2_encode_corpus.csv.gz'
    with gzip.open(str(encode_file), 'rt') as f:
        for row in csv.DictReader(f):
            assert s2cell.lat_lon_to_token(
                float(row['lat']), float(row['lon']), int(row['level'])
            ) == row['token']


def test_invalid_cell_id_to_lat_lon():
    with pytest.raises(TypeError, match=re.escape("Cannot decode S2 cell ID from type: <class 'float'>")):
        s2cell.cell_id_to_lat_lon(1.0)

    with pytest.raises(ValueError, match=re.escape("Cannot decode S2 cell ID with invalid face: 6")):
        s2cell.cell_id_to_lat_lon(int(0b110 << s2cell._S2_POS_BITS))


def test_cell_id_to_lat_lon_compat():
    decode_file = pathlib.Path(__file__).parent / 's2_decode_corpus.csv.gz'
    with gzip.open(str(decode_file), 'rt') as f:
        for row in csv.DictReader(f):
            ll_tuple = s2cell.cell_id_to_lat_lon(int(row['cell_id']))
            expected_tuple = (float(row['lat']), float(row['lon']))

            # MacOS and Windows has slightly different rounding performance
            if sys.platform in ('darwin', 'win32'):
                assert ll_tuple == pytest.approx(expected_tuple, abs=1e-12, rel=0.0)
            else:
                assert ll_tuple == expected_tuple


def test_invalid_token_to_lat_lon():
    with pytest.raises(TypeError, match=re.escape("Cannot convert S2 token from type: <class 'float'>")):
        s2cell.token_to_lat_lon(1.0)

    with pytest.raises(ValueError, match=re.escape('Cannot convert S2 token with length > 16 characters')):
        s2cell.token_to_lat_lon('a' * 17)

    with pytest.raises(ValueError, match=re.escape("Cannot decode S2 cell ID with invalid face: 6")):
        s2cell.token_to_lat_lon('{:016x}'.format(np.uint64(0b110 << s2cell._S2_POS_BITS)))


def test_token_to_lat_lon_compat():
    decode_file = pathlib.Path(__file__).parent / 's2_decode_corpus.csv.gz'
    with gzip.open(str(decode_file), 'rt') as f:
        for row in csv.DictReader(f):
            ll_tuple = s2cell.token_to_lat_lon(row['token'])
            expected_tuple = (float(row['lat']), float(row['lon']))

            # MacOS and Windows has slightly different rounding performance
            if sys.platform in ('darwin', 'win32'):
                assert ll_tuple == pytest.approx(expected_tuple, abs=1e-12, rel=0.0)
            else:
                assert ll_tuple == expected_tuple


def test_invalid_cell_id_to_level():
    with pytest.raises(TypeError, match=re.escape("Cannot decode S2 cell ID from type: <class 'float'>")):
        s2cell.cell_id_to_level(1.0)

    with pytest.raises(ValueError, match=re.escape("Cannot decode invalid S2 cell ID: 0")):
        s2cell.cell_id_to_level(0)


def test_cell_id_to_level():
    # Check against generated S2 tests
    encode_file = pathlib.Path(__file__).parent / 's2_encode_corpus.csv.gz'
    with gzip.open(str(encode_file), 'rt') as f:
        for row in csv.DictReader(f):
            assert s2cell.cell_id_to_level(int(row['cell_id'])) == int(row['level'])


def test_invalid_token_to_level():
    with pytest.raises(TypeError, match=re.escape("Cannot convert S2 token from type: <class 'float'>")):
        s2cell.token_to_level(1.0)

    with pytest.raises(ValueError, match=re.escape('Cannot convert S2 token with length > 16 characters')):
        s2cell.token_to_level('a' * 17)

    with pytest.raises(ValueError, match=re.escape("Cannot decode invalid S2 cell ID: 0")):
        s2cell.token_to_level('')


def test_token_to_level():
    # Check against generated S2 tests
    encode_file = pathlib.Path(__file__).parent / 's2_encode_corpus.csv.gz'
    with gzip.open(str(encode_file), 'rt') as f:
        for row in csv.DictReader(f):
            assert s2cell.token_to_level(row['token']) == int(row['level'])

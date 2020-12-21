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
import pathlib
import re
import sys

import pytest
import s2cell


@pytest.mark.parametrize('lat, lon, level, expected', [
    (0, 0, 0, 1152921504606846976),
    (0, 0, 30, 1152921504606846977),
    (45, 45, 30, 4635422624767557889),
    (-45, -45, 30, 13811321448941993727),
    (90, -180, 30, 5764607523034234881),
    (12.3456789, 12.3456789, 30, 1226158516923251567),
])
def test_lat_lon_to_cell_id(lat, lon, level, expected):
    cell_id = s2cell.lat_lon_to_cell_id(lat, lon, level=level)
    assert cell_id == expected


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
    encode_file = pathlib.Path(__file__).parent / 's2_encode_corpus.csv'
    with encode_file.open() as f:
        for row in csv.DictReader(f):
            assert s2cell.lat_lon_to_cell_id(
                float(row['lat']), float(row['lon']), int(row['level'])
            ) == int(row['cell_id'])


@pytest.mark.parametrize('lat, lon, level, expected', [
    (0, 0, 0, '1'),
    (0, 0, 30, '1000000000000001'),
    (45, 45, 30, '4054545155144101'),
    (-45, -45, 30, 'bfababaeaaebbeff'),
    (90, -180, 30, '5000000000000001'),
    (12.3456789, 12.3456789, 30, '110430acb787bb6f'),
])
def test_lat_lon_to_token(lat, lon, level, expected):
    cell_id = s2cell.lat_lon_to_token(lat, lon, level=level)
    assert cell_id == expected


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
    encode_file = pathlib.Path(__file__).parent / 's2_encode_corpus.csv'
    with encode_file.open() as f:
        for row in csv.DictReader(f):
            assert s2cell.lat_lon_to_token(
                float(row['lat']), float(row['lon']), int(row['level'])
            ) == row['token']


def test_cell_id_to_lat_lon_invalid():
    with pytest.raises(TypeError, match=re.escape("Cannot decode S2 cell ID from type: <class 'float'>")):
        s2cell.cell_id_to_lat_lon(1.0)


def test_cell_id_to_lat_lon_compat():
    decode_file = pathlib.Path(__file__).parent / 's2_decode_corpus.csv'
    with decode_file.open() as f:
        for row in csv.DictReader(f):
            ll_tuple = s2cell.cell_id_to_lat_lon(int(row['cell_id']))
            expected_tuple = (float(row['lat']), float(row['lon']))

            # MacOS has slightly different rounding performance
            if sys.platform == 'darwin':
                assert ll_tuple == pytest.approx(expected_tuple, abs=1e-12, rel=0.0)
            else:
                assert ll_tuple == expected_tuple


def test_token_to_lat_lon_invalid():
    with pytest.raises(TypeError, match=re.escape("Cannot decode S2 token from type: <class 'float'>")):
        s2cell.token_to_lat_lon(1.0)

    with pytest.raises(ValueError, match=re.escape('Cannot decode S2 token with length > 16 characters')):
        s2cell.token_to_lat_lon('a' * 17)


def test_token_to_lat_lon_compat():
    decode_file = pathlib.Path(__file__).parent / 's2_decode_corpus.csv'
    with decode_file.open() as f:
        for row in csv.DictReader(f):
            ll_tuple = s2cell.token_to_lat_lon(row['token'])
            expected_tuple = (float(row['lat']), float(row['lon']))

            # MacOS has slightly different rounding performance
            if sys.platform == 'darwin':
                assert ll_tuple == pytest.approx(expected_tuple, abs=1e-12, rel=0.0)
            else:
                assert ll_tuple == expected_tuple

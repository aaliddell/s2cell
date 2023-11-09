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

import collections
import csv
import gzip
import pathlib
import re

import pytest
import s2cell
from s2cell.s2cell import _S2_POS_BITS, _s2_face_uv_to_xyz


def test_invalid__s2_face_uv_to_xyz():
    with pytest.raises(ValueError, match=re.escape('Cannot convert UV to XYZ with invalid face: 6')):
        _s2_face_uv_to_xyz(6, (0, 0))


def test_zero_cell_id_to_token():
    assert s2cell.cell_id_to_token(0) == 'X'


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

    with pytest.raises(s2cell.InvalidToken, match=re.escape('Cannot convert S2 token with length > 16 characters')):
        s2cell.token_to_cell_id('a' * 17)


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

    with pytest.raises(s2cell.InvalidCellID, match=re.escape('Cannot decode invalid S2 cell ID: 13835058055282163712')):
        s2cell.cell_id_to_lat_lon(int(0b110 << _S2_POS_BITS))


def test_cell_id_to_lat_lon_compat():
    decode_file = pathlib.Path(__file__).parent / 's2_decode_corpus.csv.gz'
    with gzip.open(str(decode_file), 'rt') as f:
        for row in csv.DictReader(f):
            ll_tuple = s2cell.cell_id_to_lat_lon(int(row['cell_id']))
            expected_tuple = (float(row['lat']), float(row['lon']))
            assert ll_tuple == pytest.approx(expected_tuple, abs=1e-12, rel=0.0)


def test_invalid_token_to_lat_lon():
    with pytest.raises(TypeError, match=re.escape("Cannot check S2 token with type: <class 'float'>")):
        s2cell.token_to_lat_lon(1.0)

    with pytest.raises(s2cell.InvalidToken, match=re.escape('Cannot decode invalid S2 token: aaaaaaaaaaaaaaaaa')):
        s2cell.token_to_lat_lon('a' * 17)

    with pytest.raises(s2cell.InvalidToken, match=re.escape('Cannot decode invalid S2 token: c000000000000000')):
        s2cell.token_to_lat_lon('{:016x}'.format(0b110 << _S2_POS_BITS))


def test_token_to_lat_lon_compat():
    decode_file = pathlib.Path(__file__).parent / 's2_decode_corpus.csv.gz'
    with gzip.open(str(decode_file), 'rt') as f:
        for row in csv.DictReader(f):
            ll_tuple = s2cell.token_to_lat_lon(row['token'])
            expected_tuple = (float(row['lat']), float(row['lon']))
            assert ll_tuple == pytest.approx(expected_tuple, abs=1e-12, rel=0.0)


@pytest.mark.parametrize('token, expected', [
    ('3', '3'),
    ('2ef59bd352b93ac3', '2ef59bd352b93ac3'),
    ('  2ef59bd352b93ac3', '2ef59bd352b93ac3'),
    ('2ef59bd352b93ac3  ', '2ef59bd352b93ac3'),
    (' 2ef59bd352b93ac3 ', '2ef59bd352b93ac3'),
    ('2EF', '2ef'),
    ('2eF', '2ef'),
    ('2ef000', '2ef'),
    ('', 'X'),
    ('x', 'X'),
])
def test_token_to_canonical_token(token, expected):
    assert s2cell.token_to_canonical_token(token) == expected


@pytest.mark.parametrize('cell_id, is_valid', [
    (0b1111010101010101010101010101010101010101010101010101010101010101, False),  # Invalid face
    (0, False),
] + [
    (1 << even_number, True) for even_number in range(0, _S2_POS_BITS, 2)
] + [
    (1 << odd_number, False) for odd_number in range(1, _S2_POS_BITS, 2)
])
def test_cell_id_is_valid(cell_id, is_valid):
    assert s2cell.cell_id_is_valid(cell_id) == is_valid


def test_cell_id_is_valid_compat():
    decode_file = pathlib.Path(__file__).parent / 's2_decode_corpus.csv.gz'
    with gzip.open(str(decode_file), 'rt') as f:
        for row in csv.DictReader(f):
            assert s2cell.cell_id_is_valid(int(row['cell_id']))


@pytest.mark.parametrize('token, is_valid', [
    ('', False),  # Invalid cell ID
    ('x', False),  # Invalid cell ID
    ('X', False),  # Invalid cell ID
    ('2ef', True),
    ('2EF', True),
    ('2ef0000000000000', True),
    ('2ef00000000000000', False),  # Too long
    ('2efinvalid', False),  # Invalid characters
    ('86R', False),  # Invalid hex
    ('2efx', False),  # Incorrect use of X
])
def test_token_is_valid(token, is_valid):
    assert s2cell.token_is_valid(token) == is_valid


def test_token_is_valid_compat():
    decode_file = pathlib.Path(__file__).parent / 's2_decode_corpus.csv.gz'
    with gzip.open(str(decode_file), 'rt') as f:
        for row in csv.DictReader(f):
            assert s2cell.token_is_valid(row['token'])


def test_invalid_cell_id_to_level():
    with pytest.raises(TypeError, match=re.escape("Cannot decode S2 cell ID from type: <class 'float'>")):
        s2cell.cell_id_to_level(1.0)

    with pytest.raises(s2cell.InvalidCellID, match=re.escape("Cannot decode invalid S2 cell ID: 0")):
        s2cell.cell_id_to_level(0)


def test_cell_id_to_level_compat():
    # Check against generated S2 tests
    encode_file = pathlib.Path(__file__).parent / 's2_encode_corpus.csv.gz'
    with gzip.open(str(encode_file), 'rt') as f:
        for row in csv.DictReader(f):
            assert s2cell.cell_id_to_level(int(row['cell_id'])) == int(row['level'])


def test_invalid_token_to_level():
    with pytest.raises(TypeError, match=re.escape("Cannot check S2 token with type: <class 'float'>")):
        s2cell.token_to_level(1.0)

    with pytest.raises(s2cell.InvalidToken, match=re.escape('Cannot decode invalid S2 token: aaaaaaaaaaaaaaaaa')):
        s2cell.token_to_level('a' * 17)

    with pytest.raises(s2cell.InvalidToken, match=re.escape('Cannot decode invalid S2 token: ')):
        s2cell.token_to_level('')


def test_token_to_level_compat():
    # Check against generated S2 tests
    encode_file = pathlib.Path(__file__).parent / 's2_encode_corpus.csv.gz'
    with gzip.open(str(encode_file), 'rt') as f:
        for row in csv.DictReader(f):
            assert s2cell.token_to_level(row['token']) == int(row['level'])


def test_invalid_cell_id_to_parent_cell_id():
    with pytest.raises(TypeError, match=re.escape("Cannot decode S2 cell ID from type: <class 'float'>")):
        s2cell.cell_id_to_parent_cell_id(1.0)

    with pytest.raises(s2cell.InvalidCellID, match=re.escape('Cannot decode invalid S2 cell ID: 0')):
        s2cell.cell_id_to_parent_cell_id(0)

    with pytest.raises(ValueError, match=re.escape('Cannot get parent cell ID of a level 0 cell ID')):
        s2cell.cell_id_to_parent_cell_id(3458764513820540928)

    with pytest.raises(ValueError, match=re.escape('S2 level must be integer >= 0 and <= 30')):
        s2cell.cell_id_to_parent_cell_id(3383782026652942336, 'a')

    with pytest.raises(ValueError, match=re.escape('S2 level must be integer >= 0 and <= 30')):
        s2cell.cell_id_to_parent_cell_id(3383782026652942336, -1)

    with pytest.raises(ValueError, match=re.escape('S2 level must be integer >= 0 and <= 30')):
        s2cell.cell_id_to_parent_cell_id(3383782026652942336, 31)

    with pytest.raises(ValueError, match=re.escape('Cannot get level 16 parent cell ID of cell ID with level 15')):
        s2cell.cell_id_to_parent_cell_id(3383782026652942336, 16)


def test_cell_id_to_parent_cell_id_compat():
    # Check against generated S2 tests
    encode_file = pathlib.Path(__file__).parent / 's2_encode_corpus.csv.gz'
    with gzip.open(str(encode_file), 'rt') as f:
        points = collections.defaultdict(dict)
        for row in csv.DictReader(f):
            points[(float(row['lat']), float(row['lon']))][int(row['level'])] = int(row['cell_id'])

    for levels_dict in list(points.values())[::200]:
        for level in levels_dict:
            # Test direct parent
            if level > 0:
                assert s2cell.cell_id_to_parent_cell_id(levels_dict[level]) == levels_dict[level - 1]
            else:
                with pytest.raises(ValueError, match=re.escape('Cannot get parent cell ID of a level 0 cell ID')):
                    s2cell.cell_id_to_parent_cell_id(levels_dict[level])

            # Test all other levels
            for other_level in levels_dict:
                if other_level <= level:
                    assert s2cell.cell_id_to_parent_cell_id(levels_dict[level], other_level) == levels_dict[other_level]
                else:
                    with pytest.raises(ValueError, match=re.escape('Cannot get level {} parent cell ID of cell ID with level {}'.format(other_level, level))):
                        s2cell.cell_id_to_parent_cell_id(levels_dict[level], other_level)


def test_invalid_token_to_parent_token():
    with pytest.raises(TypeError, match=re.escape("Cannot check S2 token with type: <class 'float'>")):
        s2cell.token_to_parent_token(1.0)

    with pytest.raises(s2cell.InvalidToken, match=re.escape('Cannot decode invalid S2 token: aaaaaaaaaaaaaaaaa')):
        s2cell.token_to_parent_token('a' * 17)

    with pytest.raises(ValueError, match=re.escape('Cannot get parent cell ID of a level 0 cell ID')):
        s2cell.token_to_parent_token('3')

    with pytest.raises(ValueError, match=re.escape('S2 level must be integer >= 0 and <= 30')):
        s2cell.token_to_parent_token('2ef59bd34', 'a')

    with pytest.raises(ValueError, match=re.escape('S2 level must be integer >= 0 and <= 30')):
        s2cell.token_to_parent_token('2ef59bd34', -1)

    with pytest.raises(ValueError, match=re.escape('S2 level must be integer >= 0 and <= 30')):
        s2cell.token_to_parent_token('2ef59bd34', 31)

    with pytest.raises(ValueError, match=re.escape('Cannot get level 16 parent cell ID of cell ID with level 15')):
        s2cell.token_to_parent_token('2ef59bd34', 16)


def test_token_to_parent_token_compat():
    # Check against generated S2 tests
    encode_file = pathlib.Path(__file__).parent / 's2_encode_corpus.csv.gz'
    with gzip.open(str(encode_file), 'rt') as f:
        points = collections.defaultdict(dict)
        for row in csv.DictReader(f):
            points[(float(row['lat']), float(row['lon']))][int(row['level'])] = row['token']

    for levels_dict in list(points.values())[::200]:
        for level in levels_dict:
            # Test direct parent
            if level > 0:
                assert s2cell.token_to_parent_token(levels_dict[level]) == levels_dict[level - 1]
            else:
                with pytest.raises(ValueError, match=re.escape('Cannot get parent cell ID of a level 0 cell ID')):
                    s2cell.token_to_parent_token(levels_dict[level])

            # Test all other levels
            for other_level in levels_dict:
                if other_level <= level:
                    assert s2cell.token_to_parent_token(levels_dict[level], other_level) == levels_dict[other_level]
                else:
                    with pytest.raises(ValueError, match=re.escape('Cannot get level {} parent cell ID of cell ID with level {}'.format(other_level, level))):
                        s2cell.token_to_parent_token(levels_dict[level], other_level)


def test_s2_cell_id_to_neighbor_cell_ids_edge():
    # s2geometry/blob/7773d518b1f29caa1c2045eb66ec519e025be108/src/python/s2geometry_test.py#L66-L73
    cell = 0x466d319000000000
    expected_neighbors = [  # Order is guaranteed for edge only
        0x466d31b000000000,
        0x466d317000000000,
        0x466d323000000000,
        0x466d31f000000000,
    ]
    neighbors = s2cell.cell_id_to_neighbor_cell_ids(cell)
    assert neighbors == expected_neighbors


def test_s2_cell_id_to_neighbor_cell_ids_all():
    # s2geometry/blob/7773d518b1f29caa1c2045eb66ec519e025be108/src/python/s2geometry_test.py#L86-L99
    cell = 0x466d319000000000
    expected_neighbors = {  # Order is not guaranteed for non-edge only
        0x466d31d000000000,
        0x466d311000000000,
        0x466d31b000000000,
        0x466d323000000000,
        0x466d31f000000000,
        0x466d317000000000,
        0x466d321000000000,
        0x466d33d000000000,
    }
    assert s2cell.cell_id_to_level(cell) == 12
    neighbors = set(s2cell.cell_id_to_neighbor_cell_ids(cell, corner=True))
    assert neighbors == expected_neighbors

    # s2geometry/blob/7773d518b1f29caa1c2045eb66ec519e025be108/src/python/s2geometry_test.py#L146-L157
    cell = 0x6aa7590000000000
    expected_neighbors = {  # Order is not guaranteed for non-edge only
        0x2ab3530000000000,
        0x2ab34b0000000000,
        0x2ab34d0000000000,
        0x6aa75b0000000000,
        0x6aa7570000000000,
        0x6aa75f0000000000,
        0x6aa7510000000000,
        0x6aa75d0000000000,
    }
    neighbors = sorted(s2cell.cell_id_to_neighbor_cell_ids(cell, corner=True))
    assert neighbors == expected_neighbors


def test_s2_cell_id_to_neighbor_cell_ids_at_cube_corner():
    cell = 0x4aac000000000000
    expected_neighbors = [  # Order is guaranteed for edge only
        0x0aac000000000000,
        0x4aa4000000000000,
        0x4ab4000000000000,
        0x8aac000000000000,
    ]
    neighbors = s2cell.cell_id_to_neighbor_cell_ids(cell, edge=True, corner=False)
    assert neighbors == expected_neighbors

    expected_neighbors = {
        0x0ab4000000000000,
        0x4abc000000000000,
        0x8aa4000000000000,
    }
    neighbors = set(s2cell.cell_id_to_neighbor_cell_ids(cell, edge=False, corner=True))
    assert neighbors == expected_neighbors

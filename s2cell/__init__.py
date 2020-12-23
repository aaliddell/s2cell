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

"""Minimal Python S2 cell ID, S2 token and lat/lon conversion library."""

import math
from typing import Tuple, Union

import numpy as np

__version__ = '1.1.1'


#
# S2 base constants needed for cell mapping
#

# The maximum level supported within an S2 cell ID. Each level is represented by two bits in the
# final cell ID
_S2_MAX_LEVEL = np.uint32(30)

# The maximum value within the I and J bits of an S2 cell ID
_S2_MAX_SIZE = np.uint32(1) << _S2_MAX_LEVEL

# The number of bits in a S2 cell ID used for specifying the base face
_S2_FACE_BITS = np.uint32(3)

# The number of bits in a S2 cell ID used for specifying the position along the Hilbert curve
_S2_POS_BITS = np.uint32(2 * _S2_MAX_LEVEL + 1)

# The maximum value of the Si/Ti integers used when mapping from IJ to ST. This is twice the max
# value of I and J, since Si/Ti allow referencing both the centre and edge of a leaf cell
_S2_MAX_SI_TI = np.uint32(1) << (_S2_MAX_LEVEL + 1)

# Mask that specifies the swap orientation bit for the Hilbert curve
_S2_SWAP_MASK = np.uint64(1)

# Mask that specifies the invert orientation bit for the Hilbert curve
_S2_INVERT_MASK = np.uint64(2)

# The number of bits per I and J in the lookup tables
_S2_LOOKUP_BITS = np.uint32(4)

# Lookup table for mapping 10 bits of IJ + orientation to 10 bits of Hilbert curve position +
# orientation. Populated later by _s2_init_lookups
_S2_LOOKUP_POS = None

# Lookup table for mapping 10 bits of Hilbert curve position + orientation to 10 bits of IJ +
# orientation. Populated later by _s2_init_lookups
_S2_LOOKUP_IJ = None

# Lookup table of two bits of IJ from two bits of curve position, based also on the current curve
# orientation from the swap and invert bits
_S2_POS_TO_IJ = np.array([
    [0, 1, 3, 2],  # 0: Normal order, no swap or invert
    [0, 2, 3, 1],  # 1: Swap bit set, swap I and J bits
    [3, 2, 0, 1],  # 2: Invert bit set, invert bits
    [3, 1, 0, 2],  # 3: Swap and invert bits set
], dtype=np.uint64)

# Lookup for the orientation update mask of one of the four sub-cells within a higher level cell.
# This mask is XOR'ed with the current orientation to get the sub-cell orientation.
_S2_POS_TO_ORIENTATION_MASK = np.array([
    _S2_SWAP_MASK, 0, 0, _S2_SWAP_MASK | _S2_INVERT_MASK
], dtype=np.uint64)


#
# S2 helper functions
#

def _s2_uv_to_st(component: float) -> float:
    """
    Convert S2 UV to ST.

    This is done using the quadratic projection that is used by default for S2. The C++ and Java S2
    libraries use a different definition of the ST cell-space, but the end result in IJ is the same.
    The below uses the C++ ST definition.

    See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2coords.h#L317-L320

    """
    if component >= 0.0:
        return 0.5 * math.sqrt(1.0 + 3.0 * component)
    return 1.0 - 0.5 * math.sqrt(1.0 - 3.0 * component)


def _s2_st_to_uv(component: float) -> float:
    """
    Convert S2 ST to UV.

    This is done using the quadratic projection that is used by default for S2. The C++ and Java S2
    libraries use a different definition of the ST cell-space, but the end result in IJ is the same.
    The below uses the C++ ST definition.

    See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2coords.h#L312-L315

    """
    if component >= 0.5:
        return (1.0 / 3.0) * (4.0 * component ** 2 - 1.0)
    return (1.0 / 3.0) * (1.0 - 4.0 * (1.0 - component) ** 2)


def _s2_st_to_ij(component: float) -> np.uint64:
    """
    Convert S2 ST to IJ.

    The mapping here differs between C++ and Java versions, but the combination of
    _st_to_ij(_uv_to_st(val)) is the same for both. The below uses the C++ ST definition.

    See s2geometry/blob/2c02e21040e0b82aa5719e96033d02b8ce7c0eff/src/s2/s2coords.h#L333-L336

    """
    return np.uint64(max(0, min(_S2_MAX_SIZE - 1, round(_S2_MAX_SIZE * component - 0.5))))


def _s2_si_ti_to_st(component: np.uint64) -> float:
    """
    Convert S2 Si/Ti to ST.

    This converts an integer in range 0 to _S2_MAX_SI_TI into a float in range 0.0 to 1.0.

    See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2coords.h#L338-L341

    """
    return (1.0 / _S2_MAX_SI_TI) * component


def _s2_face_uv_to_xyz(  # pylint: disable=invalid-name
        face: Union[int, np.uint64], uv: Tuple[float, float]
) -> Tuple[float, float, float]:
    """
    Convert face + UV to S2Point XYZ.

    See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2coords.h#L348-L357

    Args:
        face: The S2 face for the input point.
        uv: The S2 face UV coordinates.

    Returns:
        The unnormalised S2Point XYZ.

    Raises:
        ValueError: If the face is not valid in range 0-5.

    """
    # Face -> XYZ components -> indices with negation:
    # 0    -> ( 1,  u,  v)   -> ( /,  0,  1)
    # 1    -> (-u,  1,  v)   -> (-0,  /,  1)
    # 2    -> (-u, -v,  1)   -> (-0, -1,  /)
    # 3    -> (-1, -v, -u)   -> (-/, -1, -0) <- -1 here means -1 times the value in index 1,
    # 4    -> ( v, -1, -u)   -> ( 1, -/, -0)    not index -1
    # 5    -> ( v,  u, -1)   -> ( 1,  0, -/)
    if face == 0:
        s2_point = (1, uv[0], uv[1])
    elif face == 1:
        s2_point = (-uv[0], 1, uv[1])
    elif face == 2:
        s2_point = (-uv[0], -uv[1], 1)
    elif face == 3:
        s2_point = (-1, -uv[1], -uv[0])
    elif face == 4:
        s2_point = (uv[1], -1, -uv[0])
    elif face == 5:
        s2_point = (uv[1], uv[0], -1)
    else:
        raise ValueError('Cannot convert UV to XYZ with invalid face: ' + str(face))

    return s2_point


def _s2_init_lookups() -> None:
    """
    Initialise the S2 lookups in global vars _S2_LOOKUP_POS and _S2_LOOKUP_IJ.

    This generates 4 variations of a 4 level deep Hilbert curve, one for each swap/invert bit
    combination. This allows mapping between 8 bits (+2 orientation) of Hilbert curve position and 8
    bits (+2 orientation) of I and J, and vice versa. The new orientation bits read from the mapping
    tell us the base orientation of the curve segments within the next deeper level of sub-cells.

    This implementation differs in structure from the reference implementation, since it is
    iterative rather than recursive. The end result is the same lookup table.

    See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2cell_id.cc#L75-L109

    """
    global _S2_LOOKUP_POS, _S2_LOOKUP_IJ  # pylint: disable=global-statement
    if _S2_LOOKUP_POS is None or _S2_LOOKUP_IJ is None:  # pragma: no branch
        lookup_length = 1 << (2 * _S2_LOOKUP_BITS + 2)
        _S2_LOOKUP_POS = np.zeros((lookup_length,), dtype=np.uint64)
        _S2_LOOKUP_IJ = np.zeros((lookup_length,), dtype=np.uint64)

        # Generate lookups for each of the base orientations given by the swap and invert bits
        for base_orientation in np.array([
            0, _S2_SWAP_MASK, _S2_INVERT_MASK, _S2_SWAP_MASK | _S2_INVERT_MASK  # 0-4 effectively
        ], dtype=np.uint64):
            # Walk the 256 possible positions within a level 4 curve. There is probably a smarter
            # way of doing this iteratively that reuses work at each level. e.g. 4 nested for loops?
            for pos in np.arange(4 ** 4, dtype=np.uint64):
                ij = np.uint64(0)  # Has pattern iiiijjjj, not ijijijij  # pylint: disable=invalid-name
                orientation = np.uint64(base_orientation)

                # Walk the pairs of bits of pos, from most significant, getting IJ and orientation
                # as we go
                for bit_pair_offset in range(4):
                    # Bit pair is effectively the sub-cell index
                    bit_pair = (pos >> np.uint64((3 - bit_pair_offset) * 2)) & np.uint64(0b11)

                    # Get the I and J for the sub-cell index. These need to be spread into iiiijjjj
                    # by inserting as bit positions 4 and 0
                    ij_bits = _S2_POS_TO_IJ[orientation][bit_pair]
                    ij = (  # pylint: disable=invalid-name
                        (ij << np.uint64(1))  # Free up position 4 and 0 from old IJ
                        | ((ij_bits & np.uint32(2)) << np.uint32(3))  # I bit in position 4
                        | (ij_bits & np.uint32(1))  # J bit in position 0
                    )

                    # Update the orientation with the new sub-cell orientation
                    orientation = orientation ^ _S2_POS_TO_ORIENTATION_MASK[bit_pair]

                # Shift IJ and position to allow orientation bits in LSBs of lookup
                ij <<= np.uint32(2)  # pylint: disable=invalid-name
                pos <<= np.uint32(2)

                # Write lookups
                _S2_LOOKUP_POS[ij | base_orientation] = pos | orientation
                _S2_LOOKUP_IJ[pos | base_orientation] = ij | orientation


#
# Cell ID <-> Token translation functions
#

def cell_id_to_token(cell_id: Union[int, np.uint64]) -> str:
    """
    Convert S2 cell ID to a S2 token.

    Converts the S2 cell ID to hex and strips any trailing zeros. The 0 cell ID token is represented
    as 'X' to prevent it being an empty string.

    See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2cell_id.cc#L204-L220

    Args:
        cell_id: The S2 cell ID integer.

    Returns:
        The S2 token string for the S2 cell ID.

    Raises:
        TypeError: If the cell_id is not int or np.uint64.

    """
    # Check type
    if not isinstance(cell_id, (int, np.uint64)):
        raise TypeError('Cannot convert S2 cell ID from type: ' + str(type(cell_id)))
    cell_id = np.uint64(cell_id)

    # The zero token is encoded as 'X' rather than as a zero-length string. This implementation has
    # no method of generating the 0 cell ID, so this line is mostly here for consistency with the
    # reference implementation.
    if cell_id == 0:  # pragma: no cover
        return 'X'

    # Convert cell ID to hex and strip any trailing zeros
    return '{:016x}'.format(cell_id).rstrip('0')


def token_to_cell_id(token: str) -> np.uint64:
    """
    Convert S2 token to S2 cell ID.

    Restores the stripped 0 characters from the token and converts the hex string to integer.

    See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2cell_id.cc#L222-L239

    Args:
        token: The S2 token string. Can be upper or lower case hex string.

    Returns:
       The S2 cell ID for the S2 token.

    Raises:
        TypeError: If the token is not str.
        ValueError: If the token length is over 16.

    """
    # Check input
    if not isinstance(token, str):
        raise TypeError('Cannot convert S2 token from type: ' + str(type(token)))

    if token in ('x', 'X'):
        # The zero cell ID is represented as the character 'X' rather than as an empty string
        return np.uint64(0)

    if len(token) > 16:
        raise ValueError('Cannot convert S2 token with length > 16 characters')

    # Add stripped zeros
    token = token + ('0' * (16 - len(token)))

    # Convert to cell ID by converting hex to int
    return np.uint64(int(token, 16))


#
# Encode functions
#

def lat_lon_to_cell_id(  # pylint: disable=too-many-locals
        lat: float, lon: float, level: int = 30
) -> np.uint64:
    """
    Convert lat/lon to a S2 cell ID.

    It is expected that the lat/lon provided are normalised, with latitude in the range -90 to 90.

    Args:
        lat: The latitude to convert, in degrees.
        lon: The longitude to convert, in degrees.
        level: The level of the cell ID to generate, from 0 up to 30.

    Returns:
        The S2 cell ID for the lat/lon location.

    Raises:
        ValueError: When level is not an integer, is < 0 or is > 30.

    """
    if not isinstance(level, int) or level < 0 or level > _S2_MAX_LEVEL:
        raise ValueError('S2 level must be integer >= 0 and <= 30')

    # Populate _S2_LOOKUP_POS on first run.
    # See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2cell_id.cc#L75-L109
    #
    # This table takes 10 bits of I and J and orientation and returns 10 bits of curve position and
    # new orientation
    if _S2_LOOKUP_POS is None:  # pragma: no cover
        _s2_init_lookups()

    # Reuse constant expressions
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    sin_lat_rad = math.sin(lat_rad)
    cos_lat_rad = math.cos(lat_rad)
    sin_lon_rad = math.sin(lon_rad)
    cos_lon_rad = math.cos(lon_rad)

    # Convert to S2Point
    # This is effectively the unit non-geodetic ECEF vector
    s2_point = (
        cos_lat_rad * cos_lon_rad,  # X
        cos_lat_rad * sin_lon_rad,  # Y
        sin_lat_rad                 # Z
    )

    # Get cube face
    # See s2geometry/blob/2c02e21040e0b82aa5719e96033d02b8ce7c0eff/src/s2/s2coords.h#L380-L384
    #
    # The face is determined by the largest XYZ component of the S2Point vector. When the component
    # is negative, the second set of three faces is used.
    # Largest component -> face:
    # +x -> 0
    # +y -> 1
    # +z -> 2
    # -x -> 3
    # -y -> 4
    # -z -> 5
    face = int(np.argmax(np.abs(s2_point)))  # Largest absolute component
    if s2_point[face] < 0.0:
        face += 3

    # Convert face + XYZ to cube-space face + UV
    # See s2geometry/blob/2c02e21040e0b82aa5719e96033d02b8ce7c0eff/src/s2/s2coords.h#L366-L372
    #
    # The faces are oriented to ensure continuity of curve.
    # Face -> UV components -> indices with negation (without divisor, which is always the remaining
    # component (index: face % 3)):
    # 0 -> ( y,  z) -> ( 1,  2)
    # 1 -> (-x,  z) -> (-0,  2)
    # 2 -> (-x, -y) -> (-0, -1) <- -1 here means -1 times the value in index 1, not index -1
    # 3 -> ( z,  y) -> ( 2,  1)
    # 4 -> ( z, -x) -> ( 2, -0)
    # 5 -> (-y, -x) -> (-1, -0)
    #
    # For a compiled language, a switch statement on face is preferable as it will be more easily
    # optimised as a jump table etc; but in Python the indexing method is more concise.
    #
    # The index selection can be reduced to some bit magic:
    # U: 1 - ((face + 1) >> 1)
    # V: 2 - (face >> 1)
    #
    # The negation of the the two components is then selected:
    # U: (face in [1, 2, 5]) ? -1: 1
    # V: (face in [2, 4, 5])) ? -1: 1
    uv = (  # pylint: disable=invalid-name
        s2_point[1 - ((face + 1) >> 1)] / s2_point[face % 3],  # U
        s2_point[2 - (face >> 1)] / s2_point[face % 3]         # V
    )
    if face in (1, 2, 5):
        uv = (-uv[0], uv[1])  # Negate U  # pylint: disable=invalid-name
    if face in (2, 4, 5):
        uv = (uv[0], -uv[1])  # Negate V  # pylint: disable=invalid-name

    # Project cube-space UV to cell-space ST
    # See s2geometry/blob/2c02e21040e0b82aa5719e96033d02b8ce7c0eff/src/s2/s2coords.h#L317-L320
    st = (_s2_uv_to_st(uv[0]), _s2_uv_to_st(uv[1]))  # pylint: disable=invalid-name

    # Convert ST to IJ integers
    # See s2geometry/blob/2c02e21040e0b82aa5719e96033d02b8ce7c0eff/src/s2/s2coords.h#L333-L336
    ij = (_s2_st_to_ij(st[0]), _s2_st_to_ij(st[1]))  # pylint: disable=invalid-name

    # Convert face + IJ to cell ID
    # See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2cell_id.cc#L256-L298
    #
    # This is done by looking up 8 bits of I and J (4 each) at a time in the lookup table, along
    # with two bits of orientation (swap (1) and invert (2)). This gives back 8 bits of position
    # along the curve and two new orientation bits for the curve within the sub-cells in the next
    # step.
    #
    # The swap bit swaps I and J with each other
    # The invert bit inverts the bits of I and J, which means axes are negated
    #
    # Compared to the standard versions, we check the required number of steps we need to do for the
    # requested level and don't perform steps that will be completely overwritten in the truncation
    # below, rather than always doing every step. Each step does 4 bits each of I and J, which is 4
    # levels, so the required number of steps is ceil((level + 2) / 4), when level is > 0. The
    # additional 2 levels added are required to account for the top 3 bits (4 before right shift)
    # that are occupied by the face bits.
    bits = np.uint64(face) & _S2_SWAP_MASK  # iiiijjjjoo. Initially set by by face
    cell_id = np.uint64(face << (_S2_POS_BITS - 1))  # Insert face at most signficant bits
    lookup_mask = np.uint64((1 << _S2_LOOKUP_BITS) - 1)
    required_steps = math.ceil((level + 2) / 4) if level > 0 else 0
    for k in range(7, 7 - required_steps, -1):
        # Grab 4 bits of each of I and J
        offset = np.uint32(k * _S2_LOOKUP_BITS)
        bits += ((ij[0] >> offset) & lookup_mask) << np.uint32(_S2_LOOKUP_BITS + 2)
        bits += ((ij[1] >> offset) & lookup_mask) << np.uint32(2)

        # Map bits from iiiijjjjoo to ppppppppoo
        bits = _S2_LOOKUP_POS[bits]

        # Insert position bits to cell ID
        cell_id |= (bits >> np.uint32(2)) << np.uint32(k * 2 * _S2_LOOKUP_BITS)

        # Remove position bits, leaving just new swap and invert bits for the next round
        bits &= (_S2_SWAP_MASK | _S2_INVERT_MASK)

    # Left shift and add trailing bit
    # The trailing bit addition is disabled, as we are overwriting this below in the truncation
    # anyway. This line is kept as an example of the full method for S2 cell ID creation as is done
    # in the standard library versions.
    cell_id = (cell_id << np.uint8(1))  # + np.uint64(1)

    # Truncate to desired level
    # This is done by finding the mask of the trailing 1 bit for the specified level, then zeroing
    # out all bits less significant than this, then finally setting the trailing 1 bit. This is
    # still necessary to do even after a reduced number of steps `required_steps` above, since each
    # step contains multiple levels that may need partial overwrite. Additionally, we need to add
    # the trailing 1 bit, which is not yet set above.
    least_significant_bit_mask = np.uint64(1) << np.uint32(2 * (_S2_MAX_LEVEL - level))
    cell_id = (cell_id & -least_significant_bit_mask) | least_significant_bit_mask

    return cell_id


def lat_lon_to_token(lat: float, lon: float, level: int = 30) -> str:
    """
    Convert lat/lon to a S2 token.

    Converts the S2 cell ID to hex and strips any trailing zeros. The 0 cell ID token is represented
    as 'X' to prevent it being an empty string.

    It is expected that the lat/lon provided are normalised, with latitude in the range -90 to 90.

    See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2cell_id.cc#L204-L220

    Args:
        lat: The latitude to convert, in degrees.
        lon: The longitude to convert, in degrees.
        level: The level of the cell ID to generate, from 0 up to 30.

    Returns:
        The S2 token string for the lat/lon location.

    Raises:
        ValueError: When level is not an integer, is < 0 or is > 30.

    """
    # Generate cell ID and convert to token
    return cell_id_to_token(lat_lon_to_cell_id(lat=lat, lon=lon, level=level))


#
# Decode functions
#

def cell_id_to_lat_lon(  # pylint: disable=too-many-locals
    cell_id: Union[int, np.uint64]
) -> Tuple[float, float]:
    """
    Convert S2 cell ID to lat/lon.

    Args:
        cell_id: The S2 cell ID integer.

    Returns:
        The lat/lon (in degrees) tuple generated from the S2 cell ID.

    Raises:
        TypeError: If the cell_id is not int or np.uint64.
        ValueError: If the cell_id has invalid face bits.

    """
    # Check type
    if not isinstance(cell_id, (int, np.uint64)):
        raise TypeError('Cannot decode S2 cell ID from type: ' + str(type(cell_id)))
    cell_id = np.uint64(cell_id)

    # Populate _S2_LOOKUP_IJ on first run.
    # See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2cell_id.cc#L75-L109
    # This table takes 10 bits of curve position and orientation and returns 10 bits of I and J and
    # new orientation
    if _S2_LOOKUP_IJ is None:  # pragma: no cover
        _s2_init_lookups()

    # Extract face + IJ from cell ID
    # See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2cell_id.cc#L312-L367
    #
    # This is done by looking up 8 bits of curve position at a time in the lookup table, along with
    # two bits of orientation (swap (1) and invert (2)). This gives back 8 bits of I and J (4 each)
    # and two new orientation bits for the curve within the sub-cells in the next step.
    #
    # The swap bit swaps I and J with each other
    # The invert bit inverts the bits of I and J, which means axes are negated
    #
    # In the first loop (most significant bits), the 3 bits occupied by the face need to be masked
    # out, since these are not set in the IJ to cell ID during encoding.
    #
    # The I and J returned here are of one of the two leaf (level 30) cells that are located
    # diagonally closest to the cell centre. This happens because repeated ..00.. will select the
    # 'lower left' (for nominally oriented Hilbert curve segments) of the sub-cells. The ..10..
    # arising from the trailing bit, prior to the repeated ..00.. bits, ensures we first pick the
    # 'upper right' of the cell, then iterate in to lower left until we hit the leaf cell. However,
    # in the case of the swapped and inverted curve segment (4th sub-curve segment), the ..10.. will
    # select the 'lower left' and then iterate to the 'upper right' with each ..00.. following. In
    # that case, we will be offset left and down by one leaf cell in each of I and J, which needs to
    # be added to have a consistent mapping. This is detectable by seeing that the final bit of I or
    # J is 1 (i.e we have picked an odd row/column, which will happen concurrently in both I and J,
    # so we only need to check one), except in case of level 29 where the logic is inverted and the
    # correction needs to be applied when we pick an even row/column (i.e I/J ends in 0), since
    # there are no trailing ..00..
    #
    # This behaviour can be captured in the expression:
    # apply_correction = not leaf and (i ^ (is level 29)) & 1
    # apply_corerction = not leaf and (i ^ (cell_id >> 2)) & 1
    #
    # We check for level 29 by looking for the trailing 1 in third LSB, when we already know that we
    # are not a leaf cell (which could give false positive) by the initial check in the expression.
    # See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2cell_id.h#L503-L529
    #
    face = cell_id >> _S2_POS_BITS
    bits = face & _S2_SWAP_MASK  # ppppppppoo. Initially set by by face
    lookup_mask = np.uint64((1 << _S2_LOOKUP_BITS) - 1)
    i = np.uint64(0)
    j = np.uint64(0)
    for k in range(7, -1, -1):
        # Pull out 8 bits of cell ID, except in first loop where we pull out only 4
        n_bits = (_S2_MAX_LEVEL - 7 * _S2_LOOKUP_BITS) if k == 7 else _S2_LOOKUP_BITS
        extract_mask = np.uint64((1 << (2 * n_bits)) - 1)  # 8 (or 4) one bits
        bits += (
            (cell_id >> np.uint32(k * 2 * _S2_LOOKUP_BITS + 1)) & extract_mask
        ) << np.uint32(2)

        # Map bits from ppppppppoo to iiiijjjjoo
        bits = _S2_LOOKUP_IJ[bits]

        # Extract I and J bits
        offset = np.uint32(k * _S2_LOOKUP_BITS)
        i += (bits >> np.uint32(_S2_LOOKUP_BITS + 2)) << offset  # Don't need lookup mask here
        j += ((bits >> np.uint32(2)) & lookup_mask) << offset

        # Remove I and J bits, leaving just new swap and invert bits for the next round
        bits &= (_S2_SWAP_MASK | _S2_INVERT_MASK)

    # Resolve the centre of the cell. For leaf cells, we add half the leaf cell size. For non-leaf
    # cells, we currently have one of either two cells diagonally around the cell centre, as
    # described above. The centre_correction_delta is 2x the offset, as we left shift I and J first.
    # This gives us the values Si and Ti, which are discrete representation of S and T in range 0 to
    # _S2_MAX_SI_TI. The extra power of 2 over IJ allows for identifying both the centre and edge of
    # cells, whilst IJ is just the leaf cells.
    # See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2coords.h#L57-L65
    is_leaf = bool(cell_id & np.uint64(1))  # Cell is leaf cell when trailing one bit is in LSB
    apply_correction = not is_leaf and ((i ^ (cell_id >> np.uint32(2))) & np.uint64(1))
    centre_correction_delta = np.uint64(1 if is_leaf else (2 if apply_correction else 0))
    si = (i << np.uint32(1)) + centre_correction_delta  # pylint: disable=invalid-name
    ti = (j << np.uint32(1)) + centre_correction_delta  # pylint: disable=invalid-name

    # Convert integer si/ti to double ST
    # See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2coords.h#L338-L341
    st = (_s2_si_ti_to_st(si), _s2_si_ti_to_st(ti))  # pylint: disable=invalid-name

    # Project cell-space ST to cube-space UV
    # See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2coords.h#L312-L315
    uv = (_s2_st_to_uv(st[0]), _s2_st_to_uv(st[1]))  # pylint: disable=invalid-name

    # Convert face + UV to S2Point XYZ
    # See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2coords.h#L348-L357
    s2_point = _s2_face_uv_to_xyz(face, uv)

    # Normalise XYZ S2Point vector
    # This section is part of the reference implementation but is not necessary when mapping
    # straight into lat/lon, since the normalised and unnormalised triangles used to calculate the
    # angles are geometrically similar. If anything, the normalisation process loses precision when
    # tested against the reference implementation, albeit not at a level that is important either
    # way. The code below is left for demonstration of the normalisation process.
    # norm = math.sqrt(s2_point[0] ** 2 + s2_point[1] ** 2 + s2_point[2] ** 2)
    # s2_point = (s2_point[0] / norm, s2_point[1] / norm, s2_point[2] / norm)

    # Map into lat/lon
    # See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2latlng.h#L196-L205
    lat_rad = math.atan2(s2_point[2], math.sqrt(s2_point[0] ** 2 + s2_point[1] ** 2))
    lon_rad = math.atan2(s2_point[1], s2_point[0])

    return (math.degrees(lat_rad), math.degrees(lon_rad))


def token_to_lat_lon(token: str) -> Tuple[float, float]:
    """
    Convert S2 token to lat/lon.

    See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2cell_id.cc#L222-L239

    Args:
        token: The S2 token string. Can be upper or lower case hex string.

    Returns:
        The lat/lon (in degrees) tuple generated from the S2 token.

    Raises:
        TypeError: If the token is not str.
        ValueError: If the token length is over 16.
        ValueError: If the token has invalid face bits.

    """
    # Convert to cell ID and decode to lat/lon
    return cell_id_to_lat_lon(token_to_cell_id(token))


#
# Level extraction
#

def cell_id_to_level(cell_id: Union[int, np.uint64]) -> int:
    """
    Get the level for a S2 cell ID.

    See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2cell_id.h#L543-L551

    Args:
        cell_id: The S2 cell ID integer.

    Returns:
        The level of the S2 cell ID.

    Raises:
        TypeError: If the cell_id is not int or np.uint64.
        ValueError: If the cell_id is 0.

    """
    # Check input
    if not isinstance(cell_id, (int, np.uint64)):
        raise TypeError('Cannot decode S2 cell ID from type: ' + str(type(cell_id)))
    cell_id = np.uint64(cell_id)

    if cell_id == 0:
        # The cell ID 0 has no level
        raise ValueError('Cannot decode invalid S2 cell ID: 0')

    # Find the position of the lowest set one bit, which will be the trailing one bit. The level is
    # given by the max level (30) minus the floored division by two of the position of the lowest
    # set bit.
    #
    # The position of the lowest set bit is found using 'count trailing zeros', which would be
    # equivalent to the C++20 function std::countr_zero() or the ctz instruction.
    lsb_pos = 0
    while cell_id != 0:  # pragma: no branch
        if cell_id & np.uint64(1):
            break
        lsb_pos += 1
        cell_id >>= np.uint64(1)

    return int(_S2_MAX_LEVEL - (lsb_pos >> 1))


def token_to_level(token: str) -> int:
    """
    Get the level for a S2 token.

    See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2cell_id.h#L543-L551

    Args:
        token: The S2 token string. Can be upper or lower case hex string.

    Returns:
        The level of the S2 token.

    Raises:
        TypeError: If the token is not str.
        ValueError: If the token length is over 16.
        ValueError: If the token as cell ID is 0.

    """
    # Convert to cell ID and get the level for that
    return cell_id_to_level(token_to_cell_id(token))

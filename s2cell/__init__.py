"""Minimal Python S2 cell ID, S2Point and lat/lon conversion library."""

import math

import numpy as np

__version__ = '0.0.0'


#
# S2 base constants needed for S2 cell mapping
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

# Lookup for the orientation update mask of one of the four sub-cells within a higher level cell
_S2_POS_TO_ORIENTATION_MASK = np.array([
    _S2_SWAP_MASK, 0, 0, _S2_SWAP_MASK | _S2_INVERT_MASK
], dtype=np.uint64)



#
# S2 helper functions
#

def _s2_uv_to_st(component: float) -> float:
    """
    Convert S2 UV to ST.

    This is done using the quadratic projection that is used by default for S2. The C++ and
    Java S2 libraries use a different definition of the ST cell-space, but the end result in
    IJ is the same. The below uses the C++ ST definition.

    See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2coords.h#L317-L320

    """
    if component >= 0.0:
        return 0.5 * math.sqrt(1.0 + 3.0 * component)
    return 1.0 - 0.5 * math.sqrt(1.0 - 3.0 * component)


def _s2_st_to_uv(component: float) -> float:
    """
    Convert S2 ST to UV.

    This is done using the quadratic projection that is used by default for S2. The C++ and
    Java S2 libraries use a different definition of the ST cell-space, but the end result in
    IJ is the same. The below uses the C++ ST definition.

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

    See s2geometry/blob/c59d0ca01ae3976db7f8abdc83fcc871a3a95186/src/s2/s2coords.h#L338-L341

    """
    return (1.0 / _S2_MAX_SI_TI) * component


def _s2_init_lookups() -> None:
    """
    Initialise the S2 lookups in global vars _S2_LOOKUP_POS and _S2_LOOKUP_IJ.

    This generates 4 variations of a 4 level deep Hilbert curve, one for each swap/invert bit
    combination. This allows mapping between 8 bits (+2 orientation) of Hilbert curve position
    and 8 bits (+2 orientation) of I and J, and vice versa. The new orientation bits read from the
    mapping tell us the base orientation of the curve segments within the next deeper level of
    sub-cells.

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
                ij = np.uint64(0)  # Has pattern iiiijjjj, not ijijijij
                orientation = np.uint64(base_orientation)

                # Walk the pairs of bits of pos, from most significant, getting IJ and orientation
                # as we go
                for bit_pair_offset in range(4):
                    # Bit pair is effectively the sub-cell index
                    bit_pair = (pos >> np.uint64((3 - bit_pair_offset) * 2)) & np.uint64(0b11)

                    # Get the I and J for the sub-cell index. These need to be spread into iiiijjjj
                    # by inserting as bit positions 4 and 0
                    ij_bits = _S2_POS_TO_IJ[orientation][bit_pair]
                    ij = (
                        (ij << np.uint64(1))  # Free up position 4 and 0 from old IJ
                        | ((ij_bits & np.uint32(2)) << np.uint32(3))  # I bit in position 4
                        | (ij_bits & np.uint32(1))  # J bit in position 0
                    )

                    # Update the orientation with the new sub-cell orientation
                    orientation = orientation ^ _S2_POS_TO_ORIENTATION_MASK[bit_pair]

                # Shift IJ and position to allow orientation bits in LSBs of lookup
                ij <<= np.uint32(2)
                pos <<= np.uint32(2)

                # Write lookups
                _S2_LOOKUP_POS[ij | base_orientation] = pos | orientation
                _S2_LOOKUP_IJ[pos | base_orientation] = ij | orientation


#
# Public functions
#

def lat_lon_to_cell_id(
        lat: float, lon: float, level: int = 30
) -> np.uint64:  # pylint: disable=too-many-locals
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
    # This table takes 10 bits of I and J and orientation and returns 10 bits of curve position
    # and new orientation
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
    # The face is determined by the largest XYZ component of the S2Point vector. When the
    # component is negative, the second set of three faces is used.
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
    # Face -> UV components -> indices with negation (without divisor, which is always the
    # remaining component (index: face % 3)):
    # 0 -> ( y,  z) -> ( 1,  2)
    # 1 -> (-x,  z) -> (-0,  2)
    # 2 -> (-x, -y) -> (-0, -1) <- -1 here means -1 times the value in index 1, not index -1
    # 3 -> ( z,  y) -> ( 2,  1)
    # 4 -> ( z, -x) -> ( 2, -0)
    # 5 -> (-y, -x) -> (-1, -0)
    #
    # For a compiled language, a switch statement on face is preferable as it will be more
    # easily optimised as a jump table etc; but in Python the indexing method is more concise.
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
    # along the curve and two new orientation bits for the curve within the sub-cells in the
    # next step.
    #
    # The swap bit swaps I and J with each other
    # The invert bit inverts the bits of I and J, which means axes are negated
    #
    # Compared to the standard versions, we check the required number of steps we need to do for
    # the requested level and don't perform steps that will be completely overwritten in the
    # truncation below, rather than always doing every step. Each step does 4 bits each of I and
    # J, which is 4 levels, so the required number of steps is ceil((level + 2) / 4), when level
    # is > 0. The additional 2 levels added are required to account for the top 3 bits (4 before
    # right shift) that are occupied by the face bits.
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
    # anyway. This line is kept as an example of the full method for S2 cell ID creation as is
    # done in the standard library versions.
    cell_id = (cell_id << np.uint8(1))  # + np.uint64(1)

    # Truncate to desired level
    # This is done by finding the mask of the trailing 1 bit for the specified level, then
    # zeroing out all bits less significant than this, then finally setting the trailing 1 bit.
    # This is still necessary to do even after a reduced number of steps `required_steps` above,
    # since each step contains multiple levels that may need partial overwrite. Additionally, we
    # need to add the trailing 1 bit, which is not yet set.
    least_significant_bit_mask = np.uint64(1) << np.uint32(2 * (_S2_MAX_LEVEL - level))
    cell_id = (cell_id & -least_significant_bit_mask) | least_significant_bit_mask

    return cell_id

def lat_lon_to_token(lat: float, lon: float, level: int = 30) -> str:
    """
    Convert lat/lon to a S2 token.

    Converts the S2 cell ID to hex and strips any trailing zeros. The 0 cell ID token is
    represented as 'X' to prevent it being an empty string.

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
    # Get the cell ID for the lat/lon
    cell_id = lat_lon_to_cell_id(lat=lat, lon=lon, level=level)

    # The zero token is encoded as 'X' rather than as a zero-length string. This implementation
    # has no method of generating the 0 cell ID, so this line is mostly here for consistency
    # with the reference implementation.
    if cell_id == 0:  # pragma: no cover
        return 'X'

    # Convert cell ID to hex and strip any trailing zeros
    return '{:016x}'.format(cell_id).rstrip('0')

"""Minimal Python S2 cell ID, S2Point and lat/lon conversion library."""

import math

import numpy as np

__all__ = []  # TODO


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
    Convert S2 si/ti to ST.

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

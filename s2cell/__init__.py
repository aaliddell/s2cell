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

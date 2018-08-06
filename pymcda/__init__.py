from . import support
from . import normalize
from . import weightedsum
from . import topsis
from . import concordance
from . import fuzzy
from . import promethee

try:
	import numpy as np
except ImportError:
    print("numpy missing!")

__version__ = '0.4'


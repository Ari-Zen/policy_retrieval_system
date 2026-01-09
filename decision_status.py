# Module
from enum import Enum

# Decision status
class DecisionStatus(str, Enum):
    SAFE = 'safe'
    CONFLICT = 'conflict'
    INSUFFICIENT_COVERAGE = 'insufficient_coverage'
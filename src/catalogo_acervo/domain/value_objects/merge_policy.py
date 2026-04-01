from enum import Enum


class MergePolicy(str, Enum):
    REPLACE = "replace"
    MERGE = "merge"
    KEEP_EXISTING = "keep"

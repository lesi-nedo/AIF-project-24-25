
from functools import lru_cache
from typing import Any, Dict, Tuple
import hashlib

class ProblogCache:
    def __init__(self, maxsize=128):
        self.maxsize = maxsize
        self._cache = {}

    @lru_cache(maxsize=128)
    def _compute_hash(self, query: str, evidence: Dict[str, bool]) -> str:
        """Create a unique hash for the query and evidence"""
        evidence_str = str(sorted(evidence.items()))
        return hashlib.md5(f"{query}:{evidence_str}".encode()).hexdigest()

    def get(self, query: str, evidence: Dict[str, bool]) -> Any:
        """Get cached result for a query"""
        key = self._compute_hash(query, evidence)
        return self._cache.get(key)

    def set(self, query: str, evidence: Dict[str, bool], result: Any) -> None:
        """Cache the result of a query"""
        key = self._compute_hash(query, evidence)
        self._cache[key] = result
        
        # Basic cache size management
        if len(self._cache) > self.maxsize:
            # Remove oldest entries
            oldest = list(self._cache.keys())[:-self.maxsize]
            for key in oldest:
                del self._cache[key]

    def clear(self):
        """Clear the cache"""
        self._cache.clear()
        self._compute_hash.cache_clear()
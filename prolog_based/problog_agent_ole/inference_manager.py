
from problog.logic import Term, Constant
from problog.program import PrologString
from problog.tasks import sample
from problog.engine import DefaultEngine
from typing import List, Dict, Any
import random

class ApproximateInference:
    def __init__(self, max_samples: int = 1000):
        self.engine = DefaultEngine()
        self.max_samples = max_samples

    def monte_carlo_sample(self, program: str, query: str, n_samples: int = None) -> float:
        """Monte Carlo sampling for approximate inference"""
        if n_samples is None:
            n_samples = self.max_samples

        # Convert program to ProbLog format
        prob_program = PrologString(program)
        
        # Perform sampling
        results = sample.sample(prob_program, n_samples=n_samples)
        
        # Count successful samples
        success_count = sum(1 for r in results if query in r)
        return success_count / n_samples

    def k_best(self, program: str, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """K-best approximation - returns k most probable explanations"""
        prob_program = PrologString(program)
        engine = DefaultEngine()
        db = engine.prepare(prob_program)
        
        # Get k-best proofs
        results = []
        for proof in engine.enumerate_proofs(db, Term(query), k=k):
            probability = self._compute_proof_probability(proof)
            results.append({
                'proof': proof,
                'probability': probability
            })
            
        return sorted(results, key=lambda x: x['probability'], reverse=True)

    def bounded_approximation(self, program: str, query: str, threshold: float = 0.1) -> float:
        """Bounded approximation with error threshold"""
        prob_program = PrologString(program)
        
        # Initial sample size
        n_samples = 100
        prev_prob = 0
        current_prob = self.monte_carlo_sample(program, query, n_samples)
        
        # Keep sampling until convergence
        while abs(current_prob - prev_prob) > threshold and n_samples < self.max_samples:
            prev_prob = current_prob
            n_samples *= 2
            current_prob = self.monte_carlo_sample(program, query, n_samples)
            
        return current_prob

    def _compute_proof_probability(self, proof) -> float:
        """Helper method to compute probability of a proof"""
        # Simple multiplication of fact probabilities in the proof
        probability = 1.0
        for fact in proof:
            if hasattr(fact, 'probability'):
                probability *= fact.probability
        return probability
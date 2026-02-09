"""Gene and Individual entity classes."""

from typing import List


class Gene:
    """Represents a single gene with expression level.

    Parameters
    ----------
    name : str
        Name/identifier for the gene.
    expression_level : float
        Current expression level. Negative values are clamped to 0.
    """

    __slots__ = ('name', '_expression_level')

    def __init__(self, name: str, expression_level: float):
        self.name: str = name
        # Clamp expression level to [0, inf)
        self._expression_level: float = max(0.0, expression_level)

    @property
    def expression_level(self) -> float:
        """Current expression level (always >= 0)."""
        return self._expression_level


class Individual:
    """Represents an individual in the population with genes and fitness.

    Parameters
    ----------
    genes : List[Gene]
        List of Gene objects in this individual.
    """

    __slots__ = ('genes', 'fitness')

    def __init__(self, genes: List[Gene]):
        self.genes: List[Gene] = genes
        self.fitness: float = 1.0

    def mean_expression(self) -> float:
        """Compute mean expression level across all genes.

        Returns
        -------
        float
            Mean of all gene expression levels. Returns 0.0 if no genes.
        """
        if not self.genes:
            return 0.0
        return sum(gene.expression_level for gene in self.genes) / len(self.genes)

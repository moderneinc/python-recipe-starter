"""Example OpenRewrite Python recipes.

``activate()`` is the entry point the Moderne CLI calls to discover the recipes
in this package. It is wired up through the ``openrewrite.recipes`` entry point
declared in ``pyproject.toml``.
"""

from rewrite import CategoryDescriptor
from rewrite.marketplace import RecipeMarketplace, Python

from .remove_redundant_pass import RemoveRedundantPass
from .rename_function_call import RenameFunctionCall

__all__ = ["RenameFunctionCall", "RemoveRedundantPass", "activate"]

# Category paths run from shallowest to deepest; this one files recipes under
# Python > Cleanup in the marketplace.
Cleanup = [*Python, CategoryDescriptor(display_name="Cleanup")]


def activate(marketplace: RecipeMarketplace) -> None:
    """Install this package's recipes into the recipe marketplace."""
    marketplace.install(RenameFunctionCall, Python)
    marketplace.install(RemoveRedundantPass, Cleanup)

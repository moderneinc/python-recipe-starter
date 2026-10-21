"""Example OpenRewrite Python recipes.

``activate()`` is the entry point the Moderne CLI calls to discover the recipes
in this package. It is wired up through the ``openrewrite.recipes`` entry point
declared in ``pyproject.toml``.
"""

from rewrite.decorators import get_recipe_category
from rewrite.marketplace import RecipeMarketplace

from .find_shell_subprocess_calls import FindShellSubprocessCalls
from .remove_zero_from_range import RemoveZeroFromRange
from .replace_locale_resetlocale import ReplaceLocaleResetlocale

__all__ = ["FindShellSubprocessCalls", "RemoveZeroFromRange", "ReplaceLocaleResetlocale", "activate"]


def activate(marketplace: RecipeMarketplace) -> None:
    """Install this package's recipes under the category each declares with ``@categorize``."""
    for recipe in (FindShellSubprocessCalls, RemoveZeroFromRange, ReplaceLocaleResetlocale):
        category = get_recipe_category(recipe)
        if category is not None:
            marketplace.install(recipe, category)

"""A recipe that replaces a removed standard-library call using templates.

This example shows how a recipe handles imports:

* a ``template`` whose ``context`` names the imports its code needs, and
* ``maybe_remove_import`` for an import the rewrite leaves unused.

A template binds the names its context imports the way ``rewrite.python.binding.maybe_bind``
does. Where the file already imports the module, the template spells the file's name for it.
Otherwise the import is added.
"""

from typing import Any

from rewrite import ExecutionContext, Preconditions, Recipe, TreeVisitor
from rewrite.category import CategoryDescriptor
from rewrite.decorators import categorize
from rewrite.java import J
from rewrite.java.tree import MethodInvocation
from rewrite.marketplace import Python
from rewrite.python.method_matcher import MethodMatcher
from rewrite.python.preconditions import uses_method
from rewrite.python.remove_import import RemoveImportOptions, maybe_remove_import
from rewrite.python.template import template
from rewrite.python.visitor import PythonVisitor

Migrate = [*Python, CategoryDescriptor(display_name="Migrate")]

_RESETLOCALE = "locale resetlocale(..)"
_RESETLOCALE_CALL = MethodMatcher.create(_RESETLOCALE)

_SETLOCALE = template('locale.setlocale(locale.LC_ALL, "")', context=["import locale"])


@categorize(Migrate)
class ReplaceLocaleResetlocale(Recipe):
    """
    Replace ``locale.resetlocale()`` with ``locale.setlocale(locale.LC_ALL, "")``.

    Example:
        Before:
            import locale
            locale.resetlocale()

        After:
            import locale
            locale.setlocale(locale.LC_ALL, "")
    """

    @property
    def name(self) -> str:
        return "com.yourorg.ReplaceLocaleResetlocale"

    @property
    def display_name(self) -> str:
        return 'Replace `locale.resetlocale()` with `locale.setlocale(locale.LC_ALL, "")`'

    @property
    def description(self) -> str:
        return (
            "`locale.resetlocale()` was deprecated in Python 3.11 and removed in Python 3.13. "
            'Replace it with `locale.setlocale(locale.LC_ALL, "")`. '
            "A call is left alone where `locale` names something other than the module in the file."
        )

    @property
    def tags(self) -> list[str]:
        return ["python", "migration"]

    def editor(self) -> TreeVisitor[Any, ExecutionContext]:
        class Visitor(PythonVisitor[ExecutionContext]):
            def visit_method_invocation(self, method: MethodInvocation, p: ExecutionContext) -> J:
                m = super().visit_method_invocation(method, p)
                if not isinstance(m, MethodInvocation) or not _RESETLOCALE_CALL.matches(m, cursor=self.cursor):
                    return m
                try:
                    replaced = _SETLOCALE.apply(self.cursor, visitor=self)
                except ValueError:
                    # A template refuses a file where a name its context binds means something else.
                    return m
                maybe_remove_import(self, RemoveImportOptions(module="locale", name="resetlocale"))
                return replaced or m

        return Preconditions.check(uses_method(_RESETLOCALE), Visitor())

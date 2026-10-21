"""A recipe that simplifies ``range(0, n)`` to ``range(n)`` using a pattern and a template.

This example shows how a recipe matches and rewrites code by its shape:

* a ``pattern`` that matches code by its structure and types, with a ``capture`` for the part that
  varies and a ``constraint`` on what the capture accepts,
* a ``template`` that builds the replacement from what the pattern captured,
* a precondition, so files that never call ``range`` are skipped.
"""

from typing import Any

from rewrite import ExecutionContext, Preconditions, Recipe, TreeVisitor
from rewrite.category import CategoryDescriptor
from rewrite.decorators import categorize
from rewrite.java import J
from rewrite.java.tree import MethodInvocation
from rewrite.marketplace import Python
from rewrite.python.preconditions import uses_method
from rewrite.python.template import capture, pattern, template
from rewrite.python.tree import Star
from rewrite.python.visitor import PythonVisitor

# A category path runs from the shallowest category to the deepest. This one files the recipe
# under Python > Cleanup in the marketplace.
Cleanup = [*Python, CategoryDescriptor(display_name="Cleanup")]

# An unpacked ``*args`` may hold the step as well as the stop, so dropping the ``0`` before it
# would change which argument is which.
_stop = capture("stop", constraint=lambda arg: not isinstance(arg, Star))
_RANGE_FROM_ZERO = pattern(f"range(0, {_stop})")
_RANGE = template(f"range({_stop})")


@categorize(Cleanup)
class RemoveZeroFromRange(Recipe):
    """
    Drop the ``0`` start argument from ``range(0, n)``.

    Example:
        Before:
            indices = range(0, n)

        After:
            indices = range(n)
    """

    @property
    def name(self) -> str:
        return "com.yourorg.RemoveZeroFromRange"

    @property
    def display_name(self) -> str:
        return "Drop the `0` start argument from `range()`"

    @property
    def description(self) -> str:
        return (
            "Shorten `range(0, n)` to `range(n)`, since `range` starts at zero by default. "
            "A call with an unpacked `*` argument is left alone."
        )

    @property
    def tags(self) -> list[str]:
        return ["python", "cleanup", "ruff", "PIE808"]

    def editor(self) -> TreeVisitor[Any, ExecutionContext]:
        class Visitor(PythonVisitor[ExecutionContext]):
            def visit_method_invocation(self, method: MethodInvocation, p: ExecutionContext) -> J:
                m = super().visit_method_invocation(method, p)
                if not isinstance(m, MethodInvocation):
                    return m
                match = _RANGE_FROM_ZERO.match(m, self.cursor)
                if not match:
                    return m
                return _RANGE.apply(self.cursor, values=match) or m

        return Preconditions.check(uses_method("range <constructor>(..)"), Visitor())

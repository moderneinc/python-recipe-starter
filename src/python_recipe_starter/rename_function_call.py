"""A configurable recipe that renames calls to a function.

This example shows the most common shape of a recipe:

* a ``@dataclass`` recipe with configurable ``option()`` fields,
* an ``editor()`` that returns a ``PythonVisitor``,
* a visitor that inspects a node and returns a modified copy.
"""

from dataclasses import dataclass, field

from rewrite import ExecutionContext, Recipe, TreeVisitor, option
from rewrite.java import J
from rewrite.java.tree import MethodInvocation
from rewrite.python.visitor import PythonVisitor


@dataclass
class RenameFunctionCall(Recipe):
    """Rename calls to a function from one name to another."""

    old_name: str = field(default="", metadata=option(
        display_name="Old function name",
        description="The name of the function whose calls should be renamed.",
        example="assertEquals",
    ))

    new_name: str = field(default="", metadata=option(
        display_name="New function name",
        description="The name to rename matching calls to.",
        example="assertEqual",
    ))

    @property
    def name(self) -> str:
        return "com.yourorg.RenameFunctionCall"

    @property
    def display_name(self) -> str:
        return "Rename a function call"

    @property
    def description(self) -> str:
        return "Rename calls to a function from one name to another."

    def editor(self) -> TreeVisitor[J, ExecutionContext]:
        # Copy the options into locals so the nested visitor can read them.
        # Inside the visitor, ``self`` is the visitor, not the recipe.
        old_name = self.old_name
        new_name = self.new_name

        class Visitor(PythonVisitor[ExecutionContext]):
            def visit_method_invocation(self, method: MethodInvocation, p: ExecutionContext) -> J:
                method = super().visit_method_invocation(method, p)
                if method.name.simple_name == old_name:
                    # LST nodes are immutable, so build updated copies with replace().
                    renamed = method.name.replace(_simple_name=new_name)
                    return method.replace(_name=renamed)
                return method

        return Visitor()

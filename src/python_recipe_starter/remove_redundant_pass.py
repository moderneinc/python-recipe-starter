"""A recipe that deletes redundant ``pass`` statements.

This example shows two more techniques:

* deleting a node by returning ``None`` from a visit method, and
* using the visitor's ``cursor`` to inspect a node's surroundings.
"""

from typing import Optional

from rewrite import ExecutionContext, Recipe, TreeVisitor
from rewrite.java import J
from rewrite.java.tree import Block
from rewrite.python.tree import Pass
from rewrite.python.visitor import PythonVisitor


class RemoveRedundantPass(Recipe):
    """Remove ``pass`` statements that share a block with other statements."""

    @property
    def name(self) -> str:
        return "com.yourorg.RemoveRedundantPass"

    @property
    def display_name(self) -> str:
        return "Remove redundant `pass` statements"

    @property
    def description(self) -> str:
        return "Removes a `pass` statement when its block already contains other statements."

    def editor(self) -> TreeVisitor[J, ExecutionContext]:
        class Visitor(PythonVisitor[ExecutionContext]):
            def visit_pass(self, pass_: Pass, p: ExecutionContext) -> Optional[J]:
                # Look up the block this `pass` lives in. If it has statements
                # other than `pass`, the `pass` is redundant and can be removed.
                # Every `pass` sees the same unmodified block, so counting other
                # `pass` statements would delete them all and leave it empty.
                # Returning None deletes the node.
                block = self.cursor.first_enclosing(Block)
                if block is not None and any(not isinstance(s, Pass) for s in block.statements):
                    return None
                return pass_

        return Visitor()

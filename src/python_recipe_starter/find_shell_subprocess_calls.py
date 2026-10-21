"""A search recipe that reports what it finds in a data table.

This example shows how a recipe produces rows for a data table:

* a ``@dataclass`` row whose fields carry ``column(...)`` metadata, naming each column,
* a ``DataTable`` the recipe declares through its ``data_tables`` property,
* ``insert_row`` from the visitor, one row per finding, and
* ``SearchResult.found`` to mark each finding in the code as well.

A search recipe changes nothing but the markers, so the run's diff shows where each finding is and the
data table gathers them all, across every file and repository the recipe runs on.
"""

from dataclasses import dataclass, field
from typing import Any

from rewrite import Cursor, ExecutionContext, Preconditions, Recipe, TreeVisitor
from rewrite.category import CategoryDescriptor
from rewrite.data_table import DataTable, column
from rewrite.decorators import categorize
from rewrite.java import J, JavaType
from rewrite.java.tree import Literal, MethodInvocation
from rewrite.markers import SearchResult
from rewrite.marketplace import Python
from rewrite.python.method_matcher import MethodMatcher
from rewrite.python.preconditions import uses_import
from rewrite.python.printer import PythonPrinter
from rewrite.python.tree import CompilationUnit, NamedArgument
from rewrite.python.visitor import PythonVisitor

Search = [*Python, CategoryDescriptor(display_name="Search")]

_SUBPROCESS_CALLS = (
    MethodMatcher.create("subprocess *(..)"),
    MethodMatcher.create("subprocess.Popen <constructor>(..)"),
)


@dataclass
class ShellSubprocessCall:
    source_path: str = field(metadata=column("Source path", "The file that makes the call."))
    function: str = field(metadata=column("Function", "The `subprocess` function or class called."))
    command: str = field(metadata=column("Command", "The command passed to the shell, as written."))


@categorize(Search)
class FindShellSubprocessCalls(Recipe):
    """
    Find ``subprocess`` calls that run their command through the shell.

    Example:
        Before:
            subprocess.run(f"ls {path}", shell=True)

        After:
            /*~~>*/subprocess.run(f"ls {path}", shell=True)
    """

    calls = DataTable[ShellSubprocessCall](
        "com.yourorg.table.ShellSubprocessCalls",
        "Shell subprocess calls",
        "Calls into `subprocess` that pass `shell=True`, with the command each one runs.",
        ShellSubprocessCall,
    )

    @property
    def name(self) -> str:
        return "com.yourorg.FindShellSubprocessCalls"

    @property
    def display_name(self) -> str:
        return "Find `subprocess` calls with `shell=True`"

    @property
    def description(self) -> str:
        return (
            "Find calls into `subprocess` that pass `shell=True`, which run their command through the shell. "
            "A command built from untrusted input can then inject shell syntax. "
            "Each call is listed in a data table along with the command it runs."
        )

    @property
    def tags(self) -> list[str]:
        return ["python", "security", "bandit", "B602", "CWE-78"]

    @property
    def data_tables(self) -> list[DataTable]:
        return [self.calls]

    def editor(self) -> TreeVisitor[Any, ExecutionContext]:
        calls = self.calls

        class Visitor(PythonVisitor[ExecutionContext]):
            def visit_method_invocation(self, method: MethodInvocation, p: ExecutionContext) -> J:
                m = super().visit_method_invocation(method, p)
                if not isinstance(m, MethodInvocation) or not _runs_through_the_shell(m):
                    return m
                if not any(matcher.matches(m, cursor=self.cursor) for matcher in _SUBPROCESS_CALLS):
                    return m
                source_file = self.cursor.first_enclosing_or_throw(CompilationUnit)
                calls.insert_row(
                    p,
                    ShellSubprocessCall(
                        source_path=str(source_file.source_path),
                        function=_function_name(m),
                        command=_command(m, self.cursor),
                    ),
                )
                return SearchResult.found(m)

        return Preconditions.check(uses_import("subprocess"), Visitor())


def _runs_through_the_shell(method: MethodInvocation) -> bool:
    return any(
        isinstance(arg, NamedArgument)
        and arg.name.simple_name == "shell"
        and isinstance(arg.value, Literal)
        and arg.value.value is True
        for arg in method.arguments
    )


def _command(method: MethodInvocation, cursor: Cursor) -> str:
    """The command as written, whether passed first or as the ``args`` keyword."""
    for arg in method.arguments:
        if isinstance(arg, NamedArgument) and arg.name.simple_name == "args":
            return PythonPrinter().print(arg.value, cursor=cursor).strip()
        if not isinstance(arg, NamedArgument):
            return PythonPrinter().print(arg, cursor=cursor).strip()
    return ""


def _function_name(method: MethodInvocation) -> str:
    """The call's name as the module spells it, whatever name the file imports it under."""
    method_type = method.method_type
    if method_type is None or not isinstance(method_type.declaring_type, JavaType.Class):
        return method.name.simple_name
    declaring_type = method_type.declaring_type.fully_qualified_name
    if method_type.name == "<constructor>":
        return declaring_type
    return f"{declaring_type}.{method_type.name}"

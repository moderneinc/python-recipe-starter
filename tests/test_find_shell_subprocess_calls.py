from pathlib import Path

from rewrite.data_table import DATA_TABLE_STORE
from rewrite.execution import InMemoryExecutionContext
from rewrite.test import RecipeSpec, python

from python_recipe_starter.find_shell_subprocess_calls import FindShellSubprocessCalls, ShellSubprocessCall


def rows(ctx: InMemoryExecutionContext) -> list[ShellSubprocessCall]:
    store = ctx.get_message(DATA_TABLE_STORE)
    return list(store.get_rows(FindShellSubprocessCalls.calls.name)) if store else []


class TestFindShellSubprocessCalls:
    def test_marks_each_call_and_adds_a_row_for_it(self):
        ctx = InMemoryExecutionContext()
        RecipeSpec(recipe=FindShellSubprocessCalls(), execution_context=ctx).rewrite_run(
            python(
                """
                import subprocess
                from subprocess import Popen

                subprocess.run(f"ls {path}", shell=True)
                Popen("make install", shell=True)
                subprocess.run(["ls", path])
                """,
                """
                import subprocess
                from subprocess import Popen

                /*~~>*/subprocess.run(f"ls {path}", shell=True)
                /*~~>*/Popen("make install", shell=True)
                subprocess.run(["ls", path])
                """,
                path=Path("app.py"),
            )
        )
        assert rows(ctx) == [
            ShellSubprocessCall(source_path="app.py", function="subprocess.run", command='f"ls {path}"'),
            ShellSubprocessCall(source_path="app.py", function="subprocess.Popen", command='"make install"'),
        ]

    def test_names_the_function_the_module_defines_under_an_alias(self):
        ctx = InMemoryExecutionContext()
        RecipeSpec(recipe=FindShellSubprocessCalls(), execution_context=ctx).rewrite_run(
            python(
                """
                from subprocess import check_output as run

                out = run(command, shell=True)
                """,
                """
                from subprocess import check_output as run

                out = /*~~>*/run(command, shell=True)
                """,
                path=Path("app.py"),
            )
        )
        assert rows(ctx) == [
            ShellSubprocessCall(source_path="app.py", function="subprocess.check_output", command="command"),
        ]

    def test_reads_the_command_from_the_args_keyword(self):
        ctx = InMemoryExecutionContext()
        RecipeSpec(recipe=FindShellSubprocessCalls(), execution_context=ctx).rewrite_run(
            python(
                """
                import subprocess

                subprocess.call(shell=True, args="make clean")
                """,
                """
                import subprocess

                /*~~>*/subprocess.call(shell=True, args="make clean")
                """,
                path=Path("app.py"),
            )
        )
        assert rows(ctx) == [
            ShellSubprocessCall(source_path="app.py", function="subprocess.call", command='"make clean"'),
        ]

    def test_leaves_calls_that_do_not_use_the_shell(self):
        ctx = InMemoryExecutionContext()
        RecipeSpec(recipe=FindShellSubprocessCalls(), execution_context=ctx).rewrite_run(
            python(
                """
                import subprocess

                subprocess.run("ls", shell=False)
                runner.run("ls", shell=True)
                """
            )
        )
        assert rows(ctx) == []

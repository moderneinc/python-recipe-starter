from rewrite.test import RecipeSpec, python

from python_recipe_starter.remove_redundant_pass import RemoveRedundantPass


def test_removes_pass_when_block_has_other_statements():
    RecipeSpec(recipe=RemoveRedundantPass()).rewrite_run(
        python(
            """
            def foo():
                pass
                x = 1
            """,
            """
            def foo():
                x = 1
            """,
        )
    )


def test_removes_every_pass_when_block_has_other_statements():
    RecipeSpec(recipe=RemoveRedundantPass()).rewrite_run(
        python(
            """
            def foo():
                pass
                x = 1
                pass
            """,
            """
            def foo():
                x = 1
            """,
        )
    )


def test_keeps_passes_when_block_has_only_passes():
    RecipeSpec(recipe=RemoveRedundantPass()).rewrite_run(
        python(
            """
            def foo():
                pass
                pass
            """
        )
    )


def test_keeps_pass_when_it_is_the_only_statement():
    RecipeSpec(recipe=RemoveRedundantPass()).rewrite_run(
        python(
            """
            def foo():
                pass
            """
        )
    )

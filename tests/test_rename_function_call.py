from rewrite.test import RecipeSpec, python

from python_recipe_starter.rename_function_call import RenameFunctionCall


def test_renames_a_bare_call():
    spec = RecipeSpec(recipe=RenameFunctionCall(
        old_name="assertEquals",
        new_name="assertEqual",
    ))
    spec.rewrite_run(
        python(
            """
            assertEquals(a, b)
            """,
            """
            assertEqual(a, b)
            """,
        )
    )


def test_renames_a_qualified_call():
    spec = RecipeSpec(recipe=RenameFunctionCall(
        old_name="assertEquals",
        new_name="assertEqual",
    ))
    spec.rewrite_run(
        python(
            """
            self.assertEquals(a, b)
            """,
            """
            self.assertEqual(a, b)
            """,
        )
    )


def test_leaves_other_calls_unchanged():
    spec = RecipeSpec(recipe=RenameFunctionCall(
        old_name="assertEquals",
        new_name="assertEqual",
    ))
    spec.rewrite_run(
        python(
            """
            assertTrue(x)
            """
        )
    )

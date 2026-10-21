from rewrite.test import RecipeSpec, python

from python_recipe_starter.remove_zero_from_range import RemoveZeroFromRange


class TestRemoveZeroFromRange:
    def test_drops_a_zero_start(self):
        RecipeSpec(recipe=RemoveZeroFromRange()).rewrite_run(
            python(
                """
                a = range(0, n)
                b = range(1, n)
                """,
                """
                a = range(n)
                b = range(1, n)
                """,
            )
        )

    def test_leaves_a_call_with_an_unpacked_argument(self):
        RecipeSpec(recipe=RemoveZeroFromRange()).rewrite_run(
            python(
                """
                b = range(0, *bounds)
                """
            )
        )

    def test_leaves_a_function_that_shadows_range(self):
        RecipeSpec(recipe=RemoveZeroFromRange()).rewrite_run(
            python(
                """
                a = range(0, n)


                def f(range):
                    return range(0, n)
                """,
                """
                a = range(n)


                def f(range):
                    return range(0, n)
                """,
            )
        )

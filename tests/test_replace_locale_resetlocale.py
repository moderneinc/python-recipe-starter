from rewrite.test import RecipeSpec, python

from python_recipe_starter.replace_locale_resetlocale import ReplaceLocaleResetlocale


class TestReplaceLocaleResetlocale:
    def test_rewrites_a_call_through_the_module_under_the_files_name_for_it(self):
        RecipeSpec(recipe=ReplaceLocaleResetlocale()).rewrite_run(
            python(
                """
                import locale as loc

                loc.resetlocale()
                other.resetlocale()
                """,
                """
                import locale as loc

                loc.setlocale(loc.LC_ALL, "")
                other.resetlocale()
                """,
            )
        )

    def test_rewrites_a_call_by_name_and_replaces_its_import(self):
        RecipeSpec(recipe=ReplaceLocaleResetlocale()).rewrite_run(
            python(
                """
                from locale import resetlocale

                resetlocale()
                """,
                """
                import locale

                locale.setlocale(locale.LC_ALL, "")
                """,
            )
        )

    def test_leaves_a_call_where_the_module_name_is_taken(self):
        RecipeSpec(recipe=ReplaceLocaleResetlocale()).rewrite_run(
            python(
                """
                from locale import resetlocale

                locale = "C"
                resetlocale()
                """
            )
        )

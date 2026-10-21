# Python Recipe Starter

A starter repository for learning how to create [OpenRewrite](https://github.com/openrewrite/rewrite) recipes for Python. This repo includes example recipes with tests, demonstrating the full project setup you need to author, test, and run your own recipes.

## Getting started

New to OpenRewrite Python recipe development? Start with the [guide to writing a Python refactoring recipe](https://docs.moderne.io/user-documentation/recipes/authoring-recipes/writing-recipes/writing-python-recipes), and the [OpenRewrite documentation](https://docs.openrewrite.org/). The Python LST and parser live in the [`rewrite-python` module](https://github.com/openrewrite/rewrite/tree/main/rewrite-python).

## Quick start

You need Python 3.12 or newer. Clone this repository, create a virtual environment, and install the project with its development dependencies:

```bash
git clone git@github.com:moderneinc/python-recipe-starter.git
cd python-recipe-starter
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run the tests, the linter and the type checker:

```bash
pytest
ruff check
ty check
```

## Example recipes

This repository includes example recipes that demonstrate different authoring techniques:

* **[RemoveZeroFromRange](./src/python_recipe_starter/remove_zero_from_range.py)** — shortens `range(0, n)` to `range(n)`. Demonstrates a `pattern` that matches code by its structure and types, a `capture` with a `constraint`, a `template` built from what the pattern captured, and a precondition that skips files never calling `range`.
* **[ReplaceLocaleResetlocale](./src/python_recipe_starter/replace_locale_resetlocale.py)** — replaces `locale.resetlocale()`, removed in Python 3.13, with `locale.setlocale(locale.LC_ALL, "")`. Demonstrates a `MethodMatcher` that matches calls by their type rather than their name, a `template` whose `context` declares the imports its code needs, which the template binds in the file the way `maybe_bind` does, and `maybe_remove_import` for the import the rewrite leaves unused.

Before writing a recipe, check whether the SDK already ships it. [`rewrite.python.recipes`](https://github.com/openrewrite/rewrite/tree/main/rewrite-python/rewrite/src/rewrite/python/recipes) includes `ChangeMethodName`, `ChangeImport`, `RemovePass` and others, and their sources are worth reading next. [`ChangeMethodName`](https://github.com/openrewrite/rewrite/blob/main/rewrite-python/rewrite/src/rewrite/python/recipes/change_method_name.py) is configured through `option()` fields, [`RemovePass`](https://github.com/openrewrite/rewrite/blob/main/rewrite-python/rewrite/src/rewrite/python/recipes/remove_pass.py) deletes statements from a block, and [`ChangeImport`](https://github.com/openrewrite/rewrite/blob/main/rewrite-python/rewrite/src/rewrite/python/recipes/change_import.py) moves an import with `maybe_rebind`, renaming the references that read it.

## Project structure

```
python-recipe-starter/
├── src/
│   └── python_recipe_starter/
│       ├── __init__.py                # activate(): registers the recipes
│       ├── remove_zero_from_range.py
│       └── replace_locale_resetlocale.py
├── tests/
│   ├── test_remove_zero_from_range.py
│   └── test_replace_locale_resetlocale.py
├── pyproject.toml                     # package metadata + openrewrite.recipes entry point
└── .github/workflows/ci.yml
```

Each recipe declares its marketplace category with `@categorize` (`ReplaceLocaleResetlocale` lands under **Python > Migrate**). The `activate()` function in `__init__.py` installs each recipe under that category, and the `openrewrite.recipes` entry point in `pyproject.toml` is how the Moderne CLI discovers it.

## Running your recipes

To run these recipes against a real codebase, use the [Moderne CLI](https://docs.moderne.io/user-documentation/moderne-cli/getting-started/cli-intro) with [Python support configured](https://docs.moderne.io/user-documentation/moderne-cli/how-to-guides/python).

Install this package into the CLI's recipe marketplace, straight from the project directory:

```bash
mod config recipes pip install .
```

Then build the Python LSTs for your target repository and run a recipe by its name. A recipe with options takes each one as a `-P<option>=<value>` parameter.

```bash
mod build /path/to/your/repo
mod run /path/to/your/repo --recipe=com.yourorg.ReplaceLocaleResetlocale
```

## License

See the [LICENSE](./LICENSE) file for details.

# Python Recipe Starter

A starter repository for learning how to create [OpenRewrite](https://github.com/openrewrite/rewrite) recipes for Python. This repo includes example recipes with tests, demonstrating the full project setup you need to author, test, and run your own recipes.

## Getting started

New to OpenRewrite Python recipe development? Start with the [guide to writing a Python refactoring recipe](https://docs.moderne.io/user-documentation/recipes/recipe-authoring/writing-python-recipes), and the [OpenRewrite documentation](https://docs.openrewrite.org/). The Python LST and parser live in the [`rewrite-python` module](https://github.com/openrewrite/rewrite/tree/main/rewrite-python).

## Quick start

Clone this repository, create a virtual environment, and install the project with its development dependencies:

```bash
git clone git@github.com:moderneinc/python-recipe-starter.git
cd python-recipe-starter
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run the tests:

```bash
pytest
```

## Example recipes

This repository includes example recipes that demonstrate different authoring techniques:

* **[RenameFunctionCall](./src/python_recipe_starter/rename_function_call.py)** — renames calls to a function from one name to another (for example, `assertEquals` to `assertEqual`). Demonstrates a configurable recipe with `option()` fields and a visitor that returns a modified copy of a node.
* **[RemoveRedundantPass](./src/python_recipe_starter/remove_redundant_pass.py)** — removes `pass` statements that share a block with other statements. Demonstrates deleting a node by returning `None`, and using the visitor's `cursor` to inspect a node's surroundings.

## Project structure

```
python-recipe-starter/
├── src/
│   └── python_recipe_starter/
│       ├── __init__.py                # activate(): registers the recipes
│       ├── rename_function_call.py
│       └── remove_redundant_pass.py
├── tests/
│   ├── test_rename_function_call.py
│   └── test_remove_redundant_pass.py
├── pyproject.toml                     # package metadata + openrewrite.recipes entry point
└── .github/workflows/ci.yml
```

The `activate()` function in `__init__.py` installs each recipe into the marketplace, and the `openrewrite.recipes` entry point in `pyproject.toml` is how the Moderne CLI discovers it.

## Running your recipes

To run these recipes against a real codebase, use the [Moderne CLI](https://docs.moderne.io/user-documentation/moderne-cli/getting-started/cli-intro) with [Python support configured](https://docs.moderne.io/user-documentation/moderne-cli/how-to-guides/python).

Install this package into the CLI's recipe marketplace, straight from the project directory:

```bash
mod config recipes pip install .
```

Then build the Python LSTs for your target repository and run a recipe by its name, passing any options as `-P` parameters:

```bash
mod build /path/to/your/repo
mod run /path/to/your/repo --recipe=com.yourorg.RenameFunctionCall -Pold_name=assertEquals -Pnew_name=assertEqual
```

## License

See the [LICENSE](./LICENSE) file for details.

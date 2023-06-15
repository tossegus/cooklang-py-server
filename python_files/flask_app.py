"""
Flask application

The main page just re-directs to /recipes since that is
the most relevant page anyway. And who wants a 'Welcome here' page anyway?
"""
import os
import re
from flask import Flask, render_template, request
from datawrapper import DataWrapper
from recipe import Recipe
from shoppinglist import ShoppingList
from helper import convert_str_to_int
from cooklang import parseRecipe

shopping_list = []
app = Flask(__name__)


def add_to_shoppinglist(path):
    """Add chosen recipe to the shopping list"""
    if path not in shopping_list:
        print("Added to list")
        # Only add each recipe once.
        shopping_list.append(path)


@app.route("/")
def home():
    """Home page. Redirects to recipes page"""
    return recipes()


@app.route("/recipes/")
def recipes():
    """
    Show the recipes page. A lot of data mangling happens here.
    Accessible via menu bar.
    """
    server_item = DataWrapper(os.getcwd())
    recipe_tree = server_item.recipe_tree.tree
    return render_template("recipes.html", recipe_tree=recipe_tree)


@app.route("/shoppinglist/", methods=["POST", "GET"])
def shoppinglist():
    """
    Show the Shopping List page. This page is empty if no recipes have
    been added in recipes view.
    Accissble via menu bar.
    """
    if request.method == "POST":
        print("Handle post")
        url = request.form.get("button")
        if url in shopping_list:
            shopping_list.remove(url)

    int_dict = {}

    if not shopping_list:
        # The shopping_list is empty
        print("Empty list")
    else:
        print("List not empty")
        for item in shopping_list:
            filename = os.path.basename(item)
            int_dict[filename] = item
        print("List is not empty")
    return render_template("shopping_list.html", recipes=int_dict)


@app.route("/printshoppinglist/", methods=["POST", "GET"])
def printshoppinglist():
    """Displays the items in the shopping list. Only available through Shopping List"""
    global shopping_list
    int_shoppinglist = ShoppingList()
    int_dict = {}
    if request.method == "POST":
        if request.form.get("button") == "empty_list":
            shopping_list = []
    else:
        if not shopping_list:
            print("Shopping list empty")
        else:
            for item in shopping_list:
                int_shoppinglist.add_recipe(parseRecipe(item))

        for item in int_shoppinglist.items:
            int_dict[
                item
            ] = f"{int_shoppinglist.items[item].quantity}{int_shoppinglist.items[item].unit}"

    return render_template("print_shopping_list.html", shoppinglist=int_dict)


@app.route("/recipe/", methods=["POST", "GET"])
def recipe():
    """Recipe page. Show the selected recipe."""
    path = request.args.get("recipe_path")
    if request.method == "POST":
        print("Got button press!")
        if request.form.get("add_to_recipe") == "add":
            # add this recipe to the shopping_list
            add_to_shoppinglist(path)

    else:
        path = request.args.get("recipe_path")

    int_recipe = Recipe(path)
    ingredients = []
    for item in int_recipe.ingredients:
        quantity = convert_str_to_int(item["quantity"])
        ingredients.append(f'{item["name"]} {quantity}{item["units"]}')

    step_list = int_recipe.steps_str.split("\n")
    step_dict = {}
    for item in step_list:
        match = re.search("[^ ]", item)
        if match:
            index = match.start()
        else:
            index = 0
        # Strip leading white spaces
        key = item[index:]
        step_dict[key] = "TAB" if key.startswith("[") else "BASE"

    return render_template(
        "recipe.html",
        path=path,
        metadata=int_recipe.metadata,
        ingredients=ingredients,
        steps=step_dict,
    )


def main():
    """Start the application. Entry point for the flask application"""
    # Start application
    app.run(debug=True)


if __name__ == "__main__":
    main()

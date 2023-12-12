"""
6.101 Lab 6:
Recipes
"""

import pickle
import sys

sys.setrecursionlimit(20_000)
# NO ADDITIONAL IMPORTS!


def make_recipe_book(recipes):
    """
    Given recipes, a list containing compound and atomic food items, make and
    return a dictionary that maps each compound food item name to a list
    of all the ingredient lists associated with that name.
    """
    compound_dict = {}
    # for each item in the recipe book
    for items in recipes:
        # if the item in recipe is a compound
        if items[0] == "compound":
            # adds each ingredient to the dict of compounds
            compound_dict.setdefault(items[1], []).append(items[2])
    return compound_dict


def make_atomic_costs(recipes):
    """
    Given a recipes list, make and return a dictionary mapping each atomic food item
    name to its cost.
    """
    atomic_dict = {}
    for items in recipes:
        # if the item in recipe is a atomic
        if items[0] == "atomic":
            # sets the atomic item to its cost
            atomic_dict[items[1]] = items[2]
    return atomic_dict

def lowest_cost(recipes, food_item, forbidden=[]):
    """
    Given a recipes list and the name of a food item, return the lowest cost of
    a full recipe for the given food item.
    """
    # Create the compound and atomic costs dictionaries
    compound_dict = make_recipe_book(recipes)
    atomic_costs = make_atomic_costs(recipes)

    # helper recursive function to get cost of item
    def recursive_cost_helper(item):
        """
        Recursive helper function to calculate the cost of a food item.
        """
        # if item is forbidden
        if item in forbidden:
            return None
        # If the food item is atomic, return its cost
        if item in atomic_costs:
            return atomic_costs[item]
        # if the item isn't in the store
        if item not in compound_dict:
            return None
        # If the food item is compound, calculate the cost for each ingredient list
        costs = []
        # for ingredients in the compound
        for ingredient_list in compound_dict[item]:
            # make cost as 0 in case compound could have multiple ingredients
            cost = 0
            # goes over each ingredient and its quantity
            for ingredient, quantity in ingredient_list:
                ingredient_cost = recursive_cost_helper(ingredient)
                # if ingredient cost does not exist, then return None
                if ingredient_cost is None:
                    cost = None
                    break
                cost += ingredient_cost * quantity
            # put cost into costs list
            costs.append(cost)

        # Return the minimum cost among all ingredient lists
        # makes a cost list without None
        real_cost = [cost for cost in costs if cost is not None]
        # if real cost is empty return None
        if not real_cost:
            return None
        return min(real_cost)

    return recursive_cost_helper(food_item)


def scale_recipe(flat_recipe, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.
    """
    # dictionary comprehension to return value scaled by n
    return {key: value * n for key, value in flat_recipe.items()}


def make_grocery_list(flat_recipes):
    """
    Given a list of flat_recipe dictionaries that map food items to quantities,
    return a new overall 'grocery list' dictionary that maps each ingredient name
    to the sum of its quantities across the given flat recipes.

    For example,
        make_grocery_list([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}
    """
    ingredient_count = {}
    for recipes in flat_recipes:
        for ingredient in recipes:
            #adds values to it to ingredient key, or makes an ingredient key
            if ingredient in ingredient_count:
                ingredient_count[ingredient] += recipes[ingredient]
            else:
                ingredient_count[ingredient] = recipes[ingredient]
    return ingredient_count


def cheapest_flat_recipe(recipes, food_item, forbidden=[]):
    """
    Given a recipes list and the name of a food item, return a dictionary
    (mapping atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.
    """
    compound_dict = make_recipe_book(recipes)
    atomic_costs = make_atomic_costs(recipes)

    def cheapest_flat_recipe_helper(item):
        # if item is forbidden
        if item in forbidden:
            return None
        # If the food item is atomic
        if item in atomic_costs:
            return {item: 1}
        # If the food item not in the compound dictionary, return None
        if item not in compound_dict:
            return None
        # If the food item is compound, calculate the cost for each ingredient list
        cheapest_recipe = None
        # makes the initial minimum cost be positive infinity
        min_cost = float("inf")
        # goes through every ingridient of item
        for ingredient_list in compound_dict[item]:
            total_cost = 0
            flat_recipe = {}
            for ingredient, quantity in ingredient_list:
                ingredient_cost = lowest_cost(recipes, ingredient, forbidden)
                # If the ingredient cost is None, skip this ingredient list
                if ingredient_cost is None:
                    #make total cost infinity so that this path isn't considered
                    total_cost = float("inf")
                    break
                # add ingridient cost and quantity to total cost
                total_cost += ingredient_cost * quantity
                # Recursively get the flat recipe for the ingredient
                ingredient_flat_recipe = cheapest_flat_recipe_helper(ingredient)
                # If the ingredient flat recipe is None, skip this ingredient list
                if ingredient_flat_recipe is None:
                    #make total cost infinity so that this path isn't considered
                    total_cost = float("inf")
                    break
                # Scale the ingredient flat recipe by its quantity
                scaled_flat_recipe = scale_recipe(
                    ingredient_flat_recipe, quantity
                )
                # Add the scaled ingredient flat recipe to the overall flat recipe
                for key, value in scaled_flat_recipe.items():
                    flat_recipe[key] = flat_recipe.get(key, 0) + value
            # make cheapest price the lowest minimum cost
            print(flat_recipe)
            if total_cost < min_cost:
                min_cost = total_cost
                cheapest_recipe = flat_recipe
        return cheapest_recipe

    return cheapest_flat_recipe_helper(food_item)


def ingredient_mixes(flat_recipes):
    """
    Given a list of lists of dictionaries, where each inner list represents all
    the flat recipes for a certain ingredient, compute and return a list of flat
    recipe dictionaries that represent all the possible combinations of
    ingredient recipes.
    """
    # if flat_recipes is empty, return a list with an empty dictionary
    if not flat_recipes:
        return [{}]
    # Take the first recipe of recipes
    first_recipes = flat_recipes[0]
    # Recursively call ingredient_mixes on the rest of the flat_recipes
    rest_mixes = ingredient_mixes(flat_recipes[1:])
    # List to store the result
    result = []
    # For each recipe in the first list
    for item in first_recipes:
        # For each result from the recursive call
        for mixes in rest_mixes:
            # Add the merged dictionary to the result list
            result.append(make_grocery_list([item, mixes]))
    return result


def all_flat_recipes(recipes, food_item, forbidden=[]):
    """
    Given a list of recipes and the name of a food item, produce a list (in any
    order) of all possible flat recipes for that category.

    Returns an empty list if there are no possible recipes
    """
    compound_dict = make_recipe_book(recipes)
    atomic_costs = make_atomic_costs(recipes)

    def all_flat_recipes_helper(item):
        # If the item is forbidden, return an empty list
        if item in forbidden:
            return []
        # If the food item is atomic, return its quantity
        if item in atomic_costs:
            return [{item: 1}]
        # If the food item isn't in the compound dictionary, return an empty list
        if item not in compound_dict:
            return []
        # For compound items, get all possible flat recipes
        all_recipes = []
        for ingredient_list in compound_dict[item]:
            ingredient_flat_recipes = []
            # valid to see whether ingredient list can be plausible
            valid = True
            # For each ingredient in the compound item
            for ingredient, quantity in ingredient_list:
                flat_recipes_ingredient = all_flat_recipes_helper(ingredient)
                # If no recipes exist for an ingredient, skip this list
                if not flat_recipes_ingredient:
                    valid = False
                    break
                # Scale the ingredient's recipes by its quantity
                scaled_flat_recipes = [
                    scale_recipe(recipe, quantity)
                    for recipe in flat_recipes_ingredient
                ]
                ingredient_flat_recipes.append(scaled_flat_recipes)
            # If all ingredients have valid recipes, combine them
            if valid:
                combined_recipes = ingredient_mixes(ingredient_flat_recipes)
                all_recipes.extend(combined_recipes)

        return all_recipes

    result = all_flat_recipes_helper(food_item)
    # remove empty dictionaries and return in format of list of dictionaries
    return [recipe for recipe in result if recipe]


# HELPER FUNCTIONS


def sum_costs(atomic_dict):
    """
    Given a dictionary with atomic foods as keys and their
    cost as their values, return the sum of the total costs
    """
    return sum(costs for costs in atomic_dict.values())


def multiple_recipes(compound_dict):
    """
    Given a dictionary with compound foods as keys and their
    ingredients as values, return the how many can be made
    in multiple ways
    """
    # list of values with multiple recipes
    multiple_recipes_ls = [
        recipes for recipes in compound_dict if len(compound_dict[recipes]) > 1
    ]
    # returns length of the list to see how many foods have multiple ways of being made
    return len(multiple_recipes_ls)


# IF NAME == MAIN
if __name__ == "__main__":
    dairy_recipes = [
        ("compound", "milk", [("cow", 2), ("milking stool", 1)]),
        ("compound", "cheese", [("milk", 1), ("time", 1)]),
        ("compound", "cheese", [("cutting-edge laboratory", 11)]),
        ("atomic", "milking stool", 5),
        ("atomic", "cutting-edge laboratory", 1000),
        ("atomic", "time", 10000),
        ("atomic", "cow", 100),
    ]
    # ALL Flat prices test
    cookie_recipes = [
        ("compound", "cookie sandwich", [("cookie", 2), ("ice cream scoop", 3)]),
        ("compound", "cookie", [("chocolate chips", 3)]),
        ("compound", "cookie", [("sugar", 10)]),
        ("atomic", "chocolate chips", 200),
        ("atomic", "sugar", 5),
        ("compound", "ice cream scoop", [("vanilla ice cream", 1)]),
        ("compound", "ice cream scoop", [("chocolate ice cream", 1)]),
        ("atomic", "vanilla ice cream", 20),
        ("atomic", "chocolate ice cream", 30),
    ]
    # print(all_flat_recipes(cookie_recipes,'cookie sandwich'))
    print(all_flat_recipes(cookie_recipes, "cookie sandwich"))

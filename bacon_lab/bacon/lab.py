"""
6.101 Lab 3:
Bacon Number
"""

#!/usr/bin/env python3

import pickle

# NO ADDITIONAL IMPORTS ALLOWED!


def transform_data(raw_data):
    """
    Make a dictionary of dictionaries, for actors to actors, actor to movies,
    and movies to actors. First, create a key corresponding to whatever value is needed,
    for example, for the actor to actors dictionary, actor1 is used as a key and then
    actor2 is added to it. However, if actor1 is already a key, then setdefault is used
    with set() in order to make sure there are not multiple dictionaries with the
    same key. However, if the key exists, then setdefault will initiate it
    with an empty set, which is then added to by actor
    """
    actor_actor = {}
    actor_movies = {}
    movies_actor = {}

    for actor_id_1, actor_id_2, film_id in raw_data:
        # Node connecting actors
        actor_actor.setdefault(actor_id_1, set()).add(actor_id_2)
        actor_actor.setdefault(actor_id_2, set()).add(actor_id_1)
        # Map actors to each movie
        actor_movies.setdefault(actor_id_1, set()).add(film_id)
        actor_movies.setdefault(actor_id_2, set()).add(film_id)
        #  Map movies to each actor
        movies_actor.setdefault(film_id, set()).add(actor_id_1)
        movies_actor.setdefault(film_id, set()).add(actor_id_2)

    # dictionary of dictionaries
    transformed_data = {
        "actor_actor": actor_actor,
        "actor_movies": actor_movies,
        "movies_actor": movies_actor,
    }
    return transformed_data


def acted_together(transformed_data, actor_id_1, actor_id_2):
    node = transformed_data["actor_actor"]
    # if actor2 is in the actor1 dictionary or if the ids are the same, returns true
    if actor_id_2 in node[actor_id_1] or actor_id_1 == actor_id_2:
        return True
    return False


def actors_with_bacon_number(transformed_data, n):
    """
    Given a bacon number 'n', returns a set containing all actors with
    that bacon number
    """
    # node of actors
    node = transformed_data["actor_actor"]
    # Kevin bacon's id is 4724, start set with it
    actors_bn = {4724}
    # keeps track of seen actors
    seen = {4724}
    # iterates n times to find bacon number
    for _ in range(n):
        # keep track of actors found in current bacon number
        new_actors = set()
        for actor in actors_bn:
            # Find all linked actors
            # gets the values of actors that acted with previous bn, else gets empty set
            linked_actors = node.get(actor, set())
            # Add linked actors to the new set, not including seen actors
            new_actors.update(linked_actors - seen)
        # updates seen so no more actors are repeated
        seen.update(new_actors)
        # Make actors_bn the current actors with the bn
        actors_bn = new_actors
        # if new_actors is empty, the loop is broken
        if not new_actors:
            break
    return actors_bn


def bacon_path(transformed_data, actor_id):
    """
    Implements a breath-first-search algorithm with the graph data type in
    order to find the shortest path from an actor to kevin bacon, in this
    case, since this problem is a subset of actor to actor, then
    actor to actor is called with kevin bacon's id used as actor_id_1
    """
    return actor_to_actor_path(transformed_data, 4724, actor_id)


def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    """
    Implements a breath-first-search algorithm with the graph data type in
    order to find the shortest path from an actor to another actor
    """
    return actor_path(transformed_data, actor_id_1, lambda n: n == actor_id_2)


def actor_to_movie_path(transformed_data, actor_id_1, actor_id_2):
    """
    list of movie names that connects two arbitrary actors
    """
    # dictionary of movies that says which actors acted in it
    node = transformed_data["movies_actor"]
    # list of actors that connects two actors
    ls_actors = actor_to_actor_path(transformed_data, actor_id_1, actor_id_2)
    # list to store movies that connect each actor
    ls_movies = []
    # goes through each actor
    for index in range(len(ls_actors) - 1):
        for movies in node:
            # checks for movies that both actors acted in
            if (
                ls_actors[index] in node[movies]
                and ls_actors[index + 1] in node[movies]
            ):
                ls_movies.append(movies)
    return ls_movies


def actor_path(transformed_data, actor_id_1, goal_test_function):
    """
    Implements a breath-first-search algorithm with the graph data type in
    order to find the shortest path from an actor to an actor that
    satisfies the goal_test_function
    """
    father = {}  # dictionary to store where neighbors came from
    node = transformed_data["actor_actor"]
    ls = []  # list to store path
    seen = {actor_id_1}
    queue = [actor_id_1]  # queue begins with kevin bacon
    # while queue is non-empty
    while queue:
        # removes first item of queue and adds it to actor
        # actor is the last element of path
        actor = queue.pop(0)
        if goal_test_function(actor):
            ls.append(actor)
            temp_actor = actor  # stores temporary actor
            while ls[-1] != actor_id_1:
                ls.append(father[temp_actor])
                temp_actor = father[temp_actor]
            return ls[::-1]  # Return the path when the actor is found
        # for each actor connecting to this actor
        for neighbor in node.get(actor, set()):
            # if this connecred actor hasn't been seen yet
            if neighbor not in seen:
                queue.append(neighbor)
                father[neighbor] = actor
                # actor gets added to seen
                seen.add(neighbor)
    return None  # Return None if no path exists


def actors_connecting_films(transformed_data, film1, film2):
    """
    returns the shortest list of actors that connect two
    movies together. Will do a breath for search for this function
    """
    # node that stores actors that acted in each movie
    movies_actor = transformed_data["movies_actor"]
    # list that the stores the shortest path from actor to actor
    ls_shortest = []
    # for actors that acted in film1
    for actors in movies_actor[film1]:
        #finds shortest path from actor of film1 to another actor of film2
        ls_actors = actor_path(
            transformed_data, actors, lambda n: n in movies_actor[film2]
        )
        # used to find the shortest path from an actor of film1 to actor of film2
        if len(ls_actors) < len(ls_shortest) or not ls_shortest:
            ls_shortest = ls_actors
    return ls_shortest


# HELPER FUNCTIONS


# GET KEY OF DICTIONARY GIVEN VALUE
def get_key(val, dict):
    for key, value in dict.items():
        if val == value:
            return key
    return None


# TRANSFORM ACTOR_ID INTO ACTOR NAMES
def id_to_name(actor_id_ls):
    """
    Takes a list of actor_ids and converts them into a list
    of the name of each actor
    """
    # list to store names of actors
    ls_names = []
    with open("resources/names.pickle", "rb") as f:
        names = pickle.load(f)
        # adds name of actor to the list, using the actor id as a key
        for _, actor_id in enumerate(actor_id_ls):
            ls_names.append(get_key(actor_id, names))
    return ls_names


# TRANSFORM MOVIE_ID INTO MOVIE NAMES
def id_to_movie(movie_ls):
    """
    Takes a list of movie ids and converts them into a list
    of the name of each movie
    """
    # list to store names of movies
    ls_names = []
    with open("resources/movies.pickle", "rb") as f:
        names = pickle.load(f)
        # adds name of movie to the list, using the movie id as a key
        for _, movie in enumerate(movie_ls):
            ls_names.append(get_key(movie, names))
    return ls_names


if __name__ == "__main__":
    # acted together test
    with open("resources/small.pickle", "rb") as f:
        raw_smalldb = pickle.load(f)
        smalldb = transform_data(raw_smalldb)
        # print(acted_together(smalldb, 94976, 583590))

    # bacon number of 6 test
    with open("resources/large.pickle", "rb") as f:
        raw_largedb = pickle.load(f)
        largedb = transform_data(raw_largedb)
        print(id_to_name(actors_with_bacon_number(largedb, 6)))
    # load names.pickle
    with open("resources/names.pickle", "rb") as f:
        namesdb = pickle.load(f)
        #print(namesdb)
    # load tinypickle
    with open("resources/tiny.pickle", "rb") as f:
        tinydb = pickle.load(f)
        # print(tinydb)
    # path from kevin bacon to niyala ban
    with open("resources/large.pickle", "rb") as f:
        raw_largedb = pickle.load(f)
        largedb = transform_data(raw_largedb)
        print(id_to_name(bacon_path(largedb, 1115072)))
    # path from linnea hillberg to billy crudup
    with open("resources/large.pickle", "rb") as f:
        raw_largedb = pickle.load(f)
        largedb = transform_data(raw_largedb)
        print(id_to_name(actor_to_actor_path(largedb, 565664, 8289)))
    # movie path from Clara Hopkins Daniels to Vjeran Tin Turk
    with open("resources/large.pickle", "rb") as f:
        raw_largedb = pickle.load(f)
        largedb = transform_data(raw_largedb)
        print(id_to_movie(actor_to_movie_path(largedb, 58571, 1367972)))

    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.

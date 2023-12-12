"""
6.101 Lab 12:
LISP Interpreter Part 1
"""

#!/usr/bin/environment python3

import sys
import doctest

sys.setrecursionlimit(20_000)

# NO ADDITIONAL IMPORTS!

#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    # split string into lines
    lines = source.split("\n")
    # remove comments from lines
    new_lines = [line.split(";")[0] for line in lines]
    # turn lines back into a single string
    new_source = " ".join(new_lines)
    #  empty list to store tokens
    tokens = []
    #  empty string to store current token
    current_token = ""
    # for each character in new source
    for char in new_source:
        # if the character is a parenthesis
        if char in ["(", ")"]:
            # add the current token to tokens list if it's not empty
            if current_token:
                tokens.append(current_token)
                # reset current token into an empty string
                current_token = ""
            # add the parenthesis as a separate token
            tokens.append(char)
        # if the character is a white spice
        elif char.isspace():
            # if token is not empty
            if current_token:
                # add token to token list
                tokens.append(current_token)
                # reset current token to an empty string
                current_token = ""
        # else add other char it to the current token
        else:
            current_token += char

    # add the last token to the list if it exists
    if current_token:
        tokens.append(current_token)
    # return the list of tokens
    return tokens


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """

    def parse_expression(index):
        """
        Helper function to parse expressions
        """
        # if index is greater than token length, then raise an error
        if index >= len(tokens):
            raise SchemeSyntaxError("Unexpected end of tokens")
        # get the current token
        token = tokens[index]
        # if token is a left open parenthesis
        if token == "(":
            # move to the next token
            index += 1
            # make a new list for expressions
            expressions = []
            # while index is less than tokens length and tokens isn't a right parenthesis
            while index < len(tokens) and tokens[index] != ")":
                # parse the subexpression
                subexpression, index = parse_expression(index)
                # add the subexpression to expressions
                expressions.append(subexpression)
            # if index is equal to tokens length, then raise an error
            if index == len(tokens):
                raise SchemeSyntaxError("Missing parenthesis")
            # return the list of expressions and the next index
            return expressions, index + 1
        # if the token is right parenthesis, then raise an unexpected error
        elif token == ")":
            raise SchemeSyntaxError("Unexpected parenthesis")
        # else if the token is a number or symbol, then return the token and the next index
        else:
            return number_or_symbol(token), index + 1
    # if the token list is empty raise an error
    if len(tokens) == 0:
        raise SchemeSyntaxError("No tokens to parse")
    # parse from the first token
    parsed_expression, next_index = parse_expression(0)
    # if next index is not in the length of tokens, then raise an error
    if next_index != len(tokens):
        raise SchemeSyntaxError("Too many tokens")

    return parsed_expression


######################
# Built-in Functions #
######################


# Function to handle subtraction
def subtract(arguments):
    """
    Helper function to subtract arguments
    """
    # if there are no arguments
    if not arguments:
        # raise an error
        raise SchemeEvaluationError("Subtraction requires at least one argument")

    # if only one argument in arguments
    if len(arguments) == 1:
        # return the negative of said argument
        return -arguments[0]

    # else make result start with argument
    result = arguments[0]
    # for each argument left in arguments
    for argument in arguments[1:]:
        # subtract the argument from the result
        result -= argument
    return result


# Function to handle multiplication
def multiply(arguments):
    """
    Helper function to multiply arguments
    """
    # if no argument
    if not arguments:
        # return 1
        return 1

    # if only one argument
    if len(arguments) == 1:
        # return the first argument
        return arguments[0]

    # else, start with the first argument
    result = arguments[0]
    # for each argument in the remaining arguments
    for argument in arguments[1:]:
        # multiply the argument with the result
        result *= argument
    return result


# Function to handle division
def divide(arguments):
    """
    Helper function to divide arguments
    """
    # if there are no arguments, raise an error
    if not arguments:
        raise SchemeEvaluationError("Division requires at least one argument")

    # case fror when there is a single argument
    if len(arguments) == 1:
        # return reciprocal of the argument
        return 1 / arguments[0]

    # else start with the first argument
    result = arguments[0]

    # for each argument in the remaining arguments
    for argument in arguments[1:]:
        # check if the argument is zero
        if argument == 0:
            # raise an error if so
            raise SchemeEvaluationError("Cannot divide by zero")
        # else divide the result by the argument
        result /= argument
    return result


# Dictionary mapping built-in function names to their implementations
scheme_builtins = {
    # sum all arguments
    "+": sum,
    # subtract all arguments
    "-": subtract,
    # multiplies all arguments
    "*": multiply,
    # divide all arguments
    "/": divide,
}

##############
# Frame and Functions Classes #
##############


# Class to represent frames
class Frame:
    """
    Class that represents a frame in the Scheme interpreter
    """

    def __init__(self, parent=None):
        """
        Initialize a new frame with an optional parent frame
        """
        # dictionary to store variable bindings in this frame
        self.bindings = {}
        # parent frame from which to inherit bindings
        self.parent = parent

    def define(self, name, value):
        """
        Define or update a variable in this frame
        """
        # bind the variable name to value
        self.bindings[name] = value

    def get(self, name):
        """
        Get the value of a variable in frame or parent frames
        """
        # if the name is in the frame's bindins
        if name in self.bindings:
            # return its value
            return self.bindings[name]
        # if frame has parents
        elif self.parent is not None:
            # search in the parent frame
            return self.parent.get(name)
        # else if no parent frames are left raise an error
        else:
            raise SchemeNameError(f"Name {name} is not defined")


# Class to represent functions
class Function:
    """
    Class that represents user defined function in scheme interpreter
    """

    def __init__(self, parameters, body, defining_frame):
        """
        initialize the function with parameters, body, and defining frame
        """
        # list of parameter names
        self.parameters = parameters
        # body of function
        self.body = body
        # frame in which the function is defined
        self.defining_frame = defining_frame

    def __call__(self, arguments):
        """
        make the function callable
        """
        # if the length of arguments is not the same as the length of parameters
        if len(arguments) != len(self.parameters):
            # Raise error
            raise SchemeEvaluationError(
                "number of arguments does not match number of parameters"
            )
        # create new frame for this function call, with defining frame as parent
        call_frame = Frame(parent=self.defining_frame)
        # make each arguments go with its corresponding parameter in the new frame
        for parameter, argument in zip(self.parameters, arguments):
            # define parameter in the call frame
            call_frame.define(parameter, argument)
        # evaluate the function
        return evaluate(self.body, call_frame)


##############
# Evaluation #
##############


# make a global frame
global_environment = Frame()
# make global frame have built in scheme functions
for name, function in scheme_builtins.items():
    # define each function with its name and what it does
    global_environment.define(name, function)


def result_and_frame(expression, environment=None):
    """
    Evaluates scheme expression in the given environment and returns the result or makes the new environment
    and returns the result of the new environment
    """
    # if there is no environment
    if environment is None:
        # create a new frame with global_environment as the parent
        environment = Frame(parent=global_environment)
    # evaluate the expression in the environment
    result = evaluate(expression, environment)
    # return expression and environment where it was made
    return result, environment


def evaluate(tree, environment=None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    # if environment is none
    if environment is None:
        # create a new environment with global_environment as the parent
        environment = Frame(parent=global_environment)

    # if tree is a list
    if isinstance(tree, list):
        # for lambda expressions
        if tree[0] == "lambda":
            # get the parameters and body of lambda
            _, parameters, body = tree
            # return a new function object with these
            return Function(parameters, body, environment)

        # for define expressions
        elif tree[0] == "define":
            # if it's a shorthand function definition
            if isinstance(tree[1], list):
                # get the function name and parameters
                func_name, *parameters = tree[1]
                # get the function's body
                func_body = tree[2]
                # create the function with this information
                func = Function(parameters, func_body, environment)
                # define the function in the environment
                environment.define(func_name, func)
                return func
            # else if its a normal variable
            else:
                # get name and expression
                _, name, expression = tree
                # evaluate the expression
                value = evaluate(expression, environment)
                # define the variable in the environment
                environment.define(name, value)
                return value
        # for function calls
        else:
            # evaluate each element in the expression
            evaluated_elements = [evaluate(child, environment) for child in tree]
            # if the first element isn't a function
            if not callable(evaluated_elements[0]):
                # raise an error
                raise SchemeEvaluationError(
                    "First element in list is not a callable function"
                )
            # Call the function
            function = evaluated_elements[0]
            # get the arguments to give to function
            arguments = evaluated_elements[1:]
            # return the result of the function with the arguments
            return function(arguments)
    # if tree is a number or float
    elif isinstance(tree, (int, float)):
        # just return tree
        return tree
    # if tree is a string
    elif isinstance(tree, str):
        # get it in the environment
        return environment.get(tree)
    # else return an error
    else:
        raise SchemeEvaluationError(f"Unknown expression type: {type(tree)}")


########
# REPL #
########

import os
import re
import sys
import traceback
from cmd import Cmd

try:
    import readline
except:
    readline = None


def supports_color():
    """
    Returns True if the running system's terminal supports color, and False
    otherwise.  Not guaranteed to work in all cases, but maybe in most?
    """
    plat = sys.platform
    supported_platform = plat != "Pocket PC" and (
        plat != "win32" or "ANSICON" in os.environ
    )
    # IDLE does not support colors
    if "idlelib" in sys.modules:
        return False
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    if not supported_platform or not is_a_tty:
        return False
    return True


class SchemeREPL(Cmd):
    """
    Class that implements a Read-Evaluate-Print Loop for our Scheme
    interpreter.
    """

    history_file = os.path.join(os.path.expanduser("~"), ".6101_scheme_history")

    if supports_color():
        prompt = "\033[96min>\033[0m "
        value_msg = "  out> \033[92m\033[1m%r\033[0m"
        error_msg = "  \033[91mEXCEPTION!! %s\033[0m"
    else:
        prompt = "in> "
        value_msg = "  out> %r"
        error_msg = "  EXCEPTION!! %s"

    keywords = {
        "define",
        "lambda",
        "if",
        "equal?",
        "<",
        "<=",
        ">",
        ">=",
        "and",
        "or",
        "del",
        "let",
        "set!",
        "+",
        "-",
        "*",
        "/",
        "#child",
        "#f",
        "not",
        "nil",
        "cons",
        "list",
        "cat",
        "cdr",
        "list-ref",
        "length",
        "append",
        "begin",
    }

    def __init__(self, use_frames=False, verbose=False):
        self.verbose = verbose
        self.use_frames = use_frames
        self.global_frame = None
        Cmd.__init__(self)

    def preloop(self):
        if readline and os.path.isfile(self.history_file):
            readline.read_history_file(self.history_file)

    def postloop(self):
        if readline:
            readline.set_history_length(10_000)
            readline.write_history_file(self.history_file)

    def completedefault(self, text, line, begidx, endidx):
        try:
            bound_vars = set(self.global_frame)
        except:
            bound_vars = set()
        return sorted(i for i in (self.keywords | bound_vars) if i.startswith(text))

    def onecmd(self, line):
        if line in {"EOF", "quit", "QUIT"}:
            print()
            print("bye bye!")
            return True

        elif not line.strip():
            return False

        try:
            token_list = tokenize(line)
            if self.verbose:
                print("tokens>", token_list)
            expression = parse(token_list)
            if self.verbose:
                print("expression>", expression)
            if self.use_frames:
                output, self.global_frame = result_and_frame(
                    *(
                        (expression, self.global_frame)
                        if self.global_frame is not None
                        else (expression,)
                    )
                )
            else:
                output = evaluate(expression)
            print(self.value_msg % output)
        except SchemeError as e:
            if self.verbose:
                traceback.print_tb(e.__traceback__)
                print(self.error_msg.replace("%s", "%r") % e)
            else:
                print(self.error_msg % e)

        return False

    completenames = completedefault

    def cmdloop(self, intro=None):
        while True:
            try:
                Cmd.cmdloop(self, intro=None)
                break
            except KeyboardInterrupt:
                print("^C")


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    SchemeREPL(use_frames=False, verbose=False).cmdloop()

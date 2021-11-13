import doctest
###########################
# Snek-related Exceptions #
###########################
class SnekError(Exception):
    """
    A type of exception to be raised if there is an error with a Snek
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """
    pass

class SnekSyntaxError(SnekError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """
    pass

class SnekNameError(SnekError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """
    pass

class SnekEvaluationError(SnekError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SnekNameError.
    """
    pass

############################
# Tokenization and Parsing #
############################

def number_or_symbol(x):
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
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return x

def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Snek
                      expression
    """
    new_source = ""
    skip = False #tracks comments ;
    for s in source:
        if s == ';':
            skip = True
        if skip:
            if s == '\n':
                skip = False
        if not skip: #adds spaces between relevant expressions to allow split()
            if s in '()':
                new_source+=" "+s+" "
            else:
                new_source+=s
    return new_source.split()

def find_paren(tokens):
    '''
    Given a list of tokens that starts with a left paren, returns the index of the matching right paren
    '''
    lCount = 0
    rCount = 0
    for i, t in enumerate(tokens):
        if t == '(':
            lCount += 1
        if t == ')':
            rCount += 1
        if rCount == lCount:
            return i
    raise SnekSyntaxError

def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens

    In: ['(', '+', '2', '(', '-', '5', '3', ')', '7', '8', ')']
    Out: ['+', 2, ['-', 5, 3], 7, 8]

    In: ['(', 'define', 'circle-area', '(', 'lambda', '(', 'r', ')', '(', '*', '3.14', '(', '*', 'r', 'r', ')', ')', ')', ')']
    Out: ['define', 'circle-area', ['lambda', ['r'], ['*', 3.14, ['*', 'r', 'r']]]]

    In: ['(', 'cat', '(', 'dog', '(', 'tomato' ,')' , ')', ')']
    Out: ['cat',['dog',['tomato']]]

    In: ['(', 'a', '(', 'b', '(', 'c', ')', '(', 'd', 'e', ')', '(', '(', '(', '(', 'f', ')', ')', ')', ')', ')', ')']
    Out: ['a', ['b', ['c'], ['d', 'e'], [[[['f']]]]]]
    """
    def p_helper(tokens,out,brackets):
        '''
        Given out and tokens, returns a parsed version of tokens and adds it to out
        '''
        if tokens == []:
            return out
        if tokens[0] == '(':
            res = p_helper(tokens[1:find_paren(tokens)],[],True)
            if brackets:
                out.append(res)
            else:
                out += res
            return p_helper(tokens[find_paren(tokens)+1:],out,brackets)
        if tokens[0] == ')':
            raise SnekSyntaxError
        if len(tokens) < 2:
            if brackets:
                return out+[number_or_symbol(tokens[0])]
            if out != []:
                raise SnekSyntaxError
            return number_or_symbol(tokens[0])
        return p_helper(tokens[1:],out + [number_or_symbol(tokens[0])],brackets)

    return p_helper(tokens,[],False)





######################
# Built-in Functions #
######################

snek_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
}

##############
# Evaluation #
##############

def evaluate(tree):
    """
    Evaluate the given syntax tree according to the rules of the Snek
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    raise NotImplementedError

if __name__ == "__main__":
    # doctest.testmod()
    #t = ['(', 'a', '(', 'b', '(', 'c', ')', '(', 'd', 'e', ')', '(', '(', '(', '(', 'f', ')', ')', ')', ')', ')', ')']
    #t = ['(', 'define', 'circle-area', '(', 'lambda', '(', 'r', ')', '(', '*', '3.14', '(', '*', 'r', 'r', ')', ')', ')', ')']
    #t = ['x']
    #t = ['(', 'cat', '(', 'dog', '(', 'tomato' ,')' , ')', ')']
    #print('res',parse(t))
    pass

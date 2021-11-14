import doctest
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
    return new_source.split() #removes spaces and returns as list

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
            return i #return place of right paren
    raise SnekSyntaxError

def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    def p_helper(tokens,out,brackets):
        '''
        Given out and tokens, returns a parsed version of tokens and adds it to out
        Brackets determines whether to wrap returned result in parentheses
        '''
        #print('parse',tokens,out,brackets)
        if tokens == []: #base case
            return out
        if tokens[0] == '(': #if starts with paren, recursive call on expression
            res = p_helper(tokens[1:find_paren(tokens)],[],True)
            if brackets:
                out.append(res)
            else:
                out += res
            return p_helper(tokens[find_paren(tokens)+1:],out,brackets)
        if tokens[0] == ')': #unmatched parentheses
            raise SnekSyntaxError
        if len(tokens) < 2: #base case
            if brackets:
                return out+[number_or_symbol(tokens[0])]
            if out != []:
                raise SnekSyntaxError
            return number_or_symbol(tokens[0])
        if tokens[0] == 'define':
            #print('t',tokens)
            if len(tokens) < 3:
                raise SnekSyntaxError
            if tokens[2] == '(': #if defining to expression
                if find_paren(tokens[2:]) != len(tokens[2:])-1:
                    print('t',tokens[2:],find_paren(tokens[2:]))
                    raise SnekSyntaxError
            if not isinstance(number_or_symbol(tokens[1]),str):
                raise SnekSyntaxError
        return p_helper(tokens[1:],out + [number_or_symbol(tokens[0])],brackets)

    return p_helper(tokens,[],False)

snek_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": lambda args: args[0] if len(args) == 1 else (args[0]*snek_builtins["*"](args[1:])),
    "/": lambda args: args[0] if len(args) == 1 else (args[0]/(snek_builtins["*"](args[1:]))),
}

class Environment:
    def __init__(self,dict,parent = None):
        self.att = {}
        if dict != None:
            for key in dict:
                self.att[key] = snek_builtins[key]
        if parent == None:
            self.parent = Environment(snek_builtins, -1)

    def define(self,key,value):
        self.att[key] = value

def evaluate(tree, env = Environment({})):
    """
    Evaluate the given syntax tree according to the rules of the Snek
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
        env: a optional pointer to an environment
    """
    print('evaluating',tree,env.att)
    if isinstance(tree,list): #if tree is a list
        if tree[0] == 'define': #special define case
            val = evaluate(tree[2], env)
            env.define(tree[1],val)
            return val
        else:
            for i,el in enumerate(tree): #evaluate every el in list
                tree[i] = evaluate(el, env)
            if callable(tree[0]):
                return tree[0](tree[1:])
        raise SnekEvaluationError
    if tree in snek_builtins: #if tree is an op
        return snek_builtins[tree]
    if isinstance(tree,(int,float)): #if tree is a number
        return tree
    if tree in env.att:#if tree is a str (var name)
        return env.att[tree]
    print('hm',tree,env.att)
    raise SnekEvaluationError

def result_and_env(tree, env = Environment({})):
    '''
    Returns a tuple with 2 elements: the result of the evaluation and the environment (even if no env passed)
    '''
    print('result and env',tree,env.att)
    return (evaluate(tree,env),env)

def repl():
    quit = False
    while not quit:
        i = input('in:')
        if i == 'QUIT':
            quit = True
        else:
            t = tokenize(i)
            #print('token',t)
            p = parse(t)
            #print('parse',p)
            eval = evaluate(p)
            print('out>',eval)

if __name__ == "__main__":
    '''s = '(define x (+ 2 3))'
    t = tokenize(s)
    print(t)
    print(parse(t))'''
    repl()

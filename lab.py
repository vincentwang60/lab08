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
            if len(tokens) < 3:
                raise SnekSyntaxError
            if tokens[2] == '(': #if defining to expression
                if find_paren(tokens[2:]) != len(tokens[2:])-1:
                    #print('t',tokens[2:],find_paren(tokens[2:]))
                    raise SnekSyntaxError
            if not isinstance(number_or_symbol(tokens[1]),str):
                raise SnekSyntaxError
        if tokens[0] == 'lambda':
            print('testing',tokens)
            if len(tokens) < 3:
                raise SnekSyntaxError
            if tokens[1] != '(':  #check if list of params
                raise SnekSyntaxError
            left = find_paren(tokens[1:]) #end of params paren
            #print('paren from 1 to', 1+left)
            for i in range(2,1+left):
                if not isinstance(number_or_symbol(tokens[i]),str):
                     raise SnekSyntaxError
            right = find_paren(tokens[left+2:])
            #print('paren from ',2+left,'to',right+left+2)
            if right + left + 3 != len(tokens):
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
        else:
            self.parent = parent

    def define(self,key,value):
        self.att[key] = value

    def get_keys(self):
        out = set(self.att.keys())
        if self.parent == None or self.parent == -1:
            return out
        res = self.parent.get_keys()
        for r in res:
            out.add(r)
        return out

    def get(self,key):
        if key in self.att:
            return self.att[key]
        if self.parent != -1:
            return self.parent.get(key)
        raise KeyError

class Function:
    def __init__(self,param,body,env = Environment({})):
        self.params = param
        self.body = body
        self.env = env
    '''
    def __str__(self):
        return '\nFUNC\nparams:'+str(self.params)+'\nbody:'+str(self.body)+'\nenv!!'+str(self.env.att)
    '''

def evaluate(tree, env = Environment({})):
    """
    Evaluate the given syntax tree according to the rules of the Snek
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
        env: a optional pointer to an environment
    """
    #print('evaluating',tree,env.att)
    if isinstance(tree,list): #if tree is a list
        if tree[0] == 'define': #special define case
            print('defining',tree)
            if isinstance(tree[1],list):
                tree[2] = ['lambda',tree[1][1:],tree[2]]
                print('new tree2',tree[2])
                val = evaluate(tree[2], env)
                env.define(tree[1][0],val)
            else:
                val = evaluate(tree[2], env)
                env.define(tree[1],val)
            return val
        if tree[0] == 'lambda': #special lambda case
            return Function(tree[1],tree[2],env)
        if not isinstance((tree[0]),list):#check for user defined func
            #new function
            if tree[0] in env.get_keys(): #named function
                try:
                    func = env.get(tree[0])
                    funcEnv = Environment({},env)
                    for i,p in enumerate(func.params):
                        funcEnv.define(p,evaluate(tree[1:][i],func.env))
                    res = evaluate(func.body,funcEnv)
                    return res
                except AttributeError:
                    pass
        newTree = []
        for i,el in enumerate(tree): #evaluate every el in list
            res = evaluate(el,env)
            if isinstance(res,Function):
                tree[i] = res
                funcEnv = Environment({},res.env)
                for j,p in enumerate(tree[i].params):
                    funcEnv.define(p,evaluate(tree[1:][j],env))
                res2 = evaluate(tree[i].body,funcEnv)
                return res2
            newTree.append(res)
        if callable(newTree[0]) or isinstance(newTree[0],Function):
            return newTree[0](newTree[1:])
        raise SnekEvaluationError
    if tree in snek_builtins: #if tree is an op
        return snek_builtins[tree]
    if isinstance(tree,(int,float)): #if tree is a number
        return tree
    if tree in env.get_keys():#if tree is a str (var name)
        return env.get(tree)
    print('t',tree,env.get_keys())
    raise SnekNameError

def result_and_env(tree, env = Environment({})):
    '''
    Returns a tuple with 2 elements: the result of the evaluation and the environment (even if no env passed)
    '''
    return (evaluate(tree,env),env)

def repl():
    gEnv = Environment({})
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
            eval = evaluate(p,gEnv)
            print('out>',eval)

if __name__ == "__main__":
    repl()

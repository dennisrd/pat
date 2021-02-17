# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 17:01:14 2021

@author: Dennis Dams (dennis.dams@tno.nl)

"""


import unittest


class Param:
    """A named, typed parameter, to be used in match patterns"""
    name: str
    typ: type

    def __init__(self, **name_type):
        """Constructor expects 1 keyword argument, e.g. 'x=int'"""
        if len(name_type.items()) > 1:
            raise RuntimeError("multiple arguments to Param")
        varname, vartype = next(iter(name_type.items()))
        self.name = varname
        self.typ = vartype

    def __str__(self):
        return 'Var(' + self.name + '=' + str(self.typ) + ')'

    def __repr__(self):
        return 'Var(' + self.name + '=' + str(self.typ) + ')'


class Pattern:
    """A pattern is a Python value with parameters that stand for sub-values.

    Allowed values are built from dict and list constructors,
    where the dict keys must be strings and the non-compound
    values must be strings, numbers, booleans, or parameters of
    one of these types."""
    def __init__(self, val):
        # TODO check val
        self.pattern = val
    
    # TODO print Params
    def __str__(self):
        return 'Pattern(' + str(self.pattern) + ')'
    
    def subst(self, **bindings):
        return Pattern(subst_any(self.pattern, bindings))
    
    def match(self, ground_val):
        return match_any(self.pattern, ground_val)


def subst_any(term, bindings):
    '''Dispatch according to type.'''
    if isinstance(term, Param):
        return subst_param(term, bindings)
    elif isinstance(term, dict):
        return subst_dict(term, bindings)
    elif isinstance(term, list):
        return subst_list(term, bindings)
    else:
        # substitution not implemented for values of other types
        return term


def subst_param(var, bindings):
    for k, val in bindings.items():
        if var.name == k:
            if var.typ == type(val):
                return val
            else:
                #print("type mismatch")
                return var
            break
    # no binding for var
    return var


def subst_dict(d: dict, bindings):
    #print(bindings)
    result = {}
    for k, v in d.items():
        result[k] = subst_any(v, bindings)
    return result


def subst_list(l: list, bindings):
    return [subst_any(el, bindings) for el in l]


def match_any(term, ground_val):
    """Dispatch according to type."""
    if isinstance(term, Param):
        return match_param(term, ground_val)
    elif ((isinstance(term, int) and isinstance(ground_val, int))
          or
          (isinstance(term, str) and isinstance(ground_val, str))
         ):
        if term == ground_val:
            return {}
        else:
            return None
    elif isinstance(term, dict) and isinstance(ground_val, dict):
        return match_dict(term, ground_val)
    elif isinstance(term, list) and isinstance(ground_val, list):
        return match_list(term, ground_val)
    else:
        return None


def match_param(var, ground_val):
    if var.typ == type(ground_val):  #isinstance(ground_val, var.typ):
        return { var.name : ground_val }
    else:
        return None


def match_dict(term: dict, ground_val: dict):
    bindings = {}
    for k in term.keys():
        # ground_val must at least have all keys that term has
        if not k in ground_val:
            return None
        # if key is both in term and in ground_val, try to match the
        # associated values
        sub_bindings = match_any(term[k], ground_val[k])
        if sub_bindings is None:
            return None
        else:
            bindings.update(sub_bindings)
    return bindings


def match_list(l: list, ground_val: list):
    bindings = {}
    if len(l) != len(ground_val):
        return None
    for l_el, ground_val_el in zip(l, ground_val):
        sub_bindings = match_any(l_el, ground_val_el)
        if sub_bindings is None:
            return None
        else:
            bindings.update(sub_bindings)
    return bindings


class TestPattern(unittest.TestCase):

    @unittest.expectedFailure
    def test0(self):
        Param(x=int, y=str)

    def test1(self):
        e = Pattern({'kind': 'Command',
                     'method': 'Inc',
                     'arg': Param(i=int)
                     }
                    )
        # Pattern(kind='Command', method='Inc', ...)
        # Inc(int i [in]) Inc(i=in(int))
        e_subst = e.subst(i=43)
        e_subst_expected = Pattern({'kind': 'Command',
                                    'method': 'Inc',
                                    'arg': 43})
        #self.assertDictEqual(e_subst, e_subst_expected)
        self.assertEqual(e_subst.pattern['kind'], e_subst_expected.pattern['kind'])
        self.assertEqual(e_subst.pattern['method'], e_subst_expected.pattern['method'])
        self.assertEqual(e_subst.pattern['arg'], e_subst_expected.pattern['arg'])

    def test2(self):
        #print(Pattern([Param(x=int)]).subst(x=0))
        s = Pattern(Param(x=int))
        s_match = s.match(3)
        self.assertEqual(s_match['x'], 3)

    def test3(self):
        d = Pattern({'aap': Param(y=int)})
        d_match = d.match({'aap': 4})
        self.assertEqual(d_match['y'], 4)
        d_match = d.match({'aap': 4, 'noot': 'mies'})
        self.assertEqual(d_match['y'], 4)
        d_match = d.match({})
        self.assertEqual(d_match, None)
        d_match = d.match({'aap': Param(z=int)})
        self.assertEqual(d_match, None)

    def test4(self):
        d = Pattern({'aap': Param(y=int), 'noot': Param(s=str)})
        d_match = d.match({'aap': 4})
        self.assertEqual(d_match, None)
        d_match = d.match({'aap': 4, 'noot': 'mies'})
        self.assertEqual(len(d_match), 2)
        self.assertEqual(d_match['y'], 4)
        self.assertEqual(d_match['s'], 'mies')
        d_match = d.match({'aap': Param(z=int)})
        self.assertEqual(d_match, None)

    def test5(self):
        d = Pattern([Param(y=int), Param(s=str), 6])
        d_match = d.match([5, 'foo', 6])
        self.assertEqual(len(d_match), 2)
        self.assertEqual(d_match['y'], 5)
        self.assertEqual(d_match['s'], 'foo')
        d_match = d.match([5])
        self.assertEqual(d_match, None)

    def test6(self):
        d = Pattern([7])
        d_match = d.match([7])
        self.assertEqual(d_match, {})
        d_match = d.match([5])
        self.assertEqual(d_match, None)

    def test7(self):
        d = Pattern(['bar'])
        d_match = d.match([7])
        self.assertEqual(d_match, None)
        d_match = d.match(['bar'])
        self.assertEqual(d_match, {})


if __name__ == '__main__':
    unittest.main()

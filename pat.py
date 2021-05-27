import unittest


class Var:
    """A placeholder for a value of the specified type."""

    def __init__(self, typ=object):
        self.typ = typ

    # Making it a descriptor does not work, since it is not a class attribute.
    # def __get__(self, instance, owner):
    #     print(f'__get__({self}, {instance}, {owner})')
    #     bindings = instance.var_bindings
    #     if self in bindings:
    #         return bindings[self]
    #     return self

    def __repr__(self):
        return f'{self.__class__}({self.typ})'

    def __str__(self):
        return f'{self.__class__.__name__}({self.typ.__name__})'
        #return f'{self.__class__}({self.typ})'

    def __gt__(self, other):
        return BinaryExpr('>', self, other)

    def __eq__(self, other):
        return BinaryExpr('==', self, other)

    # https://docs.python.org/3/reference/datamodel.html#object.__hash__
    def __hash__(self):
        return id(self)

    def subst(self, bindings):
        if self in bindings and isinstance(bindings[self], self.typ):
            return bindings[self]
        return self  # no binding for var, or type mismatch

    def match(self, ground_val, current_bindings):
        if not isinstance(ground_val, self.typ):
            raise MatchException
        if self not in current_bindings:
            current_bindings[self] = ground_val
        elif current_bindings[self] == ground_val:
            return
        else:
            raise MatchException


class BinaryExpr:
    """Binary expression"""
    operator: str
    left: object
    right: object

    def __init__(self, op, left, right):
        self.operator = op
        self.left = left
        self.right = right

    def __and__(self, other):
        return BinaryExpr('&', self, other)



class MatchException(Exception):
    pass


class MatchDict(dict):
    """Override bool() to also return True for empty dict."""
    def __bool__(self):
        return True


class Pattern:
    """A pattern is a Python value with variables that stand for sub-values.

    Allowed values are built from dict and list constructors,
    where the dict keys must be strings and the non-compound
    values must be strings, numbers, booleans, or variables of
    one of these types."""

    val: object

    def __init__(self, val):
        # TODO check val
        self.val = val

    # TODO print Vars
    def __str__(self):
        return 'Pattern(' + str(self.val) + ')'

    def __repr__(self):
        return 'Pattern(' + str(self.val) + ')'

    def subst(self, bindings):
        #return Pattern.subst_any(self.val, bindings)
        return self.subst_any(self.val, bindings)  # or: self.__class__

    def match(self, ground_val):
        bindings = {}
        try:
            self.match_any(self.val, ground_val, bindings)
            return MatchDict(bindings)
        except MatchException:
            return None

    #@staticmethod
    @classmethod
    def subst_any(cls, term, bindings):
        """Dispatch according to type."""
        if isinstance(term, Var):
            return term.subst(bindings)
        elif isinstance(term, dict):
            return cls.subst_dict(term, bindings)
        elif isinstance(term, list):
            return cls.subst_list(term, bindings)
        else:
            return term  # substitution not implemented for values of other types

    @classmethod
    #allow Var in key?
    def subst_dict(cls, d: dict, bindings):
        result = {}
        for k, v in d.items():
            result[k] = cls.subst_any(v, bindings)
        return result

    @classmethod
    def subst_list(cls, lst: list, bindings):
        return [cls.subst_any(el, bindings) for el in lst]

    @staticmethod
    def match_any(term, ground_val, bindings):
        """Match base values, or dispatch according to container type."""
        if ((isinstance(term, int) and isinstance(ground_val, int))
            or
            (isinstance(term, str) and isinstance(ground_val, str))):
            if term == ground_val:
                return
            else:
                raise MatchException
        elif isinstance(term, Var):
            term.match(ground_val, bindings)
        elif isinstance(term, dict) and isinstance(ground_val, dict):
            Pattern.match_dict(term, ground_val, bindings)
        elif isinstance(term, list) and isinstance(ground_val, list):
            Pattern.match_list(term, ground_val, bindings)
        else:
            raise MatchException

    @staticmethod
    def match_dict(term: dict, ground_val: dict, bindings):
        for k in term.keys():
            # ground_val must at least have all keys that term has
            if k not in ground_val:
                raise MatchException
            # if key is both in term and in ground_val, try to match the
            # associated values
            Pattern.match_any(term[k], ground_val[k], bindings)

    @staticmethod
    def match_list(lst: list, ground_val: list, bindings):
        if len(lst) != len(ground_val):
            raise MatchException
        for l_el, ground_val_el in zip(lst, ground_val):
            Pattern.match_any(l_el, ground_val_el, bindings)


class TestPattern(unittest.TestCase):

    def test_Var(self):
        i = Var(int)
        x = Var()

    def test_pattern_subst(self):
        v = Var(int)
        e = Pattern(v)
        e_subst = e.subst({v: 3})
        self.assertEqual(e_subst, 3)

    def test_Var_subst(self):
        i = Var(int)
        i_subst = i.subst({i: 3})
        self.assertEqual(i_subst, 3)

    # @unittest.expectedFailure
    def test_Var_subst_type_mismatch(self):
        i = Var(int)
        i_subst = i.subst({i: 'a'})
        self.assertEqual(i_subst, i)

    def test_pattern_list_subst(self):
        i = Var(int)
        e = Pattern([i])
        e_subst = e.subst({i: 42})
        self.assertEqual(e_subst, [42])

    def test_match_string(self):
        match_result = Pattern('foo').match('foo')
        self.assertEqual(match_result, {})

    def test_match_string_fail(self):
        match_result = Pattern('foo').match(Pattern('bar'))
        self.assertEqual(match_result, None)

    def test_match_int(self):
        match_result = Pattern(7).match(7)
        self.assertEqual(match_result, {})

    def test_match_type_fail(self):
        match_result = Pattern(7).match('foo')
        self.assertEqual(match_result, None)

    # @unittest.skip
    def test_match_var(self):
        match_result = Pattern(v := Var(int)).match(97)
        # print(len(bindings))
        # print(bindings[v])
        # bindings == {v: 97}
        self.assertEqual(len(match_result), 1)
        self.assertEqual(match_result[v], 97)

    def test_match_pattern_double_var_succeed(self):
        x = Var(int)
        e = Pattern({'arg1': x, 'arg2': x})
        m = e.match({'arg1': 3, 'arg2': 3})
        self.assertEqual(bool(m), True)
        self.assertEqual(m[x], 3)

    def test_match_pattern_double_var_fail(self):
        x = Var(int)
        e = Pattern({'arg1': x, 'arg2': x})
        m = e.match({'arg1': 3, 'arg2': 4})
        self.assertEqual(bool(m), False)


if __name__ == '__main__':
    unittest.main()

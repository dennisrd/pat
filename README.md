# pat
Pattern matching for Python values.

A pattern is a value that may contain variables. Such a value stands for an arbitary sub-value. Example:
```python
>>> n = Var(int)
>>> pat = Pattern([1, 2, n])
>>> pat
Pattern([1, 2, Var(<class 'int'>)])
```
This defines a pattern that is a list in which the 3rd element may be any integer value. Note how the variable n is defined: it is an instance of class Var, instantiated with a type (```int``` here).

Pattern variables may be substituted by values:
```python
>>> pat.subst({n: 42})
[1, 2, 42]
```
Method ```subst``` takes a *binding*, which is a dict that maps Vars to values, and returns the value obtained by performing the substitution. The pattern itself is not altered, so ```pat``` can be used again to produce another value by substitution:
```python
>>> pat.subst({n: 3})
[1, 2, 3]
```
A pattern can also be used to *match* other values:
```python
>>> binding = pat.match([1, 2, 7])
>>> binding
{Var(<class 'int'>): 7}
```
Matching returns a binding. In this case, ```n``` is bound to the value 7.
```python
>>> binding[n]
7
>>> next(iter(binding)) is n  # check whether the first key in binding is the same object as n
True
```
The value that is returned by method ```match``` is either ```None```, when there is no match, or a binding. This binding is such that when used as a substitution on the pattern, the result is equal to the value to be matched. So if ```p``` is a pattern and ```p.match(v)``` returns binding ```b```, then it will be the case that ```p.subst(b)``` equals ```v```. That is, ```p.subst(p.match(v)) == v```, if ```p.match(v)``` is not ```None```.

If method ```match``` returns a dict (and not ```None```), its value is in fact an instance of class MatchDict, which inherits from the Python dict class, with one difference: the truth value of MatchDict value ```{}``` is True (and not False, as it would be for a value that is a direct instance of dict). This is so that we can use the result of a call to ```match``` as a condition in the natural way, even when the returned binding is empty:
```python
>>> ground_pattern = Pattern(['abc'])
>>> match = ground_pattern.match(['abc'])
>>> match
{}
>>> if match:
...     print('they match')
... else:
...     print('they do not match')
...
they match
```

Pattern values can be constructed from Vars, numbers, and strings using list and dict containers.
```python
>>> pat = Pattern({'command': 'SetTicks', 'args': (arglist := Var(list))})
>>> pat.match({'command': 'SetTicks', 'args': [2, 4, 8, 10]})[arglist]
[2, 4, 8, 10]
```
Note the use of the Python walrus operator (:=) to name the ```Var(list)``` so that it can be referenced afterwards.

A pattern may contain multiple Vars, and a substition does not need to bind all Vars.
```python
>>> x = Var(float); y = Var(float)
>>> p = Pattern({'x_coord': x, 'y_coord': y})
>>> p_x = p.subst({x: 3.14})
>>> p_x
{'x_coord': 3.14, 'y_coord': Var(<class 'float'>)}
```
Note that the result is not a Pattern, so in order to also substitute for ```y```, it needs to be wrapped in a Pattern constructor.
```python
>>> p_x.subst({y: 7.0})
AttributeError: 'dict' object has no attribute 'subst'
>>> Pattern(p_x).subst({y: 7.0})
{'x_coord': 3.14, 'y_coord': 7.0}
```

The same Var may occur multiple times in a Pattern.
```python
>>> s = Var(str)
>>> twice = Pattern([s, s])
>>> twice.subst({s: 'one'})
['one', 'one']
>>> bool(twice.match(['one', 'two']))
False
>>> twice.match(['one', 'one'])
{Var(<class 'str'>): 'one'}
```

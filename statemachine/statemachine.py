"""State machines with reflective features."""


from pat2 import Var
import types


class StateMachine:
    """State Machine, possibly with data variables (aka Extended State Machine).

    Specific types of state machines inherit from this class. A StateMachine
    has a structure, which represents the graph of locations and transitions
    between them. It is the state machine that specifies the source and
    target locations of transitions, not the individual transitions
    themselves. This way, the same transition can occur between different
    pairs of source/target locations. In other words, the locations and the
    transitions are defined independently from how they are "wired". For
    example, a transition that should be present as a self loop on all
    locations has to be defined only once, this way. Another example is an
    "error" transition that goes from every location to a designated error
    location. """
    def __init__(self):
        #print('__init__ of StateMachine')
        self.structure = Structure()

    def __setattr__(self, name, value):
        """Intercept setting of Location and Transition attributes: add name."""
        if isinstance(value, Location):
            #print(f'__setattr__({m}, {name}, ...) of Location')
            if value.name is not None:
                print(f'warning: renaming Location {value.name} to {name}')
            value.name = name
        if isinstance(value, Transition):
            #print(f'__setattr__({m}, {name}, ...) of Transition')
            if value.name is not None:
                print(f'warning: renaming Transition {value.name} to {name}')
            value.name = name
        # Other allowed attributes are:
        # - state
        # - structure
        # TODO disallow others?
        object.__setattr__(self, name, value)

    def locations(self, *location_names):
        for name in location_names:
            self.__setattr__(name, Location())

    def add_transition(self, trans, source, target):
        self.structure.add_transition(trans, source, target)

    def check(self):
        # TODO various checks:
        # - ...
        pass

    def activate(self):
        pass

    # TODO also check for adding attributes with dupl names


class Structure:
    """Graph structure of a StateMachine.

    Each state machine has a structure, which is the graph formed by
    locations (nodes) and transitions (edges). """
    def __init__(self):
        self.graph = []

    def add_transition(self, trans, source, target):
        bound_trans = {
            'transition': trans,
            'source': source,
            'target': target,
        }
        self.graph.append(bound_trans)


class Location:
    """A control location of a StateMachine.

    Elsewhere this is called a state. Here it is called location because the
    state of a StateMachine consists of not only the current location,
    but also the values of any data variables. """
    def __init__(self):
        self.name = None
        # name is set when Location instance is assigned to attribute of a
        # StateMachine instance

    def __repr__(self):
        if self.name is None:
            return f'{self.__class__}()'
        return f'{self.__class__}({self.name})'

    def __str__(self):
        if self.name is None:
            return f'{self.__class__.__name__}()'
        return f'{self.__class__.__name__}({self.name})'


class Transition:
    """A transition of a StateMachine.

    An instance has a trigger, a condition, an update function, and a
    response. These 4 attributes together form the "static code" of the
    transition that specify when it is enabled (trigger and condition) and
    how it reacts when it is executed (update and response). Because the same
    behavior may be present between other locations in a StateMachine,
    the same transition may occur multiple times. An instance will typically
    have additional attributes that represent the parameters that are used in
    the trigger and response patterns, and that may also occur in the
    condition and update. When the transition is executed, these parameters
    will become bound, e.g. by matching the trigger pattern to an incoming
    event. Any such bindings are stored in the instance attribute
    param_bindings, but only during the execution of the transition. After
    each execution of the transition, param_bindings is reset to the empty
    dictionary. Parameters must be instances of Var. The override of
    __getattribute__ makes sure that when a parameter is accessed, its bound
    value (if any) is returned. """
    def __init__(self, sm=None, name=None, source=None, target=None):
        """sm is the StateMachine to which this Transition is added; name is
        the name of this Transition. Note that source and target are not
        stored in the Transition; they go into the StateMachine Structure."""
        if sm is None and name is not None:
            print('error: Transition with name but no StateMachine')
        self.name = name
        self.trigger = None
        self.condition = None
        self.update = None
        self.response = None
        self.param_bindings = {}
        if sm is not None:
            if name is None:
                print('error: adding Transition without name on StateMachine')
            # do not use sm.__setattr__() to avoid setting name twice
            object.__setattr__(sm, name, self)
            if source is None or target is None:
                print('error: adding Transition without source or target on '
                      'StateMachine')
            sm.add_transition(self, source, target)

    def __repr__(self):
        return f'{self.__class__}({self.name})'

    def __str__(self):
        return f'{self.__class__.__name__}({self.name})'

    def __setattr__(self, name, new_value):
        if name == 'update':
            object.__setattr__(self, name,
                               types.MethodType(lambda x: new_value(), self)
                               )
            return
        try:
            existing_value = object.__getattribute__(self, name)
            if isinstance(existing_value, Var):
                if isinstance(new_value, existing_value.typ):
                    self.param_bindings[existing_value] = new_value
                else:
                    print('type error')
            else:
                # if the attribute exists and is not a Var, just set new value
                object.__setattr__(self, name, new_value)
        except AttributeError:
            if isinstance(new_value, Var):
                new_value.name = name
                # TODO also set fully qualified name (e.g. SM().start.i ?)
            object.__setattr__(self, name, new_value)

    def __getattribute__(self, item):
        attr_value = object.__getattribute__(self, item)
        if isinstance(attr_value, Var):
            #print(f'__getattribute__({m}, {attr_value}) of Var')
            if attr_value in self.param_bindings:
                return self.param_bindings[attr_value]
        return attr_value

    def __enter__(self):
        """Support use of Transition() in with statements with a target."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class State:
    """An instance of State represents a state vector of a StateMachine. Its
    attributes must be Vars. Any set or get of such an attribute is
    redirected via the current Var bindings of the State instance."""
    def __init__(self):
        self._bindings = {}

    def __setattr__(self, name, new_value):
        #print(f'__setattr__({m}, {name}, {new_value})')
        if name in ['_bindings', '__class__']:
            object.__setattr__(self, name, new_value)
            return
        try:
            existing_value = object.__getattribute__(self, name)
            # attribute already exists (must be Var); set new value in _bindings
            if not isinstance(existing_value, Var):
                print(f'internal error: attribute {name} of {self} is not Var')
            if isinstance(new_value, existing_value.typ):
                self._bindings[existing_value] = new_value
            else:
                print('type error')
        except AttributeError:
            # new attribute; set new value (must be Var) on self
            if not isinstance(new_value, Var):
                print('new state attribute must be assigned a Var')
            new_value.name = name  # store name in Var for convenience
            object.__setattr__(self, name, new_value)

    def __getattribute__(self, item):
        if item in ['_bindings', '__class__']:
            return object.__getattribute__(self, item)
        # if item exists, it must be a Var
        attr_value = object.__getattribute__(self, item)
        if not isinstance(attr_value, Var):
            print(f'internal error: attribute {item} of {self} is not Var')
        if attr_value in self._bindings:
            # if bound, return bound value
            return self._bindings[attr_value]
        else:
            # if not bound, return the Var
            return attr_value

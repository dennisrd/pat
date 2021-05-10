"""State machines with reflective features."""


from pat2 import Var, Pattern
import types
from functools import partial
from inspect import signature


class State:
    pass


class EFSM:
    """Extended Finite State Machines.

    Specific types of state machines inherit from this class. An EFSM has a
    structure, which represents the graph of locations and transitions
    between them. It is the state machine that specifies the source and
    target locations of transitions, not the individual transitions
    themselves. This way, the same transition can occur between different
    pairs of source/target locations. In other words, the locations and the
    transitions are defined independently from how they are "wired". For
    example, a transition that should be present as a self loop on all
    locations has to be defined only once, this way. Another example is an
    "error" transition that goes from every location to a designated error
    location. """
    # Operations that are common to all the different types (subclasses) of
    # EFSMs go here.
    # These may be classmethods or normal (instance) methods.
    # (Note that operations that are used during the definition of subclasses
    # and that need to access such a subclass cannot be put here because such
    # a subclass does not exist while it's being defined. So operations on
    # the structure cannot be put here, because the structure is a class
    # attribute of the subclass.)
    #
    # For example, checks on well-formedness of the state machine structure
    # go here, such as checking that there are no unreachable locations.
    # There may also be more semantic checks, like for race conditions.

    def __init__(self):
        """An instance of an EFSM must have a state, which consists of at
        least the current location. Furthermore there may be zero or more data
        variables, defined in the subclass of EFSM that represents the
        particular type state machine."""
        self.state = State()
        self.state.loc = None

        # The update method of every transition (if any) of an EFSM requires
        # a single argument (besides its "self") that must be the EFSM. When
        # defining the transition as a class attribute of the subclass of
        # EFSM, this instance wasn't known yet, but now that it is,
        # the update method can be replaced with its partially evaluated
        # version so that the efsm argument does not need to be provided
        # anymore.
        attrs = vars(self.__class__)
        for attr in attrs:
            t = attrs[attr]
            if isinstance(t, Transition):
                # TODO check that attr has update
                # Figure out name of efsm parameter of update
                sig = signature(t.update.__func__)
                second_parameter = list(sig.parameters.items())[1]
                second_parameter_name = second_parameter[0]
                kwarg = {second_parameter_name: self}
                new_update = partial(t.update.__func__, **kwarg)
                t.update = types.MethodType(new_update, t)


class Location:
    """Locations of EFSMs."""
    def __set_name__(self, owner, name):
        """Override special method __set_name__ so that the name of the
        variable that a new Location is assigned to, is stored inside the
        Location."""
        self.name = name

    def __repr__(self):
        return f'{self.__class__}({self.name})'

    def __str__(self):
        return f'{self.__class__.__name__}({self.name})'


class Transition:
    """Transitions of EFSMs.

    An instance of this class represents a transition in an EFSM. Such an
    instance has a trigger, a condition, an update function, and a response.
    These 4 attributes together form the "static code" of the transition that
    specify when it is enabled (trigger and condition) and how it reacts when it
    is executed (update and response). Because the same behavior may be present
    between other locations in a state machine, the same transition may occur
    multiple times.
    An instance of Transition will typically have additional attributes that
    represent the parameters that are used in the trigger and response
    patterns, and that may also occur in the condition and update. When the
    transition is executed, these parameters will become bound, e.g. by
    matching the trigger pattern to an incoming event. Any such bindings are
    stored in the instance attribute param_bindings, but only during the
    execution of the transition. After each execution of the transition,
    param_bindings is reset to the empty dictionary.
    Parameters must be instances of Var. The override of __getattribute__ makes
    sure that when a parameter is accessed, its bound value (if any) is
    returned."""
    def __init__(self):
        self.name = None
        self.trigger = None
        self.condition = None
        self.update = None
        self.response = None
        self.param_bindings = {}

    def __set_name__(self, owner, name):
        """Override special method __set_name__ so that the name of the
        variable that a new Transition is assigned to, is stored inside the
        Transition."""
        self.name = name

    def __repr__(self):
        return f'{self.__class__}({self.name})'

    def __str__(self):
        return f'{self.__class__.__name__}({self.name})'

    def __getattribute__(self, item):
        """Intercept access to Var attributes: check whether they are bound."""
        # use base class method to avoid infinite recursion
        attr_value = object.__getattribute__(self, item)
        if isinstance(attr_value, Var):
            #print(f'__getattribute__({self}, {attr_value}) of Var')
            if attr_value in self.param_bindings:
                return self.param_bindings[attr_value]
        return attr_value

    def make(self, trigger, condition, update_function, response):
        """Convenience method to provide the main attributes.

        The provided update_function has 2 formal parameters. The first is an
        instance of Transition which must be this transition (i.e. self)
        because the function needs to access its input and output parameters.
        The second is the state machine to which this transition belongs,
        because it needs access to the machine's data variables. This
        function is set as the update method of the transition."""
        self.trigger = trigger
        self.condition = condition
        self.update = types.MethodType(update_function, self)
        self.response = response


class Structure:
    """Each state machine has a structure, which is the graph formed by
    locations (nodes) and transitions (edges)."""
    def __init__(self):
        self.graph = []

    def add_transition(self, trans, source, target):
        bound_trans = {
            'transition': trans,
            'source': source,
            'target': target,
        }
        self.graph.append(bound_trans)

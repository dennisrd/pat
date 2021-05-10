"""Example of a type of state machine.

An extended state machine (EFSM) can be seen as a piece of code in a specific
form. Snippets of code are attached to the edges of a graph. Such an edge
with code attached is called a transition. The nodes of the graph are the
control locations.

Just like the same piece of code may be executed by multiple processes or
threads at the same time, there may be multiple active instances of a single
EFSM. For this reason, an EFSM is modeled as a class. Each instance of the
class then represents a running state machine.

A class representing a state machine is also called a "type of state machine".
For example, the class Camera below represents a state machine that describes
the behavior of a particular type of camera. Besides cameras, there may be
other types of state machines, each corresponding to e.g. a functional
component of a system.

An instance of Camera represents an active behavior that follows the code of
class Camera. Such an instance may represent one of multiple cameras of the
same make and model.

All state machine classes derive from class EFSM, which provides common
behavior.

The definition of a state machine, i.e. of a subclass of EFSM, looks a lot
like a script that lists a sequence of instructions to build the state
machine's structure. It starts by creating an empty Structure.

Next, the locations of the state machine are defined. The locations do not
need to be added to the structure at this point - this will happen when
adding the Transitions.

Then, the transitions are defined, and each transition is added to the state
machine's structure, possibly between multiple pairs of locations.

Each location and each transition is represented as a separate class
attribute of Camera. Note that the name ("variable") of the attribute is
stored inside the Location/Transition (see the override of __set_name__ in
the class definitions of Location and Transition).

The name "update" is used as an auxiliary attribute that is deleted from the
dictionary of class attributes at the end of the class definition. (This could
be avoided if Python allowed more expressive lambdas.)

As said before, an instance of this class represents an instance of a camera.
All such instances share the same structure, i.e. the set of locations and
the transitions between locations. What varies per instance is the state
vector, which consists of the current values of the location and of the data
variables. Therefore the state vector is an instance attribute."""


from pat2 import Var
from statemachine import EFSM, Structure, Location, Transition


class Camera(EFSM):
    """A class of state machines modeling a type of Camera.

    (Incomplete - to be continued.)
    """

    # The structure is the same for all instances of Camera, so it is a class
    # attribute.
    # TODO can structure be hidden? make descriptor?
    structure = Structure()

    # The locations are the same for all instances of Camera, so they are
    # class attributes.
    # TODO add to structure?
    off = Location()
    on = Location()

    def __init__(self):
        """Definition of the state vector, which consists of a location
        and a number of data variables. Initialize the state vector for an
        instance of Camera."""
        super().__init__()
        self.state.loc = self.off
        self.state.task_counter = 0

    # Each transition is a class attribute of the state machine. Such a
    # transition has access to the data variables of an instance of
    # the state machine, which may be read and updated in the transition's
    # update method. Note that setting the attributes of the transition,
    # such as t.trigger, does not lead to the addition of attributes to the
    # class Camera.

    # Transition set_task_counter gets an integer value from the trigger,
    # and sets data variable task_counter to this value.
    set_task_counter = Transition()
    set_task_counter.i = Var(int)  # parameter
    #set_task_counter.params(
    #    i=Var(int)
    #)

    # Function that updates the data of the state machine,
    # and computes any output parameters to be used in the response events of
    # the transition.
    # The arguments passed to this function will be the transition (so that
    # the function can access its input and output parameters) and the state
    # machine (so that the function can access its data variables). This
    # function will be set as the update method on the transition, so its
    # first formal parameter could have been called 'self';
    # we use set_task_counter to stress that it will be the same transition
    # that is being defined in the surrounding code. Also, this is not a
    # method of Camera.
    def update(set_task_counter, efsm):
        print('this is the update() of set_task_counter')
        print(f'setting camera.state.task_counter to {set_task_counter.i + 1}')
        efsm.state.task_counter = set_task_counter.i + 1  # add 1 just for fun

    set_task_counter.make(
        trigger={'command': 'Set', 'arg': set_task_counter.i},
        condition=True,
        update_function=update,
        response=[{'reply': None}]
    )
    # Add the transition set_task_counter as a self-loop on both locations.
    structure.add_transition(set_task_counter, off, off)
    structure.add_transition(set_task_counter, on, on)

    # Transition t2 is to check that the function name 'update' can be reused
    # without causing confusion.
    t2 = Transition()
    def update(t2, efsm):
        print('this is the update() of t2')
    t2.make(
        trigger=None,
        condition=True,
        update_function=update,
        response=[]
    )
    # "Wire" transition t2 from Location off to Location on.
    structure.add_transition(t2, off, on)

    # Avoid that function update becomes a class attribute.
    del update


# Create an instance of Camera and do a few things with it. Normally,
# this code goes into another file, so that the definition of Camera can be
# run independently, in order to check whether that definition is ok (
# well-formed, etc.) before using it.
c = Camera()

# Set a binding manually; normally this would be the result of e.g. a match.
c.set_task_counter.param_bindings[c.set_task_counter.i] = 70

# Test the update function.
print()
print('executing c.set_task_counter.update():')
c.set_task_counter.update()
print(c.state.task_counter)

# Check that transition t2 has indeed another update function than
# transition set_task_counter.
print()
print('executing c.t2.update():')
c.t2.update()

print()
print('Camera.structure.graph:')
print(Camera.structure.graph)

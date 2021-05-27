from pat2 import Var
from statemachine import StateMachine, State, Location, Transition


class TaskControl(StateMachine):
    """State machine TaskControl models the Start and Stop commands that a
    client issues to a TaskControl server."""
    def __init__(m):
        super().__init__()

        # locations
        m.locations('on', 'off')

        # state vector: location and data variables
        m.state = State()
        m.state.loc = Var(Location)
        m.state.task_id = Var(int)

        # transitions
        with Transition(m, 'start', m.off, m.on) as t:
            t.i = Var(int)
            t.trigger = {'command': 'Start', 'arg': t.i}
            t.condition = True
            def update():
                m.state.task_id = t.i
                ReadyCompleted(m.state.task_id).activate()
            t.update = update
            t.response = [{'reply': None}]
        with Transition(m, 'stop', m.on, m.off) as t:
            t.i = Var(int)
            t.trigger = {'command': 'Stop', 'arg': t.i}
            t.condition = (t.i == m.state.task_id)
            def update():
                m.state.task_id = None
            t.update = update
            t.response = [{'reply': None}]

        # initialize the state vector
        m.state.loc = m.off
        m.task_id = None


class ReadyCompleted(StateMachine):
    """State machine ReadyComplete models the Ready and Complete
    notifications from a single task with a given task_id."""
    def __init__(m, task_id):
        super().__init__()

        # locations
        m.waiting = Location()
        m.ready = Location()
        m.completed = Location()

        # initialize state vector: location
        m.state = State()
        m.state.loc = m.waiting

        # transitions
        with Transition(m, 'notify_ready', m.waiting, m.ready) as t:
            t.trigger = None
            t.condition = True
            t.update = None
            t.response = [{'notification': 'Ready', 'arg': task_id}]
        with Transition(m, 'notify_completed', m.ready, m.completed) as t:
            t.trigger = None
            t.condition = True
            t.update = None
            t.response = [{'notification': 'Completed', 'arg': task_id}]


# Try it out.
tc = TaskControl()  # check that the definition is ok
tc.activate()  # doesn't do anything yet

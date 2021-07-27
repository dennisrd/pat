from pat2 import Var
from statemachine import StateMachine, State, Location, Transition


class Acc(StateMachine):
    # We define a class of state machines. Each instance is a running state
    # machine that represents a single account. As is common in Python,
    # the __init__ method defines how to instantiate such a state machine,
    # given arguments for the account id and its initial balance.
    def __init__(m, x, init_balance):
        super().__init__()  # Acc is derived from StateMachine, which needs
        # to be init-ed as well.

        # locations
        m.locations('A1')  # attribute notation m.A1 can now be used

        # state vector: location and data variables
        m.state = State()
        m.state.loc = Var(Location)
        m.state.total = Var(int)

        # transitions
        with Transition(m, 'add_money', m.A1, m.A1) as t:
            # Vars to be used as parameter in trigger expression
            t.y = Var(str)
            t.a = Var(int)
            # trigger expression must currently be built from dict and list
            # constructors, but this can easily be generalized to more type
            # constructors such as tuples
            t.trigger = {'name': 'transfer', 'arg1': t.y, 'arg2': t.a}
            t.condition = (t.y == x) & (m.state.total < 100)
            def update():
                m.state.total += t.a
                //ReadyCompleted(m.state.task_id).activate()
            t.update = update  # wish Python had general lambdas
            t.response = []  # no response event
        with Transition(m, 'reset', m.A1, m.A1) as t:
            t.trigger = {'command': 'reconcile'}
            t.condition = True
            def update():
                m.state.total = 0
            t.update = update
            t.response = []

        # initialize the state vector
        m.state.loc = m.A1
        m.total = 0


class KickOff(StateMachine):  # instead of main, be more Pythonic (see below)
    def __init__(m):
        super().__init__()

        # locations
        m.M1 = Location()  # demonstrating an alternative way to declare a loc

        # state vector: location and data variable
        # (demonstrate that they may also be initialized here instead of after
        # defining the transitions)
        m.state = State()
        m.state.loc = m.M1
        m.state.active_accounts = set()  # init to empty set

        # transitions
        with Transition(m, 'transfer_new_account', m.M1, m.M1) as t:
            t.y = Var(str)
            t.a = Var(int)
            t.trigger = {'name': 'transfer', 'arg1': t.y, 'arg2': t.a}
            t.condition = (t.y not in m.state.active_accounts)  # needs work...
            def update():
                m.state.active_accounts.add(t.y)
                Acc(t.y, t.a).activate()
            t.update = update
            t.response = []


# Try it out.
main = KickOff()  # instead of a main, we can just say where to start
main.activate()  # doesn't do anything yet

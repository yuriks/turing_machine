from itertools import izip

class Tape(object):
    def __init__(self):
        self.cur_pos = 0
        self.data = {}

    def read(self):
        return self.data.get(self.cur_pos, '@')

    def writeAndMove(self, new_char, direction):
        self.data[self.cur_pos] = new_char
        self.cur_pos += direction

    def moveTo(self, pos):
        self.cur_pos = pos

class State(object):
    def __init__(self, is_accepting=False):
        self.transitions = {}
        self.is_accepting = is_accepting

    def getActions(self, inputs):
        return self.transitions.get(inputs, (None, None, 0))

    def addTransition(self, conditions, actions):
        self.transitions[conditions] = actions

    def isFinal(self):
        return len(self.transitions) == 0

    def isAccepting(self):
        return self.is_accepting

class TuringMachine(object):
    def __init__(self, init_state, num_tapes=1):
        self.states = {None: State(is_accepting=False)}
        self.current_state = init_state

        self.tapes = [Tape() for i in xrange(num_tapes)]

    def addState(self, name, is_accepting=False):
        if name in self.states:
            raise KeyError
        self.states[name] = State(is_accepting)

    def addTransition(self, condition, actions):
        state = condition[0]
        self.states[state].addTransition(condition[1:], actions)

    def setTape(self, string):
        tape = self.tapes[0]
        for c in string:
            tape.writeAndMove(c, 1)
        tape.moveTo(0)

    def hasFinished(self):
        return self.states[self.current_state].isFinal()

    def hasAccepted(self):
        return self.hasFinished() and self.states[self.current_state].isAccepting()

    def step(self):
        if self.hasFinished():
            return

        input_tuple = tuple(tape.read() for tape in self.tapes)
        actions = self.states[self.current_state].getActions(input_tuple)

        num_actions = (len(actions) - 1) / 2

        self.current_state = actions[0]
        write_chars = actions[1:num_actions+1]
        head_moves = actions[num_actions+1:]
        for tape, char, move in izip(self.tapes, write_chars, head_moves):
            if char is None:
                char = tape.read()
            tape.writeAndMove(char, move)

    # Warning: May never stop!
    def run(self):
        while not self.hasFinished():
            self.step()
        return self.hasAccepted()

def main():
    #Maquina de turing que aceita se tiver o mesmo numero de
    #0 e 1
    tm = TuringMachine('q0')

    tm.addState('q0')
    tm.addState('q1')
    tm.addState('q2')
    tm.addState('q3')
    tm.addState('qaceita', is_accepting=True)

    tm.addTransition(('q0', 'x'), ('q0', '@', 1))
    tm.addTransition(('q0', '0'), ('q1', '@', 1))
    tm.addTransition(('q0', '1'), ('q3', '@', 1))
    tm.addTransition(('q0', '@'), ('qaceita', '@', 0))

    tm.addTransition(('q1', 'x'), ('q1', 'x', 1))
    tm.addTransition(('q1', '0'), ('q1', '0', 1))
    tm.addTransition(('q1', '1'), ('q2', 'x', -1))

    tm.addTransition(('q2', '0'), ('q2', '0', -1))
    tm.addTransition(('q2', '1'), ('q2', '1', -1))
    tm.addTransition(('q2', 'x'), ('q2', 'x', -1))
    tm.addTransition(('q2', '@'), ('q0', '@', 1))

    tm.addTransition(('q3', 'x'), ('q3', 'x', 1))
    tm.addTransition(('q3', '1'), ('q3', '1', 1))
    tm.addTransition(('q3', '0'), ('q2', 'x', -1))

    entry = '000011110101010101'

    tm.setTape(entry)
    tm.run()

    print 'Entry:', entry
    print 'Accepted:', tm.hasAccepted()

main()

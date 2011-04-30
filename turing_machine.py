from itertools import izip

class Tape:
    def __init__(self):
        self.cur_pos = 0
        self.data = {}

    def read(self):
        return self.data.get(self.cur_pos, '@')

    def writeAndMove(self, new_char, direction):
        self.data[self.cur_pos] = new_char
        self.cur_pos += direction

class State:
    def __init__(self, name, is_accepting=False):
        self.name = name
        self.transitions = {}
        self.is_accepting = is_accepting

    def getActions(self, inputs):
        return self.transitions.get(inputs, None)

    def addTransitions(self, conditions, actions):
        self.transitions[conditions] = actions

class TuringMachine:
    def __init__(self, init_state=None, num_tapes=1):
        self.states = {}
        self.current_state = init_state

        self.tapes = [Tape() for i in xrange(num_tapes)]

    def setTape(self, string):
        tape = self.tapes[0]
        for i, c in enumerate(string):
            tape[i] = c

    def step(self):
        input_tuple = (tape.read() for tape in self.tapes)
        actions = self.states[self.current_state].getNextState(input_tuples)

        num_actions = (len(actions) - 1) / 2

        next_state = actions[0]
        write_chars = actions[1:num_actions+1]
        head_moves = actions[num_actions+1:]
        for tape, char, move in izip(self.tapes, write_chars, head_moves):
            tape.writeAndMove(char, move)

def entry(self, content=[]):
    self.content = content
    self.content += '@@@' #@ representa o elemento vazio.

    while True:
        elem = self.content[self.currentPosition]
        func_trans = self.currentState.getStateToGoTo(elem)
        if func_trans == None:
             break

        elem = func_trans[0]
        state = func_trans[1]
        direction = func_trans[2]
        self.step(elem, state, direction)

    print 'Final Content: ' + str(self.content)

    return self.currentState.isAccepting


def main():
    #Maquina de turing que aceita se tiver o mesmo numero de
    #0 e 1
    state_0 = State('q0')
    state_1 = State('q1')
    state_2 = State('q2')
    state_3 = State('q3')
    state_4 = State('q4', isAccepting=True)

    state_0.setStateTransitions({'x': ('@', state_0, 1), 
                                 '0': ('@', state_1, 1),
                                 '1': ('@', state_3, 1),
                                 '@': ('@', state_4, 1)})

    state_1.setStateTransitions({'x': ('x', state_1, 1),
                                 '0': ('0', state_1, 1),
                                 '1': ('x', state_2, -1)})

    state_2.setStateTransitions({'0': ('0', state_2, -1),
                                 '1': ('1', state_2, -1),
                                 'x': ('x', state_2, -1),
                                 '@': ('@', state_0, 1)})

    state_3.setStateTransitions({'x': ('x', state_3, 1),
                                 '1': ('1', state_3, 1),
                                 '0': ('x', state_2, -1)})

    states = [state_0, state_1, state_2, state_3, state_4]
    mt = TuringMachine(states=states, initState=state_0)

    entry = '000011110101010101'
    print 'Entry: ' + entry
    print 'Accepted: ' +  str(mt.entry(list(entry)))

main()

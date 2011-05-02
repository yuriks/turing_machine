from itertools import izip
import sys

class Tape(object):
    def __init__(self):
        self.cur_pos = 0
        self.data = {}

    def read(self, pos=None):
        if pos is None:
            pos = self.cur_pos
        return self.data.get(pos, 'b')

    def writeAndMove(self, new_char, direction):
        self.data[self.cur_pos] = new_char
        self.cur_pos += direction
        if self.cur_pos < 0:
            self.cur_pos = 0

    def moveTo(self, pos):
        self.cur_pos = pos

    def getCurPos(self):
        return self.cur_pos

class State(object):
    def __init__(self, is_accepting=False):
        self.transitions = {}
        self.is_accepting = is_accepting

    def getActions(self, inputs):
        return self.transitions.get(inputs, (None, None, 0))

    def addTransition(self, conditions, actions):
        self.transitions[tuple(conditions)] = actions

    def isFinal(self):
        return len(self.transitions) == 0

    def isAccepting(self):
        return self.is_accepting

class EntryException(Exception):
    def __init__(self, character):
        self.character = character

class TuringMachine(object):
    letter_direction_map = {'E': -1, 'D': 1, 'S': 0}

    def __init__(self, init_state, num_tapes=1):
        self.initial_state = init_state
        self.states = {None: State(is_accepting=False)}
        self.alphabet = None # wildcard
        self.input_alphabet = None # wildcard

        self.tapes = [None] * num_tapes
        self.reset()

    def addState(self, name, is_accepting=False):
        if name in self.states:
            raise KeyError
        self.states[name] = State(is_accepting)

    def addTransition(self, condition, actions):
        state = condition[0]

        num_actions = (len(actions) - 1) / 2
        for i in xrange(num_actions+1, len(actions)):
            actions[i] = self.letter_direction_map[actions[i]]

        self.states[state].addTransition(condition[1:], actions)

    def setTape(self, string):
        if self.alphabet is not None:
            for ch in string:
                if ch not in self.input_alphabet:
                    raise EntryException(ch)
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

    def setNumberOfTabes(self, n):
        self.tapes = [None] * n
        self.reset()

    def setAlphabet(self, alphabet):
        self.alphabet = alphabet

    def setInputAlphabet(self, alphabet):
        if not alphabet.issubset(self.alphabet):
            raise ValueError("Input alphabet not contained in alphabet.")
        self.input_alphabet = alphabet

    def getTapes(self):
        return self.tapes

    def reset(self):
        self.current_state = self.initial_state
        self.tapes = [Tape() for i in xrange(len(self.tapes))]

def parseDescription(entry):
    for val in entry:
        entry[val] = entry[val].strip().replace(' ', '')

    entry['Q'] = entry['Q'].split(',')
    tm = TuringMachine(entry['Q'][0])
    for state in entry['Q'][:-1]:
        tm.addState(state)
    tm.addState(entry['Q'][-1], is_accepting=True)

    tm.setAlphabet(set(entry['Gamma'].split(',')))
    tm.setInputAlphabet(set(entry['Sigma'].split(',')))

    tape_set = False
    for state_trans in entry['sig'].split("),("):
        cond, action = state_trans.split(")=(")
        cond = cond.lstrip('(').rstrip(')').split(',')
        action = action.lstrip('(').rstrip(')').split(',')
        if not tape_set:
            tm.setNumberOfTabes(len(cond) - 1)
            tape_set = True
        tm.addTransition(cond, action)

    return tm

def readMachineInteractive():
    gamma = raw_input('Gamma: ')
    sigma = raw_input('Sigma: ')
    states = raw_input('Q: ')
    sig = raw_input('sig: ')

    return {'Gamma' : gamma, 'Sigma' : sigma, 'Q' : states, 'sig' : sig}

def readMachineFile(filename):
    entry = {}
    with open(filename) as f:
        for line in f:
            identifier, val = line.split(':')
            entry[identifier.strip()] = val
    return entry

def interactive_shell(tm):
    print "Para sair, pressione Ctrl + C."
    while True:
        entry = raw_input("Entrada: ")
        try:
            tm.reset()
            tm.setTape(entry)
        except EntryException, i:
            print "Erro: '%c' nao pertence ao alfabeto de entrada." % (i.character,)
            continue

        while not tm.hasFinished():
            for tape in tm.getTapes():
                cur_pos = tape.getCurPos()

                sys.stdout.write('1 ')
                for i in xrange(cur_pos - 10, cur_pos + 10):
                    if i < 0:
                        c = ' '
                    else:
                        c = tape.read(i)
                    sys.stdout.write(c)
                sys.stdout.write('\n')

                sys.stdout.write(' ' * 12 + '^ ' + str(tape.getCurPos()) + '\n')
                if tm.current_state is not None:
                    print 'Estado: ' + tm.current_state,
                else:
                    print 'Estado: qrejeita'
                raw_input()
            tm.step()

        if tm.hasAccepted():
            print "Aceita"
        else:
            print "Rejeita"

from optparse import OptionParser

def main():
    interactive = sys.stdin.isatty() and sys.stdout.isatty()

    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option('-m', '--machine', dest="machine_file",
                      help="File to read turing machine description from, instead of stdin.")
    parser.add_option('-b', '--batch',
                      action="store_false", dest="interactive",
                      help="Run in batch mode: Reads several inputs and only prints if they're accepted or not.")
    parser.add_option('-i', '--interactive',
                      action="store_true",  dest="interactive", default=interactive,
                      help="Run in interactive mode: Reads an input and let's you step through it's execution.")

    options, args = parser.parse_args()

    if options.machine_file is None:
        machine_desc = readMachineInteractive()
    else:
        machine_desc = readMachineFile(options.machine_file)

    tm = parseDescription(machine_desc)

    if not options.interactive:
        while True:
            line = sys.stdin.readline()
            if len(line) == 0:
                break

            line = line.strip()
            try:
                tm.reset()
                tm.setTape(line)
            except EntryException, i:
                print "Erro: '%c' nao pertence ao alfabeto de entrada." % (i.character,)
            else:
                if tm.run():
                    print "Aceita"
                else:
                    print "Rejeita"
    else:
        interactive_shell(tm)


if __name__ == "__main__":
    main()

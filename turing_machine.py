from itertools import izip
import sys

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

class EntryException(Exception):
    def __init__(self, character):
        self.character = character
        
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
        for ch in string:
            if ch not in self.alphabet:
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
    
    def setTapeNumber(self, n):
        self.tapes = [Tape() for i in xrange(n)]
    
    def setAplhabet(self, alpha):
        self.alphabet = alpha
        
class Parser:
    def parseEntry(self, entry):
        for val in entry:
            entry[val] = entry[val].strip().replace(' ', '')
        
        tm = TuringMachine(entry['Q'][0])
        for state in entry['Q'].split(','):
            tm.addState(state)
        
        tape_setted = False
        for state_trans in entry['sig'].split('),'):
            cond, action = state_trans.split('=')
            cond = cond.lstrip('(').rstrip(')')
            action = action.lstrip('(').rstrip(')')
            print cond + '  ' + action
            if not tape_setted:
                tm.setTapeNumber(len(cond) - 1)
                tape_setted = True
            tm.addTransition(cond, action)
            
        return tm
    def parseFromFile(self, filename):
        entry = {}
        with open(filename) as f:
            for line in f:
                identifier, val = line.replace(' ', '').split(':') 
                entry[identifier.replace(' ', '')] = val.replace(' ', '')
        return entry
        
def askEntry():
    gamma = raw_input('Gamma: ')
    sigma = raw_input('Sigma: ')
    states = raw_input('Q: ')
    sig = raw_input('sig: ')

    return {'Gamma' : gamma, 'Sigma' : sigma, 'Q' : states, 'sig' : sig}
        
def main():
    parser = Parser()
    machine_desc = None
    if len(sys.argv) == 1:
        machine_desc = askEntry()
    elif len(sys.argv) == 2:
        machine_desc = parser.parseFromFile(sys.argv[1])
    elif len(sys.argv) == 0:
        return
        
    tm = parser.parseEntry(machine_desc)
    
    for line in sys.stdin:
        print 'Entrada: ' + line
        try:
            tm.setTape(line)
        except i:
            print 'A entrada foi ignorada pois o caractere \'' + i.character + '\' nao pertence a alfabeto de entrada.'
        while not tm.hasFinished():
            print tm.current_state
            tm.step()
            raw_input()
        if tm.hasAccepted():
            print "Aceita"
        else:
            print "Rejeita"
main()

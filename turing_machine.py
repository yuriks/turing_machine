class State:
    def __init__(self, name='', stateTransitions={}, isAccepting=False):
        self.name = name
        self.stateTransitions = stateTransitions
        self.isAccepting = isAccepting

    def getStateToGoTo(self, element):
        try:
            return self.stateTransitions[element]
        except KeyError:
            return None

    def setStateTransitions(self, stateTransitions={}):
        self.stateTransitions = {}
        self.stateTransitions = stateTransitions

    def __str__(self):
        return self.name + '\nisAcc: ' + str(self.isAccepting) + '\nstates: ' + str(self.stateTransitions) + '\n'

    def __repr__(self):
        return self.name

class TuringMachine:
    def __init__(self, states=[], initState=None):
        self.states = states
        self.initState = initState
        self.content = []
        self.currentPosition = 0
        self.currentState = initState

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

    #direction: +1 (right), -1 (left) ou 0 (stay)
    def step(self, element, state, direction):
        print 'Current State: ' + self.currentState.name
        print 'Go To: ' + state.name
        print 'Read: ' + self.content[self.currentPosition]
        print 'Write: ' + element
        print 'Current Content: ' + self.strPosContent() + '\n'

        self.currentState = state
        self.content[self.currentPosition] = element

        if direction == -1 and self.currentPosition == 0:
            self.currentPosition = 0
        else:
            self.currentPosition += direction

    def strPosContent(self):
        s = ''
        i = 0
        for e in self.content:
            isIt = i == self.currentPosition
            if isIt:
                s += '['
            s += e
            if isIt:
                s += ']'
            i += 1
        return s

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

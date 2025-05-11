"""
FSM for regex matching.
"""
from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):
    """
    Base class for defining states in a Finite State Machine (FSM).
    """
    @abstractmethod
    def __init__(self) -> None:
        self.next_states = []

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass

    def check_next(self, next_char: str) -> State | None:
        """
        Checks the next state for the given character. Returns the next valid state if found.
        """
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        return None


class StartState(State):
    """
    Represents the starting state in the FSM.
    """
    next_states: list[State] = []

    def __init__(self):
        super().__init__()

    def check_self(self, char):
        """
        Always returns False for this state since it's the starting point.
        """
        return False


class TerminationState(State):
    """
    Represents the termination state in the FSM.
    """
    def __init__(self):
        super().__init__()

    def check_self(self, char: str) -> bool:
        """
        Always returns False for this state as it marks the end of the FSM processing.
        """
        return False


class DotState(State):
    """
    state for . character (any character accepted)
    """

    # next_states: list[State] = []

    def __init__(self):
        super().__init__()

    def check_self(self, char: str):
        """
        Accepts any character (always returns True).
        """
        return True


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """

    next_states: list[State] = []
    curr_sym = ""

    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.symbol = symbol

    def check_self(self, curr_char: str) -> bool:
        """
        Checks if the current character matches the expected symbol.
        """
        return curr_char == self.symbol


class StarState(State):
    """
    State for handling the '*' character, which allows repetition of a previous state.
    """
    next_states: list[State] = []

    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state
        self.next_states.append(checking_state)
        self.next_states.extend(checking_state.next_states)
        checking_state.next_states.append(self)

    def check_self(self, char):
        """
        Checks if the character matches the previous state (used for repetition).
        """
        return self.checking_state.check_self(char)



class PlusState(State):
    """
    State for handling the '+' character, which ensures the previous state occurs at least once.
    """
    next_states: list[State] = []

    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state
        self.next_states.append(checking_state)
        self.next_states.extend(checking_state.next_states)
        checking_state.next_states.append(self)

    def check_self(self, char: str) -> bool:
        """
        Checks if the character matches the previous state (requires at least one match).
        """
        return self.checking_state.check_self(char)


class RegexFSM:
    """
    Finite State Machine (FSM) for matching a regular expression pattern.
    """
    curr_state: State = StartState()
    term_state: TerminationState = TerminationState()

    def __init__(self, regex_expr: str) -> None:

        prev_state = self.curr_state
        tmp_next_state = self.curr_state

        for char in regex_expr:
            tmp_next_state = self.__init_next_state(char, prev_state, tmp_next_state)
            if tmp_next_state:
                prev_state.next_states.append(tmp_next_state)
                prev_state = tmp_next_state

        prev_state.next_states.append(self.term_state)

    def __init_next_state(
        self, next_token: str, prev_state: State, tmp_next_state: State
    ) -> State | None:
        new_state = None

        match next_token:
            case next_token if next_token == ".":
                new_state = DotState()
            case next_token if next_token == "*":
                new_state = StarState(tmp_next_state)
            case next_token if next_token == "+":
                new_state = PlusState(tmp_next_state)
            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)
            case _:
                raise AttributeError("Character is not supported")

        return new_state

    def check_string(self, input_str: str) -> bool:
        """
        Checks if the input string matches the regular expression pattern.
        """
        active_states = {self.curr_state}

        for char in input_str:
            next_active_states = set()

            for initial_state in active_states:
                visited = set()
                stack = [(initial_state, False)]

                while stack:
                    current_state, el = stack.pop()

                    if current_state is None or current_state in visited and not el:
                        continue
                    visited.add(current_state)

                    if isinstance(current_state, StarState):
                        if not el:
                            for next_s in current_state.next_states:
                                stack.append((next_s, False))
                            stack.append((current_state, True))
                        else:
                            if current_state.checking_state.check_self(char):
                                next_active_states.add(current_state.checking_state)

                    elif isinstance(current_state, PlusState):
                        if current_state.checking_state.check_self(char):
                            next_active_states.add(current_state.checking_state)
                        for next_s in current_state.next_states:
                            stack.append((next_s, False))

                    elif current_state.check_self(char):
                        for next_s in current_state.next_states:
                            next_active_states.add(next_s)
                            stack.append((next_s, False))

                    else:
                        for next_s in current_state.next_states:
                            stack.append((next_s, False))

            active_states = next_active_states
            if not active_states:
                return False

        return any(isinstance(state, TerminationState) for state in active_states)



if __name__ == "__main__":
    RGPATTERN = "a*4.+hi"

    regex_compiled = RegexFSM(RGPATTERN)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))  # True
    print(regex_compiled.check_string("meow"))  # False

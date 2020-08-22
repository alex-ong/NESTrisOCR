import numpy as np

PIC_PATTERNS = [
    "XXXXXXXXXX",
    "XXXXOOXXXX",
    "XXXOOOOXXX",
    "XXOOOOOOXX",
    "XOOOOOOOOX",
    "OOOOOOOOOO",
]


def pattern_optimizer(x):
    return x == "X"


def gen_numpy_patterns(patterns):
    optimizer_func = np.vectorize(pattern_optimizer)
    patterns = [optimizer_func(list(p)) for p in patterns]
    return np.stack(patterns)


PATTERNS = gen_numpy_patterns(PIC_PATTERNS)
NO_MATCH = len(PATTERNS)


class LineClearDetection:
    def __init__(self):
        self.prev_line_states = [NO_MATCH for i in range(20)]
        self.clearing_lines = [False for i in range(20)]
        self.prev_block_count = 0
        self.lines_cleared = []

    def reset(self):
        self.prev_line_states = [NO_MATCH for i in range(20)]
        self.prev_block_count = 0

    def process(self, field):
        field = np.where(field != 0, True, False)
        line_states = [self.match_state(line) for line in field]
        block_count = np.count_nonzero(field)
        block_diff = self.prev_block_count - block_count

        if block_diff > 0 and block_diff % 2 == 0:
            self.lines_cleared = []
            for i in range(len(self.clearing_lines)):
                is_clear = self.is_line_clear_anim(
                    line_states[i], self.prev_line_states[i]
                )
                self.clearing_lines[i] = is_clear
                if is_clear:
                    self.lines_cleared.append(i)

        # end of function, setup "prev"
        self.prev_line_states = line_states
        self.prev_block_count = block_count
        anim_state = NO_MATCH
        if len(self.lines_cleared) > 0:
            anim_state = self.prev_line_states[self.lines_cleared[0]]
        return self.lines_cleared, anim_state

    # returns true if the line is in a line clear animation
    def is_line_clear_anim(self, current, prev):
        if current == NO_MATCH:
            return False
        if current == NO_MATCH - 1 and prev in [NO_MATCH - 1, NO_MATCH - 2]:
            return False  # animation is over
        if prev == NO_MATCH:
            if current in [0, 1]:
                return True
        elif prev == NO_MATCH - 2:
            if current == NO_MATCH - 1:  # prev guaranteed to be 0-5 now...
                return True
        elif 1 <= current - prev <= 2:
            return True
        return False

    def match_state(self, line):
        for i, pattern in enumerate(PATTERNS):
            if np.array_equal(line, pattern):
                return i
        return NO_MATCH


def gen_test_clear(y_values):
    result = []
    for i in range(24):
        field = ["OOOOOOOOOO" for j in range(20)]
        for y in y_values:
            field[y] = PIC_PATTERNS[i // 4]
        result.append(gen_numpy_patterns(field))
    return result


def test_clear():
    # single
    single = gen_test_clear([17])
    double = gen_test_clear([15, 16])
    triple = gen_test_clear([16, 17, 18])
    tetris = gen_test_clear([16, 17, 18, 19])
    return [single, double, triple, tetris]


if __name__ == "__main__":
    print(PATTERNS)
    lcd = LineClearDetection()
    sequences = test_clear()
    for seq in sequences:
        for frame in seq:
            print(lcd.process(frame))

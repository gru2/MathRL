#!/usr/bin/env python3

import random
import numpy as np
import sys

class ProblemGenerator:
    
    def __init__(self):
        self.N = 16
        self.M = 4
        self.reset()
    
    def reset(self):
        self.input = np.ones((self.N), dtype=np.uint8) * ord(' ')
        self.output = np.ones((self.N), dtype=np.uint8) * ord(' ')
        self.scratch_pad = np.ones((self.M, self.N), dtype=np.uint8) * ord(' ')
        self.input_x = 0
        self.output_x = 0
        self.scratch_pad_x = 0
        self.scratch_pad_y = 0
        self.actions = []

    def generate_problem(self, problem_class, args):
        pass

    """
    < n >
    0000
    2333
    444
    2777
        ^ n - 1
    ^  n - 2
    ^   n - 3
    ^    n - 4
    """
    def generate_calc_sum_problem(self, max_digits=8, lhs=None, rhs=None):
        # Reset.
        self.reset()

        # Generate input string.
        if lhs is None:
            lhs = self.generate_number(max_digits)
        if rhs is None:
            rhs = self.generate_number(max_digits)
        input_ = f'{lhs} + {rhs}'

        # Set input.
        self.set_input_from_string(input_)

        # Scan input.
        self.move_input_cursor_to(len(input_) - 1)
        self.move_input_cursor_to(0)

        # Copy lhs and rhs to the scratch pad.
        n = max(len(lhs), len(rhs))
        self.copy_from_input(0, len(lhs), n - len(lhs) + 1, 1)
        self.copy_from_input(len(lhs) + 3, len(rhs), n - len(rhs) + 1, 2)

        # Calculate the sum of the input numbers.
        carry = 0
        for i in range(n):
            self.set_digit(n - i, 0, carry)
            ldigit = self.get_digit(n - i, 1)
            rdigit = self.get_digit(n - i, 2)
            digit = ldigit + rdigit + carry
            if digit >= 10:
                digit = digit - 10
                carry = 1
            else:
                carry = 0
            self.set_digit(n - i, 3, digit)
        n_out = n
        if carry == 1:
            self.set_digit(0, 0, carry)
            self.set_digit(0, 3, carry)
            n_out = n + 1

        # Copy the result form scratch pad to the output.
        self.copy_to_output(n + 1 - n_out, 3, n_out, 0)

    def generate_number(self, max_digits):
        n_digits = random.randint(1,max_digits)
        return self.generate_number_of_n_digits(n_digits)

    def generate_number_of_n_digits(self, n_digits):
        if n_digits == 1:
            s = chr(ord('0') + random.randint(0, 9))
            return s
            
        s = chr(ord('0') + random.randint(1, 9))
        for i in range(n_digits - 1):
            digit = chr(ord('0') + random.randint(0, 9))
            s += digit
        return s

    def set_input_from_string(self, s):
        n = len(s)
        for i in range(n):
            c = s[i]
            self.input[i] = ord(c)

    def copy_from_input(self, input_x, length, x, y):
        for i in range(length):
            self.move_input_cursor_to(input_x + i)
            self.move_cursor_to(x + i, y)
            c = self.input[input_x + i]
            self.scratch_pad[y, x + i] = c
            self.actions.append(chr(c))

    def copy_to_output(self, x, y, length, output_x):
        for i in range(length):
            self.move_output_cursor_to(output_x + i)
            self.move_cursor_to(x + i, y)
            c = self.scratch_pad[y, x + i]
            self.output[output_x + i] = c
            self.actions.append("C")


    def set_digit(self, x, y, digit):
        self.move_cursor_to(x, y)
        c = ord("0") + digit
        self.actions.append(chr(c))
        self.scratch_pad[y, x] = c

    def get_digit(self, x, y):
        self.move_cursor_to(x, y)
        c = self.scratch_pad[y, x]
        if c == ord(" "):
            return 0
        return c - ord("0")

    def repeat_action(self, action, n):
        for i in range(n):
            self.actions.append(action)

    def move_input_cursor_to(self, input_x):
        diff = input_x - self.input_x
        if diff > 0:
            self.repeat_action("IR", diff)
        if diff < 0:
            self.repeat_action("IL", -diff)
        self.input_x = input_x

    def move_output_cursor_to(self, output_x):
        diff = output_x - self.output_x
        if diff > 0:
            self.repeat_action("OR", diff)
        if diff < 0:
            self.repeat_action("OL", -diff)
        self.output_x = output_x

    def move_cursor_to(self, x, y):
        diff_x = x - self.scratch_pad_x
        if diff_x > 0:
            self.repeat_action("R", diff_x)
        if diff_x < 0:
            self.repeat_action("L", -diff_x)
        self.scratch_pad_x = x
        diff_y = y - self.scratch_pad_y
        if diff_y > 0:
            self.repeat_action("D", diff_y)
        if diff_y < 0:
            self.repeat_action("U", -diff_y)
        self.scratch_pad_y = y

    def to_string(self):
        in_ = "\n["
        out_ = "["
        for i in range(self.N):
            in_ = in_ + chr(self.input[i])
            out_ = out_ + chr(self.output[i])
        scratch_pad = ""
        for j in range(self.M):
            line = "["
            for i in range(self.N):
                line = line + chr(self.scratch_pad[j, i])
            scratch_pad = scratch_pad + line + "]\n"
        s = in_ + "]\n\n" + out_ + "]\n\n" + scratch_pad
        s += f'ix:{self.input_x} ox:{self.output_x} x:{self.scratch_pad_x} y:{self.scratch_pad_y}\n'
        s += f'actions:{self.actions}\n'
        return s

if __name__ == "__main__":
    pg = ProblemGenerator()
    pg.generate_calc_sum_problem(lhs="712", rhs="378")
    s = pg.to_string()
    print("s =", s)

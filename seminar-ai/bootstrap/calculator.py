#!/usr/bin/env python3

import sys
from argparse import ArgumentParser

class EpitechArgumentParser(ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        sys.stderr.write(f"{self.prog}: error: {message}\n")
        sys.exit(84)

def get_args():
    parser = EpitechArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--add", action="store_true")
    group.add_argument("--sub", action="store_true")
    group.add_argument("--mul", action="store_true")
    group.add_argument("--div", action="store_true")

    parser.add_argument("--float", action="store_true")
    parser.add_argument("--int", action="store_true")

    parser.add_argument("numbers", type=float, nargs="*")

    args = parser.parse_args()
    if len(args.numbers) != 2:
        print("Error: You must provide exactly two numbers.")
        sys.exit(84)

    return args

def addition(x, y):
    return x + y

def soustraction(x, y):
    return x - y

def multiplication(x, y):
    return x * y

def division(x, y, is_int=False):
    if y == 0:
        print("Error: Division by zero is not allowed.")
        sys.exit(84)
    if is_int:
        return int(x // y)
    else:
        return x / y

def main():
    args = get_args()

    x, y = args.numbers[0], args.numbers[1]

    if args.add:
        result = addition(x, y)
        print(f"{x} + {y} = {result}")

    elif args.sub:
        result = soustraction(x, y)
        print(f"{x} - {y} = {result}")

    elif args.mul:
        result = multiplication(x, y)
        print(f"{x} × {y} = {result}")

    elif args.div:
        if args.float and args.int:
            print("Warning: Both --int and --float provided. Using float division by default.")
            result = division(x, y)
            op = "/"
        elif args.int:
            result = division(x, y, is_int=True)
            op = "//"
        elif args.float:
            result = division(x, y)
            op = "/"
        else:
            print("Info: No division mode specified. Using float division by default.")
            result = division(x, y)
            op = "/"
        print(f"{x} {op} {y} = {result}")

if __name__ == "__main__":
    main()
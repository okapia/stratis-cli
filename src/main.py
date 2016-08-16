import os
import sys

from cli import run

def main():
    execution = run(sys.argv[1:])
    args = next(execution)
    print(args)
    print(os.linesep)
    return next(execution)

if __name__ == "__main__":
    main()

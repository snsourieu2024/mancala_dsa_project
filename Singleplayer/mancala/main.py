import argparse
from .ui import run_cli, run_gui

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--gui', action='store_true', help='Run with game2dboard GUI')
    p.add_argument('--depth', type=int, default=6)
    p.add_argument('--stones', type=int, default=4)
    args = p.parse_args()
    if args.gui:
        run_gui(args.stones, args.depth)
    else:
        run_cli(args.stones, args.depth)

if __name__ == '__main__':
    main()

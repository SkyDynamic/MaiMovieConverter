import os.path
import shutil

from src.cli import cmd
from src import usm_processor

if __name__ == "__main__":
    args = cmd()
    if args.only_convert_ivf and args.only_convert_usm:
        print("You can't use --only-convert-ivf and --only-convert-usm at the same time.")
        exit(0)
    if not args.reverse:
        if not args.only_convert_ivf:
            usm_processor.start_unpack(args)
        else:
            usm_processor.convert_path_ivf(args.file, args.output)
    else:
        usm_processor.start_reverse(args)
    
    if os.path.exists("temps"):
        shutil.rmtree("temps")

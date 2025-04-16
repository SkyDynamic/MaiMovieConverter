import argparse

def cmd() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='A simple command line for unpack maimai movie data file.')
    parser.add_argument('file', type=str, help='The file or dir path of the data file(s).')
    parser.add_argument('-o', '--output', type=str, help='The output dir path.', default='./output')
    parser.add_argument('-r', '--reverse', action='store_true', help='Convert the mp4 to dat (Reverse mode)')
    parser.add_argument('-c1', '--only-convert-ivf', action='store_true', help='Only convert ivf file to mp4.')
    parser.add_argument('-c2', '--only-convert-usm', action='store_true', help='Only convert usm file to ivf.')
    
    return parser.parse_args()
    
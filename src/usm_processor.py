import argparse
import os.path
import subprocess
from tqdm import tqdm

from PyCriCodecs import USM

from src import key


def start(args: argparse.Namespace):
    if not os.path.exists(args.file):
        print("File or directory not found.")
        exit(0)
    if os.path.isdir(args.file):
        files = [file for file in os.listdir(args.file) if file.endswith(".dat") or file.endswith(".usm")]
        for file in tqdm(files, desc="Processing USM files"):
            process(os.path.join(args.file, file))
        convert_path_ivf("temps", args.output)
    else:
        process(args.file)
        convert_path_ivf("temps", args.output)


def collect_ivf_files(path: str):
    ivf_files = []
    if os.path.isdir(path):
        for file in os.listdir(path):
            full_path = os.path.join(path, file)
            if file.endswith(".ivf"):
                ivf_files.append(full_path)
            elif os.path.isdir(full_path):
                ivf_files.extend(collect_ivf_files(full_path))
    elif path.endswith(".ivf"):
        ivf_files.append(path)
    return ivf_files


def convert_path_ivf(path: str, output_dir: str):
    ivf_files = collect_ivf_files(path)
    for ivf in tqdm(ivf_files, desc="Converting IVF to MP4"):
        converter_ifv_to_mp4(ivf, output_dir)


def process(file: str):
    usm = USM(file, key=key.get_key())
    usm.extract("temps")


def converter_ifv_to_mp4(ivf: str, output_dir: str):
    if check_ffmpeg_installed():
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        file_name = os.path.splitext(os.path.basename(ivf))[0]
        subprocess.run(['ffmpeg', '-i', ivf, '-c:v', 'copy', '-c:a', 'copy', f"{output_dir}/{file_name}.mp4"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        print("FFmpeg is not installed. Please install FFmpeg to convert IVF files.")
        print("FFmpeg can be downloaded from https://ffmpeg.org/download.html")
        exit(0)


def check_ffmpeg_installed():
    try:
        subprocess.check_output(['ffmpeg', '-version'])
        return True
    except OSError:
        return False

import argparse
import os.path
import subprocess
from tqdm import tqdm

from src.wannacri import wannacri


def start_unpack(args: argparse.Namespace):
    if not os.path.exists(args.file):
        print("File or directory not found.")
        exit(0)
    if os.path.isdir(args.file):
        files = [file for file in os.listdir(args.file) if file.endswith(".dat") or file.endswith(".usm")]
        for file in tqdm(files, desc="Processing USM files"):
            wannacri.extract_usm(os.path.join(args.file, file), "temps")
        convert_path_ivf("temps", args.output)
    else:
        print("Starting process " + args.file + " to ivf")
        wannacri.extract_usm(args.file, "temps")
        convert_path_ivf("temps", args.output)

def start_reverse(args: argparse.Namespace):
    if not os.path.exists(args.file):
        print("File or directory not found.")
        exit(0)
    if os.path.isdir(args.file):
        files = [file for file in os.listdir(args.file) if file.endswith(".mp4")]
        for file in tqdm(files, desc="Processing MP4 files"):
            convert_mp4_to_h264(os.path.join(args.file, file))
        convert_path_dat("temps", args.output)
    else:
        convert_mp4_to_h264(args.file)
        convert_path_dat("temps", args.output)


def collect_files(path: str, file_prefix: str):
    ivf_files = []
    if os.path.isdir(path):
        for file in os.listdir(path):
            full_path = os.path.join(path, file)
            if file.endswith(file_prefix):
                ivf_files.append(full_path)
            elif os.path.isdir(full_path):
                ivf_files.extend(collect_files(full_path, file_prefix))
    elif path.endswith(".ivf"):
        ivf_files.append(path)
    return ivf_files


def convert_path_ivf(path: str, output_dir: str):
    ivf_files = collect_files(path, ".ivf")
    for ivf in tqdm(ivf_files, desc="Converting IVF to MP4"):
        convert_ifv_to_mp4(ivf, output_dir)


def convert_path_dat(path: str, output_dir: str):
    h264_files = collect_files(path, ".264")
    for h264 in tqdm(h264_files, desc="Converting H264 to DAT"):
        wannacri.create_usm(h264, output_dir)

def convert_ifv_to_mp4(ivf: str, output_dir: str):
    if check_ffmpeg_installed():
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        file_name = os.path.splitext(os.path.basename(ivf))[0]
        subprocess.run(['ffmpeg', '-y', '-i', ivf, '-c:v', 'copy', '-c:a', 'copy', f"{output_dir}/{file_name}.mp4"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        __print_ffmpeg_not_installed()


def get_total_frames(mp4: str) -> int:
    command = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=nb_frames',
        '-of', 'default=nokey=1:noprint_wrappers=1', mp4
    ]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, check=True)
        total_frames = int(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"Error getting total frames: {e}")
        total_frames = None
    return total_frames


def convert_mp4_to_h264(mp4: str):
    if not os.path.exists("temps"):
        os.makedirs("temps")
    if check_ffmpeg_installed():
        file_name = os.path.splitext(os.path.basename(mp4))[0]
        total_frames = get_total_frames(mp4)
        if total_frames is None:
            print(f"Could not determine total frames for {mp4}. Falling back to non-progress bar conversion.")
            convert_mp4_to_h264_without_progress(mp4)
            return
        
        command = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=height',
            '-of', 'default=nokey=1:noprint_wrappers=1', mp4
        ]
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, check=True)
            height = int(result.stdout.strip())
            if height % 2 != 0:
                height -= 1
        except subprocess.CalledProcessError as e:
            print(f"Error getting video height: {e}")
            height = 606
        
        command = [
            'ffmpeg', '-y', '-i', mp4, '-vf', f'scale=1080:{height}', f"temps/{file_name}.264"
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        
        with tqdm(total=total_frames, unit='frame', desc=f"Converting {file_name} to h264") as pbar:
            while process.poll() is None:
                output = process.stdout.readline()
                if output.strip().startswith('frame='):
                    frame_str = output.strip().split('=')[1].strip()
                    frame = int(frame_str.replace(' fps', ''))
                    pbar.update(frame - pbar.n)
        
        process.wait()
    else:
        __print_ffmpeg_not_installed()


def convert_mp4_to_h264_without_progress(mp4: str):
    file_name = os.path.splitext(os.path.basename(mp4))[0]
    
    command = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=height',
        '-of', 'default=nokey=1:noprint_wrappers=1', mp4
    ]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, check=True)
        height = int(result.stdout.strip())
        if height % 2 != 0:
            height -= 1
    except subprocess.CalledProcessError as e:
        print(f"Error getting video height: {e}")
        height = 606
    
    command = [
        'ffmpeg', '-y', '-i', mp4, '-vf', f'scale=1080:{height}', f"temps/{file_name}.264"
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def __print_ffmpeg_not_installed():
    print("FFmpeg is not installed. Please install FFmpeg to convert the object.")
    print("FFmpeg can be downloaded from https://ffmpeg.org/download.html")
    exit(0)


def check_ffmpeg_installed():
    try:
        subprocess.check_output(['ffmpeg', '-version'])
        return True
    except OSError:
        return False


def check_ffprobe_installed():
    try:
        subprocess.check_output(['ffprobe', '-version'])
        return True
    except OSError:
        return False

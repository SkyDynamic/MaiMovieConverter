import os

from src import key
from src.wannacri.codec import Sofdec2Codec
from src.wannacri.usm import Vp9, H264, Usm, OpMode, is_usm


def create_usm(input_file: str, output_dir: str):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    codec = Sofdec2Codec.from_file(input_file)
    if codec is Sofdec2Codec.VP9:
        video = Vp9(input_file)
    elif codec is Sofdec2Codec.H264:
        video = H264(input_file)
    else:
        raise NotImplementedError("Non-Vp9/H.264 files are not yet implemented.")
    
    filename = os.path.splitext(os.path.basename(input_file))[0]
    usm = Usm(videos=[video], key=key_str_to_int(key.get_key()))
    with open(os.path.join(f"{output_dir}/{filename}.usm"), "wb") as f:
        for packet in usm.stream(OpMode.ENCRYPT, encoding="shift-jis"):
            f.write(packet)
    
def extract_usm(input_file: str, output_dir: str):
    if find_usm(input_file):
        filename = os.path.basename(input_file)
        try:
            usm = Usm.open(input_file, encoding="shift-jis", key=key_str_to_int(key.get_key()))
            usm.demux(
                path=output_dir,
                save_video=True,
                save_audio=True,
                save_pages=False,
                folder_name=filename,
            )
        except ValueError:
            print("Failed to decrypt USM file.")
            return

def find_usm(directory: str) -> bool:
    """Walks a path to find USMs."""
    if os.path.isfile(directory):
        with open(directory, "rb") as test:
            if not is_usm(test.read(4)):
                return False
    return True

def key_str_to_int(key_str) -> int:
    try:
        return int(key_str, 0)
    except ValueError:
        # Try again but this time we prepend a 0x and parse it as a hex
        key_str = "0x" + key_str

    return int(key_str, 16)
    
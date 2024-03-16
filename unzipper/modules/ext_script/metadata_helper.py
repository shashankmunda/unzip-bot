import os
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from mutagen.aiff import AIFF
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.wave import WAVE
from mutagen.asf import ASF
from mutagen.aac import AAC
import mutagen.id3 as id3

from unzipper.modules.ext_script.ext_helper import run_cmds_on_cr, __run_cmds_unzipper

def mapToMp3(file_path):
    return MP3(file_path, ID3=EasyID3)

def mapToMp4(file_path):
    return MP4(file_path)

def mapToFlac(file_path):
    return FLAC(file_path)

def mapToAiff(file_path):
    return AIFF(file_path)

def mapToOggVorbis(file_path):
    return OggVorbis(file_path)

def mapToOggOpus(file_path):
    return OggOpus(file_path)

def mapToWav(file_path):
    return WAVE(file_path)

def mapToAsf(file_path):
    return ASF(file_path)

def mapToAac(file_path):
    return AAC(file_path)

async def get_audio_metadata(file_path):
    file_ext = file_path.split(".")[-1].lower()
    audio_meta = {"performer": None, "title": None, "duration": None}
    audio_extensions = ["mp3","m4a","alac","flac","aif","aiff","ogg","opus","wav","wma","aac"]
    map_extension_to_container = {
        "mp3": mapToMp3(file_path),
        "m4a": mapToMp4(file_path),
        "alac": mapToMp4(file_path),
        "aif": mapToAiff(file_path),
        "aiff": mapToAiff(file_path),
        "ogg": mapToOggVorbis(file_path),
        "opus": mapToOggOpus(file_path),
        "wav": mapToWav(file_path),
        "wma": mapToAsf(file_path),
        "aac": mapToAac(file_path)
    }

    try:
        if file_ext in audio_extensions:
            audio = map_extension_to_container[file_ext]
        else:
            return audio_meta

        audio_meta["duration"] = int(audio.info.length)

        if file_ext in ["mp3","flac","aif","aiff","ogg","opus"]:
            audio_meta["performer"] = audio.get("artist", [None])[0]
            audio_meta["title"] = audio.get("title", [None])[0]

        elif file_ext in ["m4a", "alac"]:
            audio_meta["performer"] = audio.tags.get("\xa9ART", [None])[0]
            audio_meta["title"] = audio.tags.get("\xa9nam", [None])[0]

        elif file_ext == "wav":
            # WAV doesn't have a standard tagging system, handling might vary
            pass

        elif file_ext == "wma":
            audio_meta["performer"] = audio.tags.get("Author", [None])[0]
            audio_meta["title"] = audio.tags.get("WM/AlbumTitle", [None])[0]

        elif file_ext == "aac":
            # AAC tagging is not standardized, handling might vary
            pass

    except Exception:
        return audio_meta

    return audio_meta


async def convert_and_save(file_path, target_format, metadata):
    directory, filename = os.path.split(file_path)
    basename, _ = os.path.splitext(filename)
    new_file = os.path.join(directory, f"{basename}.{target_format}")

    cmd = ["ffmpeg", "-i", file_path, "-vn", new_file]
    await run_cmds_on_cr(__run_cmds_unzipper, cmd=cmd)

    if target_format == "mp3":
        audio = MP3(new_file, ID3=EasyID3)
        audio["artist"] = metadata["performer"]
        audio["title"] = metadata["title"]
        audio.save()
    elif target_format in ["m4a", "alac"]:
        audio = MP4(new_file)
        audio.tags["\xa9ART"] = metadata["performer"]
        audio.tags["\xa9nam"] = metadata["title"]
        audio.save()
    elif target_format == "flac":
        audio = FLAC(new_file)
        audio["artist"] = metadata["performer"]
        audio["title"] = metadata["title"]
        audio.save()
    elif target_format in ["aif", "aiff"]:
        audio = AIFF(new_file)
        # The metadata have to be a Frame instance
        audio["artist"] = id3.TextFrame(encoding=3, text=[metadata["performer"]])
        audio["title"] = id3.TextFrame(encoding=3, text=[metadata["title"]])
        audio.save()
    elif target_format == "ogg":
        audio = OggVorbis(new_file)
        audio["artist"] = metadata["performer"]
        audio["title"] = metadata["title"]
        audio.save()
    elif target_format == "opus":
        audio = OggOpus(new_file)
        audio["artist"] = metadata["performer"]
        audio["title"] = metadata["title"]
        audio.save()
    elif target_format == "wav":
        audio = WAVE(new_file)
        audio.save()
    elif target_format == "wma":
        audio = ASF(new_file)
        audio.tags["Author"] = metadata["performer"]
        audio.tags["WM/AlbumTitle"] = metadata["title"]
        audio.save()
    elif target_format == "aac":
        audio = AAC(new_file)
        audio.save()

    return new_file

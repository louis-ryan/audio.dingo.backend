import os
import subprocess
import logging

logger = logging.getLogger(__name__)

def process_video(input_path, output_folder):
    output_path = os.path.join(output_folder, f"processed_{os.path.basename(input_path)}")
    
    ffmpeg_command = [
        'ffmpeg',
        '-i', input_path,
        '-c:v', 'copy',
        '-af',
        'loudnorm=I=-23:TP=-1.5:LRA=7,'
        'compand=attacks=0:points=-80/-80|-12/-12|-6/-6|0/-3,'
        'dynaudnorm=f=200,'
        'equalizer=f=60:t=q:w=1:g=0,'
        'equalizer=f=300:t=q:w=1:g=-3,'
        'equalizer=f=1000:t=q:w=1:g=3,'
        'equalizer=f=4000:t=q:w=1:g=0,'
        'equalizer=f=10000:t=q:w=1:g=3,'
        'volume=3dB',
        '-c:a', 'aac',
        '-b:a', '192k',
        output_path
    ]

    logger.info(f"Executing FFmpeg command: {' '.join(ffmpeg_command)}")
    
    try:
        result = subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        logger.info(f"FFmpeg stdout: {result.stdout}")
        logger.info(f"FFmpeg stderr: {result.stderr}")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg command failed with return code {e.returncode}")
        logger.error(f"FFmpeg stdout: {e.stdout}")
        logger.error(f"FFmpeg stderr: {e.stderr}")
        raise
    
    return output_path

def get_video_duration(input_path):
    command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_path]
    result = subprocess.run(command, capture_output=True, text=True)
    return float(result.stdout.strip())
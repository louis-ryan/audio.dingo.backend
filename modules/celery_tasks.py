from celery import shared_task
from .video_processing import process_video, get_video_duration
from .waveform_generation import generate_waveform
import os
import logging

logger = logging.getLogger(__name__)

@shared_task(name='process_video_task')
def process_video_task(input_path, output_folder, use_simple=False):
    try:
        logger.info(f"Starting video processing task for {input_path}")
        logger.info(f"Input file exists: {os.path.exists(input_path)}")
        logger.info(f"Input file size: {os.path.getsize(input_path)} bytes")
        
        # Get video duration
        duration = get_video_duration(input_path)
        logger.info(f"Video duration: {duration}")
        
        # Process video
        output_path = process_video(input_path, output_folder)
        logger.info(f"Video processed and saved to {output_path}")
        logger.info(f"Output file exists: {os.path.exists(output_path)}")
        logger.info(f"Output file size: {os.path.getsize(output_path)} bytes")
        
        # Generate waveform for processed audio
        processed_waveform = generate_waveform(output_path)
        logger.info("Processed waveform generated")
        
        os.remove(input_path)  # Remove the original uploaded file
        logger.info(f"Original file {input_path} removed")
        
        result = {
            'filename': os.path.basename(output_path),
            'processed_waveform': processed_waveform
        }
        
        return result
    
    except Exception as e:
        logger.exception(f"Error in process_video_task: {str(e)}")
        raise

@shared_task(name='test_task')
def test_task():
    return "Hello, Celery is working!"
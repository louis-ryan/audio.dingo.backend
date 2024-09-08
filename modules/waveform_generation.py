import librosa

def generate_waveform(audio_path, num_samples=1000):
    y, sr = librosa.load(audio_path, sr=None, mono=True)
    if len(y) > num_samples:
        y = librosa.resample(y=y, orig_sr=sr, target_sr=int(sr * num_samples / len(y)))
    
    # Multiply each value by 100
    y = y * 200
    
    return y.tolist()

# Ensure the function is available when importing *
__all__ = ['generate_waveform']
from pydub import AudioSegment
import logging
from typing import List, Optional
import os

logger = logging.getLogger(__name__)

class AudioMerger:
    def __init__(self, silence_duration: float = 1.0):
        """
        Initialize the AudioMerger.
        
        Args:
            silence_duration (float): Duration of silence between audio files in seconds.
                                    Defaults to 1 second.
        """
        self.silence_duration = silence_duration
        
    def _create_silence(self, duration_ms: int) -> AudioSegment:
        """
        Create a silent AudioSegment.
        
        Args:
            duration_ms (int): Duration of silence in milliseconds.
            
        Returns:
            AudioSegment: A silent audio segment.
        """
        return AudioSegment.silent(duration=duration_ms)
    
    def merge_wav_files(self, 
                       wav_files: List[str], 
                       output_file: str,
                       normalize: bool = True) -> None:
        """
        Merge multiple WAV files into a single file with silence between them.
        
        Args:
            wav_files (List[str]): List of paths to WAV files to merge.
            output_file (str): Path where the merged WAV file will be saved.
            normalize (bool): Whether to normalize the audio volume. Defaults to True.
        
        Raises:
            FileNotFoundError: If any input file doesn't exist.
            ValueError: If the wav_files list is empty.
        """
        if not wav_files:
            raise ValueError("No WAV files provided for merging")
            
        logger.info(f"Merging {len(wav_files)} WAV files into {output_file}")
        
        # Create silence segment
        silence = self._create_silence(int(self.silence_duration * 1000))
        
        # Initialize merged audio with first file
        first_file = wav_files[0]
        if not os.path.exists(first_file):
            raise FileNotFoundError(f"File not found: {first_file}")
            
        merged = AudioSegment.from_wav(first_file)
        
        # Add remaining files with silence between them
        for wav_file in wav_files[1:]:
            if not os.path.exists(wav_file):
                raise FileNotFoundError(f"File not found: {wav_file}")
                
            # Add silence
            merged += silence
            
            # Add next audio file
            audio = AudioSegment.from_wav(wav_file)
            merged += audio
        
        # Normalize if requested
        if normalize:
            logger.debug("Normalizing audio volume")
            merged = merged.normalize()
        
        # Export the final audio
        logger.info(f"Exporting merged audio to {output_file}")
        merged.export(output_file, format="wav")
        
    @staticmethod
    def get_audio_length(wav_file: str) -> float:
        """
        Get the length of an audio file in seconds.
        
        Args:
            wav_file (str): Path to the WAV file.
            
        Returns:
            float: Length of the audio in seconds.
            
        Raises:
            FileNotFoundError: If the file doesn't exist.
        """
        if not os.path.exists(wav_file):
            raise FileNotFoundError(f"File not found: {wav_file}")
            
        audio = AudioSegment.from_wav(wav_file)
        return len(audio) / 1000.0  # Convert milliseconds to seconds

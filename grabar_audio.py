import sounddevice as sd
from scipy.io.wavfile import write

# Set parameters
fs = 44100  # Sample rate (samples per second)
seconds = 5  # Duration of recording

print("Recording for 5 seconds...")
print(sd.query_devices())
#sd.default.device = 1

# Record audio for the given number of seconds
recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
sd.wait()  # Wait until recording is finished
print("Recording complete.")

# Save the recording to a file
write("output.wav", fs, recording)
print("Audio saved as output.wav")

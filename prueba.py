import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv
import numpy as np
import random

freq = 4410

duration = 5
id = 0
recording = sd.rec(int(duration * freq),
samplerate=freq, channels=2)

sd.wait()


write("recording0.wav", freq, recording)
np.savetxt('audio_output.txt', recording)

wv.write(f"´{random.randint(1,1000)}.wav",  recording, freq, sampwidth=2)


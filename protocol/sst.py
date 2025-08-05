import pyaudio
import wave
import whisper
import numpy as np
from time import time as t

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
model = whisper.load_model("base", device="cuda")  # Load Whisper model
threshold=500
silence_duration=3
chunk_size=512
duration_limit=60
    
   
def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=chunk_size)

    print("Recording...")

    frames = []
    silence_counter = 0
    start_time = t()
    
    while True:
        data = stream.read(chunk_size, exception_on_overflow=False)
        frames.append(data)
        
        # Convert audio chunk to numpy array to analyze sound energy
        audio_data = np.frombuffer(data, dtype=np.int16)
        energy = np.sum(audio_data ** 2) / len(audio_data)  # Calculate energy of the audio chunk

        if energy < threshold:  # If energy is low, increase silence counter
            silence_counter += 1
        else:
            silence_counter = 0  # Reset counter if speaking is detected

        # Stop recording after a period of silence
        if silence_counter > silence_duration * RATE / chunk_size or t() - start_time > duration_limit:
            print("Silence detected or time limit reached, stopping recording.")
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recording to a file
    with wave.open("voice\\recorded.wav", 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    # Transcribe the audio
    result = model.transcribe("voice\\recorded.wav", fp16=False, language='English')
    msg = result["text"]
    
    return (msg)

def RECORD_PPR():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=chunk_size)
    while True:
        data = stream.read(chunk_size, exception_on_overflow=False) #512 is the chunk size
        audio_data = np.frombuffer(data, dtype=np.int16)
        energyR = np.sum(audio_data ** 2) / len(audio_data)
        print(energyR)

        if energyR > 2000:
            print("\nWaiting for next speech...\n")
            return (record_audio())
            
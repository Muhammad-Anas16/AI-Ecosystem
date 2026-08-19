import sounddevice as sd

SAMPLE_RATE = 16000
DURATION = 5  # seconds

print(f"{DURATION} second recording shuru — abhi bolna shuru karo...")
recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
sd.wait()

recording.tofile("test_audio.pcm")
print("test_audio.pcm ban gayi — ab Postman mein WebSocket se bhejo.")
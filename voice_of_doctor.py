import os
from gtts import gTTS
import subprocess
import platform

from playsound import playsound
import elevenlabs
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment

# Read API key safely
os.environ["ELEVENLABS_API_KEY"] = "sk_161f4bc426fb081bf48d9719ad280dfc2816896f8a9d10fd"
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY is not set. Please set it in your environment variables.")

def convert_mp3_to_wav(mp3_path, wav_path):
    """Convert MP3 file to WAV using pydub."""
    sound = AudioSegment.from_mp3(mp3_path)
    sound.export(wav_path, format="wav")


def play_audio(output_filepath):
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(['afplay', output_filepath])
        elif os_name == "Windows":  # Windows
            wav_path = output_filepath.replace('.mp3', '.wav')
            convert_mp3_to_wav(output_filepath, wav_path)
            subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{wav_path}").PlaySync();'])
            os.remove(wav_path)  # Clean up temporary WAV file
        elif os_name == "Linux":  # Linux
            subprocess.run(['aplay', output_filepath])  # or use mpg123 if needed
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"An error occurred while trying to play the audio: {e}")


def text_to_speech_with_gtts(input_text, output_filepath):
    language = "en"

    audioobj = gTTS(
        text=input_text,
        lang=language,
        slow=False
    )
    audioobj.save(output_filepath)

    play_audio(output_filepath)


def text_to_speech_with_elevenlabs(input_text, output_filepath):
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio = client.generate(
        text=input_text,
        voice="Aria",
        output_format="mp3_22050_32",
        model="eleven_turbo_v2"
    )
    elevenlabs.save(audio, output_filepath)

    play_audio(output_filepath)


# Example usage:
if __name__ == "__main__":
    input_text = "Hi, this is autoplay testing!"

    print("Using gTTS...")
    text_to_speech_with_gtts(input_text, "gtts_testing_autoplay.mp3")

    print("Using ElevenLabs...")
    text_to_speech_with_elevenlabs(input_text, "elevenlabs_testing_autoplay.mp3")

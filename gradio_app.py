import os
import gradio as gr
from pydub import AudioSegment

from brain import encode_image, analyze_image
from voice_of_patient import transcribe_with_groq
from voice_of_doctor import text_to_speech_with_elevenlabs

system_prompt = """You have to act as a professional doctor, i know you are not but this is for learning purpose. 
What's in this image?. Do you find anything wrong with it medically? 
If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
Donot say 'In the image I see' but say 'With what I see, I think you have ....'
Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
Keep your answer concise (max 2 sentences). No preamble, start your answer right away please."""

def process_inputs(audio_filepath, image_filepath):
    print(f"Received audio file: {audio_filepath}")

    # Convert Gradio audio to WAV (Groq prefers standard WAV format)
    audio_for_groq = "converted_for_groq.wav"
    try:
        audio = AudioSegment.from_file(audio_filepath)
        audio.export(audio_for_groq, format="wav")
        print(f"Audio converted and saved as {audio_for_groq}")
    except Exception as e:
        print(f"ERROR converting audio: {e}")
        return "Error converting audio file", "Audio conversion failed", None

    # Transcribe with Groq
    speech_to_text_output = transcribe_with_groq(
        stt_model="whisper-large-v3",
        audio_filepath=audio_for_groq,
        GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
    )

    if not speech_to_text_output or speech_to_text_output.strip() == "":
        speech_to_text_output = "[No speech detected]"
        print("WARNING: No speech detected.")

    # Analyze the image + text
    if image_filepath:
        doctor_response = analyze_image(
            query=system_prompt + speech_to_text_output,
            encoded_img=encode_image(image_filepath),
            model="meta-llama/llama-4-maverick-17b-128e-instruct"
        )
    else:
        doctor_response = "No image provided for analysis."

    # Generate doctor voice response
    try:
        voice_of_doctor = text_to_speech_with_elevenlabs(
            input_text=doctor_response,
            output_filepath="final.mp3"
        )
    except Exception as e:
        print(f"ERROR generating voice: {e}")
        voice_of_doctor = None

    return speech_to_text_output, doctor_response, voice_of_doctor

iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath"),
        gr.Image(type="filepath")
    ],
    outputs=[
        gr.Textbox(label="Speech to Text"),
        gr.Textbox(label="Doctor's Response"),
        gr.Audio("final.mp3")
    ],
    title="AI Doctor with Vision and Voice"
)

iface.launch(debug=True)

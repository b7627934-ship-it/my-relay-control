import os
import io
from flask import Flask, request, jsonify
from pydub import AudioSegment
import speech_recognition as sr

app = Flask(__name__)

# פונקציה להוספת שקט
def add_silence(audio_segment: AudioSegment) -> AudioSegment:
    silence = AudioSegment.silent(duration=1000)
    return silence + audio_segment + silence

def recognize_speech(audio_segment: AudioSegment) -> str:
    recognizer = sr.Recognizer()
    try:
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0)
        
        with sr.AudioFile(wav_io) as source:
            data = recognizer.record(source)
            
        return recognizer.recognize_google(data, language="he-IL")
    except Exception as e:
        print(f"Recognition error: {e}")
        return ""

@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty file"}), 400

    try:
        audio_data = io.BytesIO(file.read())
        audio_segment = AudioSegment.from_file(audio_data)
        
        processed_audio = add_silence(audio_segment)
        recognized_text = recognize_speech(processed_audio)
        
        return jsonify({"recognized_text": recognized_text})
        
    except Exception as e:
        print(f"Processing error: {e}")
        return jsonify({"error": "Processing error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

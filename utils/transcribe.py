import os
import requests
import tempfile
import subprocess
import whisper

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def transcribe_audio(audio_path):
    """
        First, it tries to use the Whisper API via OpenRouter.
        If it fails → it falls back to the local Whisper (small) model.
        If the transcription quality is poor → it retries with the Whisper medium model.
        Automatically supports both Arabic and English.
    """

    # optimizate the voice before analyzing
    wav_path = tempfile.mktemp(suffix=".wav")
    subprocess.run(
        [
            "ffmpeg", "-i", audio_path,
            "-ar", "16000", "-ac", "1",
            "-af", "loudnorm",  # optimize
            "-c:a", "pcm_s16le",
            wav_path, "-y"
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    text = ""

    # first try: OpenRouter API (Whisper Large-V3-Turbo)
    if OPENROUTER_API_KEY:
        try:
            url = "https://openrouter.ai/api/v1/audio/transcriptions"
            headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
            files = {"file": open(wav_path, "rb")}
            data = {"model": "openai/whisper-large-v3-turbo"}

            response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
            files["file"].close()

            if response.status_code == 200:
                text = response.json().get("text", "").strip()
                if len(text) > 5:
                    os.remove(wav_path)
                    return text
                else:
                    print("The transcription from OpenRouter is poor, switching to the local Whisper model.")
            else:
                print("OpenRouter failed:", response.text)
        except Exception as e:
            print("Error using OpenRouter:", e)

    # 2nd try: local Whisper (Hybrid Mode)
    print(" Using local Whisper fallback (hybrid mode)...")

    # small model " suitable for poor devices"
    model_small = whisper.load_model("small")
    result_small = model_small.transcribe(
        wav_path,
        fp16=False,
        language=None,
        task="transcribe"
    )
    text = result_small["text"].strip()

    # if the text is too short or unclear → use the medium model
    if len(text) < 10 or "..." in text or text.lower() in ["", "unknown"]:
        print("The transcription from the small model is poor, switching to the medium model.")
        model_medium = whisper.load_model("medium")
        result_medium = model_medium.transcribe(
            wav_path,
            fp16=False,
            language=None,
            task="transcribe"
        )
        text = result_medium["text"].strip()

    os.remove(wav_path)
    return text


    os.remove(wav_path)
    return result["text"].strip()

#strong model
#model = whisper.load_model("large-v3")
#result = model.transcribe(
    #wav_path,
   # fp16=False,
  #  language=None,  # auto-detect (ar - en )
 #   task="transcribe"
#)
import logging
import os
import tempfile
import json
import subprocess
from azure.functions import HttpRequest, HttpResponse

def main(req: HttpRequest) -> HttpResponse:
    logging.info("🔧 Auphonic-style function triggered.")

    # Check if a file and preset were provided
    file = req.files.get('file')
    preset = req.form.get('preset')
    if not file or not preset:
        logging.error("❌ 'file' or 'preset' parameter missing.")
        return HttpResponse("❌ 'file' and 'preset' are required.", status_code=400)

    logging.info(f"✅ Function is alive. Received preset: {preset}")

    try:
        # Save the input audio
        input_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        file.save(input_temp.name)
        logging.info(f"📦 Saved input audio to {input_temp.name}")

        # Load preset JSON
        preset_path = os.path.join("presets", f"{preset}.json")
        if not os.path.exists(preset_path):
            logging.error("❌ Preset file not found.")
            return HttpResponse("❌ Preset not found.", status_code=400)

        with open(preset_path, "r") as f:
            config = json.load(f)

        background_img = config.get("background", "assets/default.png")
        intro_path = "assets/IntroFile5.mp3"
        outro_path = "assets/Outrofile5.mp3"
        logging.info(f"🎨 Using background: {background_img}")

        # Create the concatenated audio with intro and outro
        final_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        cmd_audio = [
            "ffmpeg", "-y",
            "-i", f"concat:{intro_path}|{input_temp.name}|{outro_path}",
            "-acodec", "copy",
            final_audio.name
        ]
        subprocess.run(cmd_audio, capture_output=True)
        logging.info(f"🎧 Combined audio at {final_audio.name}")

        # Generate waveform video
        output_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        cmd_video = [
            "ffmpeg", "-y",
            "-i", final_audio.name,
            "-loop", "1", "-i", background_img,
            "-filter_complex", "[0:a]showwaves=s=1280x720:mode=line:rate=25:colors=white[fg];[1:v][fg]overlay=format=auto",
            "-map", "0:a", "-map", "1:v",
            "-shortest",
            output_video.name
        ]
        subprocess.run(cmd_video, capture_output=True)
        logging.info(f"🎬 Generated waveform video: {output_video.name}")

        # Serve the final video
        with open(output_video.name, "rb") as f:
            return HttpResponse(f.read(), mimetype="video/mp4")

    except Exception as e:
        logging.exception("💥 Unexpected error occurred.")
        return HttpResponse(f"Error: {str(e)}", status_code=500)

import logging
import azure.functions as func
import os
import subprocess

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("🔧 Auphonic-style function triggered.")

    preset = req.params.get("preset")
    if not preset:
        return func.HttpResponse("❌ 'preset' parameter missing.", status_code=400)

    return func.HttpResponse(f"✅ Function is alive. Received preset: {preset}", status_code=200)

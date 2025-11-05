import os
from TTS.api import TTS

# المسار المحلي للنموذج
MODEL_PATH = "tts_model/"

# تحميل النموذج محلياً فقط
def load_local_tts():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"❌ نموذج TTS غير موجود في {MODEL_PATH}")

    tts_female = TTS(model_path=MODEL_PATH, gpu=False)
    tts_male = TTS(model_path=MODEL_PATH, gpu=False)  # يمكن تعديل لاختيار نموذج رجالي مختلف إذا موجود
    return tts_female, tts_male

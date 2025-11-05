import os
from transformers import cached_download

# ===== إعدادات التحميل =====
MODEL_ID = "MBZUAI/speecht5_tts_clartts_ar"
MODEL_DIR = "models/speecht5_tts_clartts_ar"

os.makedirs(MODEL_DIR, exist_ok=True)

print(f"⏳ جاري تحميل النموذج {MODEL_ID} ...")

# تحميل النموذج إلى المجلد المحلي
cached_download(MODEL_ID, cache_dir=MODEL_DIR)

print(f"✅ تم تحميل النموذج وحفظه في: {MODEL_DIR}")

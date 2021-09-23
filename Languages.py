# import sys
ASR_lang_convertor = {
    "Arabic":"ar-EG",
    "English":"en-US",
    "French":"fr-FR",
    "Chinese":"zh (cmn-Hans-CN)",
    "Russian":"ru-RU",
    "Ukraninan":"uk-UA"
}
MT_lang_convertor = {
    "Arabic" : "ar",
    "English" : "en",
    "French" : "fr",
    "Chinese" : "ch",
    "Russian" : "ru",
    "Ukraninan" : "uk"
}
TTS_lang_convertor = {
    "English" : "en-US",
    "French" : "fr-FR",
    "Chinese" : "yue-HK",
    "Russian" : "ru-RU",
    "Ukraninan" : "uk-UA"
}

Speakers = {
    "English" : { "m" : "en-US-Wavenet-A", "f" : "en-US-Wavenet-C"},
    "French" : {"m" : "fr-FR-Wavenet-B", "f":"fr-FR-Wavenet-A"},
    "Chinese" : {"m":"yue-HK-Standard-B","f":"yue-HK-Standard-A"},
    "Russian" : {"m":"ru-RU-Wavenet-B", "f":"ru-RU-Wavenet-A"},
    "Ukraninan" : {"f":"uk-UA-Wavenet-A"}
}
def get_lang_ASR(lang):
    return ASR_lang_convertor[lang]
def get_lang_MT(lang):
    return MT_lang_convertor[lang]
def get_lang_TTS(lang):
    return TTS_lang_convertor[lang]
def get_lang_Speaker(lang):
    return Speakers[lang]
# sys.modules[__name__] = get_lang
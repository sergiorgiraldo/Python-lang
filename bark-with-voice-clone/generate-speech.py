from bark.api import generate_audio
from transformers import BertTokenizer
from bark.generation import SAMPLE_RATE, preload_models, codec_decode, generate_coarse, generate_fine, generate_text_semantic

# Enter your prompt and speaker here
text_prompt = "Oi, Sou o Carlos. Meu time sempre foi o Palmeiras, eu vivo na Holanda e pizza fria permanece meu prato preferido [risos]"
voice_name = "srg" # use your custom voice name here if you have one

# load the tokenizer
tokenizer = BertTokenizer.from_pretrained("neuralmind/bert-base-portuguese-cased")

# download and load all models
preload_models(
    text_use_gpu=True,
    text_use_small=False,
    coarse_use_gpu=True,
    coarse_use_small=False,
    fine_use_gpu=True,
    fine_use_small=False,
    codec_use_gpu=True,
    force_reload=False,
    path="models"
)

# simple generation
# audio_array = generate_audio(text_prompt, history_prompt=voice_name, text_temp=0.7, waveform_temp=0.7)

# generation with more control
x_semantic = generate_text_semantic(
    text_prompt,
    history_prompt=voice_name,
    temp=0.7,
    top_k=50,
    top_p=0.95,
)

x_coarse_gen = generate_coarse(
    x_semantic,
    history_prompt=voice_name,
    temp=0.7,
    top_k=50,
    top_p=0.95,
)
x_fine_gen = generate_fine(
    x_coarse_gen,
    history_prompt=voice_name,
    temp=0.5,
)
audio_array = codec_decode(x_fine_gen)

from scipy.io.wavfile import write as write_wav
# save audio
filepath = "/Users/GK47LX/source/Python-lang/bark-with-voice-clone/output/audio_generated.wav" # change this to your desired output path
write_wav(filepath, SAMPLE_RATE, audio_array)
from bark.generation import load_codec_model, generate_text_semantic
from encodec.utils import convert_audio

import torchaudio
import torch

model = load_codec_model(use_gpu=True)
# Load and pre-process the audio waveform
audio_filepath = 'audio.wav' # the audio you want to clone (will get truncated so 5-10 seconds is probably fine, existing samples that I checked are around 7 seconds)
device = 'cpu' # or 'cuda'
wav, sr = torchaudio.load(audio_filepath)
wav = convert_audio(wav, sr, model.sample_rate, model.channels)
wav = wav.unsqueeze(0).to(device)
with torch.no_grad():
    encoded_frames = model.encode(wav)
codes = torch.cat([encoded[0] for encoded in encoded_frames], dim=-1).squeeze()  # [n_q, T]
text = "Transcription of the audio you are cloning, this is merely sample words. in a world where ants are kings, a butterfly will fly his wings over the shoulder. any meal anticipated goes tired and beatiful. cars passing by read books about dwarfs and light sabers."
seconds = wav.shape[-1] / model.sample_rate
# generate semantic tokens
semantic_tokens = generate_text_semantic(text, max_gen_duration_s=seconds, top_k=50, top_p=.95, temp=0.7) # not 100% sure on this part
codes = codes.cpu().numpy()
import numpy as np
voice_name = 'srg' # whatever you want the name of the voice to be
output_path = 'bark/assets/prompts/' + voice_name + '.npz'
np.savez(output_path, fine_prompt=codes, coarse_prompt=codes[:2, :], semantic_prompt=semantic_tokens)
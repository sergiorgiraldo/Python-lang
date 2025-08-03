import os
import sys
import argparse
import azure.cognitiveservices.speech as speechsdk
from pathlib import Path

class AzureTextToSpeech:
    def __init__(self, subscription_key=None, region=None):
        """
        Initialize Azure Text-to-Speech client
        
        Args:
            subscription_key (str): Azure subscription key (optional, can use env var)
            region (str): Azure region (optional, can use env var)
        """
        # Get credentials from parameters or environment variables
        self.subscription_key = subscription_key or os.getenv('AZURE_SPEECH_KEY')
        self.region = region or os.getenv('AZURE_SPEECH_REGION')
        
        if not self.subscription_key or not self.region:
            raise ValueError(
                "Azure credentials not found. Please provide subscription_key and region "
                "or set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables."
            )
        
        # Create speech config
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.subscription_key, 
            region=self.region
        )
        
        # Set default voice (you can change this)
        self.speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"
    
    def text_to_speech_file(self, text, output_file="output.wav"):
        """
        Convert text to speech and save to file
        
        Args:
            text (str): Text to convert to speech
            output_file (str): Output audio file path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create audio config for file output
            audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
            
            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config, 
                audio_config=audio_config
            )
            
            # Perform synthesis
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print(f"Audio saved to: {output_file}")
                return True
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print(f"Speech synthesis canceled: {cancellation_details.reason}")
                if cancellation_details.error_details:
                    print(f"Error details: {cancellation_details.error_details}")
                return False
            
        except Exception as e:
            print(f"Error during synthesis: {str(e)}")
            return False
    
    def text_to_speech_speaker(self, text):
        """
        Convert text to speech and play through speakers
        
        Args:
            text (str): Text to convert to speech
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create synthesizer with default audio output (speakers)
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)
            
            # Perform synthesis
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print(f"Played audio for: '{text}'")
                return True
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print(f"Speech synthesis canceled: {cancellation_details.reason}")
                if cancellation_details.error_details:
                    print(f"Error details: {cancellation_details.error_details}")
                return False
                
        except Exception as e:
            print(f"✗ Error during synthesis: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Azure Text-to-Speech Application')
    parser.add_argument('word',                                 help='English word to convert to speech')
    parser.add_argument('--output', '-o',                       help='Output audio file (optional)')
    parser.add_argument('--play', '-p', action='store_true',    help='Play audio through speakers instead of saving to file')
    parser.add_argument('--key',                                help='Azure subscription key (optional if env var set)')
    parser.add_argument('--region',                             help='Azure region (optional if env var set)')
    
    args = parser.parse_args()
    
    try:
        # Initialize TTS client
        tts = AzureTextToSpeech(subscription_key=args.key, region=args.region)
        
        if args.play:
            # Play through speakers
            success = tts.text_to_speech_speaker(args.word)
        else:
            # Save to file
            output_file = args.output or f"{args.word}.wav"
            success = tts.text_to_speech_file(args.word, output_file)
        
        if not success:
            sys.exit(1)
            
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nSetup instructions:")
        print("1. Set environment variables:")
        print("   export AZURE_SPEECH_KEY='your-subscription-key'")
        print("   export AZURE_SPEECH_REGION='your-region'")
        print("2. Or provide them as command line arguments:")
        print("   python main.py hello --key YOUR_KEY --region YOUR_REGION")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
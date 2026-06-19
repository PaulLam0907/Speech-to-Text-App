import os
import sys
import datetime

# Force application to look for ffmpeg.exe in the execution directory
# Detect if running as a packaged cx_Freeze executable or raw python script
if getattr(sys, "frozen", False):
    dir_path = os.path.dirname(sys.executable) # Root folder of your built .exe
    
else:
    dir_path = os.path.dirname(os.path.realpath(__file__)) # Dev folder

os.environ["PATH"] += os.pathsep + dir_path


import whisper  # openai-whisper

# to provide ffmpeg for whisper (for local development; without installing system-wide; not added to env PATH variable)
# install : ffmpeg-downloader
# run : ffdl install --add-path
# installed in  C:\Users\PAUL\AppData\Local\ffmpegio\ffmpeg-downloader\ffmpeg\bin\ffmpeg.exe
# os.environ["PATH"] += os.pathsep + r"C:\Users\PAUL\AppData\Local\ffmpegio\ffmpeg-downloader\ffmpeg\bin"


class SpeechToText:
    """
    Transcribe audio into text
    
    Basic Usage :
    transcriber = SpeechToText()  # initialize
    result = transcriber.transcribe("audio.mp3", "base")  # transcribe audio
    text = transcriber.format_transcribed_text(result)  # convert into readable text
    transcriber.write_file(text)  # write to file
    """
    
    def __init__(self):
        self.model_location = f"C:\\Users\\{os.getlogin()}\\.cache\\whisper\\"
        self.audio_file_name = "audio.mp3"
        
    def get_available_language(self):
        return whisper.tokenizer.LANGUAGES.items()
        
    def get_loaded_model(self):
        """
        Get list of downloaded model
        
        :return: list of str containing name of model
        """
        models = []
        
        for item in os.listdir(self.model_location):
            
            if item[-3:] == ".pt":
                # print(item)
                models.append(item)
                
        return models
        
    def remove_loaded_model(self, model_name):
        """
        Delete downloaded model
        
        :param model_name: str, name of the model e.g. base (without .pt)
        :return: None
        """
        os.remove(self.model_location + model_name + ".pt")
        
    def load_model(self, model_name):
        """
        Load model for transcription. Auto download if does not exist
        
        Model  | Relative Speed |  VRAM  | Best Use Case | English Only Version
        tiny   |      10x       |  ~1GB  | lower accuracy | tiny.en
        base   |       7x       |  ~1GB  | typical usage | base.en
        small  |       4x       |  ~2GB  | Standard everyday transcription | small.en
        medium |       2x       |  ~5GB  | High-quality needs; Heavy accents; higher accuracy for multi-lingual | medium.en
        large  |       1x       | ~10GB  | Maximum accuracy; Complex & technical terminology; translation | Multilingual only
        turbo  |       8x       |  ~6GB  | accuracy=large; speed=tiny; real-time transcription with low latency | Multilingual only
        
        :param model_name: name of the model e.g. base (without .pt)
        :return: whisper.load_model()
        """
        print(f"Loading model {model_name}.pt. . .")
        
        return whisper.load_model(model_name)
    
    def transcribe(self,
                   audio_file_name,
                   model_name,
                   language = "en",
                   initial_prompt = None,
                   condition_on_previous_text = True,
                   temperature = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
                   no_speech_threshold = 0.6):
        """
        Transcribe audio into text
        
        :param audio_file_name: str, file name of audio file
        :param model_name: str, name of model for transcribing e.g. base (without .pt)
        :param language: str, main language of the audio's speech
        :param initial_prompt: str, to tailor transcription process e.g. spelling technical vocabulary, enforcing formatting and punctuation, fixing capitalization styles, etc.
        :param condition_on_previous_text: bool, True : use previous transcript as context for next 30s; False : transcribe independently without acknowledging previous step e.g. reset the punctuation logic for each 30s chunk
        :param temperature: float [0, 1], randomness and creativity of the model's transcription generation; scale the probability scores during decoding; low temperature = deterministic, accurate, no hallucinations; high temperature = creative
        :param no_speech_threshold: float [0, 1], how sensitive the model is to silence; if detected probability for no-speech audio segment exceed this value, the audio segment is considered silence and skipped; lower value (0.3) for duo-lingual audio; 0 = sensitive to silence and skip segment; 1 = sensitive to speech and keep segment
        :return: whisper.load_model().transcribe()
        """
        self.audio_file_name = audio_file_name
        
        # load model
        model = self.load_model(model_name)
        
        # transcribe the audio file
        # If you get a CUDA error on GPU, pass fp16 = False
        print("Transcribing audio . . .")
        result = model.transcribe(
                self.audio_file_name,
                language = language,  # main language is english
                # task = "transcribe",  # transcribe only, do not translate
                initial_prompt = initial_prompt,
                verbose = True,  # True : show the real-time text decoding process; False : enable progress bar; None : silent todo
                condition_on_previous_text = condition_on_previous_text,
                temperature = temperature,  # 0.0
                no_speech_threshold = no_speech_threshold,  # 0.3
        )
        print("Done")
        
        return result
    
    def format_transcribed_text(self, result, include_timestamp = False):
        """
        Format the raw transcribed text to make it readable
        
        Usage :
        transcriber = SpeechToText()
        result = transcriber.transcribe(...)
        formatted_text = transcriber.format_transcribed_text(result)
        # ready to write file
        
        :param result: raw transcribed result, the return of SpeechToText().transcribe
        :param include_timestamp: bool, indicate whether timestamp is included in the displayed output text
        :return: str
        """
        # prepare transcribed text for output
        print("Formatting transcribed text . . .")
        text_list = []
        
        for segment in result["segments"]:
            segment_text = segment["text"].strip()
            
            if include_timestamp:
                segment_start_time = int(segment["start"])  # second
                segment_start_time = str(datetime.timedelta(seconds = segment_start_time))  # HH:MM:SS.mmm
                line = f" {segment_start_time:>8} | {segment_text} \n"
            
            else:
                line = f"{segment_text}"
                
            text_list.append(line)
        
        text = " ".join(text_list)
        print("Done")
        
        return text
    
    def write_file(self, text, file_name = None, encoding = "utf-8", extension = ".txt"):
        """
        Write text into file
        
        :param text: str
        :param file_name: str, file name of the output file, default to self.audio_file_name (updated in SpeechToText().transcribe())
        :param encoding: str, how the text is encoded in the text file
        :param extension: str, extension of file
        :return: None
        """
        if file_name:
            transcript_file_name = file_name + extension
        
        else:
            transcript_file_name = self.audio_file_name[:self.audio_file_name.index(".")] + extension
            
        print(f"Writing transcript into file ({transcript_file_name}) . . .")
        
        with open(transcript_file_name, "w", encoding = encoding, errors = "replace") as file:
            # file.write(result["text"])
            file.write(text)
            file.close()
            
        print("Done")
        

# transcriber = SpeechToText()
# transcriber.get_loaded_model()

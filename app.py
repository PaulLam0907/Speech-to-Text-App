import os
import shutil
from pathlib import Path
import tempfile
import streamlit as st

import transcribe
transcriber = transcribe.SpeechToText()

# title
st.title("My Speech To Text App")
st.header("Transcribe audio speech into text")

# file upload
st.subheader("1. Select Audio File")
file = st.file_uploader("Audio file to transcribe")

# model used for transcription
st.subheader("2. Select a Model")
models = ["tiny", "base", "small", "medium", "large", "turbo"]
models_descriptions = [
    "Lower accuracy",
    "Typical usage",
    "Standard everyday transcription",
    "High-quality needs. Heavy accents. Higher accuracy for multi-lingual",
    "Maximum accuracy. Complex & technical terminology. Translation",
    "accuracy = large; speed = tiny"
]
model = st.selectbox(
        "Choose a model :",
        options = models,
        index = 3,
        help = "This model is used to transcribe your audio"
)
st.caption("Usage : " + models_descriptions[models.index(model)])

# info for choosing suitable model
with st.popover("How to choose the suitable model ?"):
    st.markdown("#### How to choose the suitable model ?")
    st.write("Choose the model according to your needs")
    st.table({
        "Model": ["tiny", "base", "small", "medium", "large", "turbo"],
        "Relative Speed": ["10x", "7x", "4x", "2x", "1x", "8x"],
        "VRAM": ["~1GB", "~1GB", "~2GB", "~5GB", "~10GB", "~6GB"],
        "Best Use Case": ["Lower accuracy", "Typical usage", "Standard everyday transcription", "High-quality needs; Heavy accents; Higher accuracy for multi-lingual", "Maximum accuracy; Complex & technical terminology; Translation", "accuracy = large; speed = tiny"],
        "English-only Version": ["tiny.en", "base.en", "small.en", "medium.en", "Multilingual only", "Multilingual only"]
    })

# remove downloaded model
with st.expander("Remove Downloaded Model"):
    downloaded_model = st.selectbox(
            "Downloaded Model(s) :",
            [i for i in transcriber.get_loaded_model()],
            help = "These are the downloaded model(s) on your computer"
    )
    st.write(f"Location : `{transcriber.model_location}`")
    
    if downloaded_model:
        
        if st.button(f"Delete {downloaded_model}"):
            transcriber.remove_loaded_model(downloaded_model[:-3])
            st.info(f"Removed {downloaded_model}")

# advanced settings
st.subheader("3. Settings")

language = st.selectbox(
        "Language",
        [i for i in transcriber.get_available_language()] + [(None, "auto detect")],
        help = "Main language of the audio's speech"
)

with st.expander("Advanced Settings"):
    
    initial_prompt = st.toggle(
            "Initial Prompt",
            value = True,
            help = "To tailor transcription process : spelling technical vocabulary, enforcing formatting and punctuation, fixing capitalization styles, etc."
    )
    
    if initial_prompt:
        initial_prompt = st.selectbox(
                "",
                label_visibility = "collapsed",
                options = [
                    "Hello, welcome to our presentation. 你好，歡迎來到我們的演講。 Today we will discuss the project. 今天我們將討論這個項目。",  # english and chinese back and forth
                    "Hello, this audio contains both English and 中文 text.",  # occasionally contain chinese
                ],
                index = 0,
                accept_new_options = True,
                placeholder = "Select or type here . . ."
        )
        
    else:
        initial_prompt = None
    
    condition_on_previous_text = st.toggle(
            "Condition on Previous Text",
            value = True,
            help = "True : use previous transcript as context for next 30s;  \nFalse : transcribe independently without acknowledging previous step"
    )
    temperature = st.toggle(
            "Temperature",
            value = False,
            help = "Randomness and creativity of the model's transcription generation.  \n0 = deterministic, no hallucinations;  \n1 = creative"
    )
    
    if temperature:
        temperature = st.number_input(
                "",
                label_visibility = "collapsed",
                min_value = 0.0,
                max_value = 1.0,
                step = 0.1,
                value = 0.0,
                placeholder = "Randomness and creativity of the model's transcription generation.",
                format = "%.2f"
        )
        
    else:
        temperature = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
    
    no_speech_threshold = st.number_input(
            "No Speech Threshold",
            min_value = 0.0,
            max_value = 1.0,
            step = 0.1,
            value = 0.6,
            help = "How sensitive the model is to silence.  \n0 = sensitive to silence and skip segment;  \n1 = sensitive to speech and keep segment;  \nLower value (0.3) for duo-lingual audio",
            placeholder = "How sensitive the model is to silence.",
            format = "%.2f"
    )
    include_timestamp = st.toggle("Include Timestamp", value = False)
    encoding = st.selectbox(
            "Encoding",
            ["utf-8", "utf-16", "big5"],
            help = "Indicate how text is encoded in the output text file"
    )

# transcribe process
st.subheader("4. Transcribe Audio")
st.caption("Credit to Whisper by OpenAI")

if st.button("Transcribe"):
    
    if file is not None:
        extension = file.name[file.name.index("."):]
        
        # create temporary file to store uploaded file bytes
        with tempfile.NamedTemporaryFile(delete = False, suffix = extension) as temp_file:
            temp_file.write(file.getvalue())
            temp_file_path = temp_file.name
        
        # output file download location
        output_file_location = str(Path(os.path.expanduser("~")) / "Downloads")
        
        # transcribe
        with st.spinner("Transcribing audio . . . this may take a few minutes . . ."):
            result = transcriber.transcribe(
                    temp_file_path,
                    model,
                    language = language[0],
                    initial_prompt = initial_prompt,
                    condition_on_previous_text = condition_on_previous_text,
                    temperature = temperature,
                    no_speech_threshold = no_speech_threshold
            )
            text = transcriber.format_transcribed_text(result, include_timestamp = include_timestamp)
            transcriber.write_file(text, output_file_location + "\\" + file.name[:file.name.index(".")], encoding = encoding)
        
        st.subheader("5. Done !")
        st.success(f"Check `{output_file_location}` for the transcription !")
        
        # clean up
        os.remove(temp_file_path)
        
        for root, dirs, files in os.walk(os.getcwd()):
            
            if "__pycache__" in dirs:
                cache_path = os.path.join(root, "__pycache__")
                # print(f"Removing : {cache_path}")
                shutil.rmtree(cache_path)
        
    else:
        st.info("Please upload an audio file")


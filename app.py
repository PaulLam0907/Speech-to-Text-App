import os
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
model = st.selectbox(
        "Choose a model :",
        ["tiny", "base", "small", "medium", "large", "turbo"],
        index = 2,
        help = "This model is used to transcribe your audio"
)

# info for choosing suitable model
with st.popover("How to choose the suitable model ?"):
    st.markdown("#### How to choose the suitable model ?")
    st.write("Choose the model according to your needs")
    st.table({
        "Model": ["tiny", "base", "small", "medium", "large", "turbo"],
        "Relative Speed": ["10x", "7x", "4x", "2x", "1x", "8x"],
        "VRAM": ["~1GB", "~1GB", "~2GB", "~5GB", "~10GB", "~6GB"],
        "Best Use Case": ["Lower accuracy", "Typical usage", "Standard everyday transcription; Higher accuracy for multi-lingual", "High-quality needs; Heavy accents; Higher accuracy for multi-lingual", "Maximum accuracy; Complex & technical terminology; Translation", "accuracy = large; speed = tiny"],
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
        [i for i in transcriber.get_available_language()],
        help = "Main language of the audio's speech"
)

with st.expander("Advanced Settings"):
    initial_prompt = st.text_input(
            "Initial Prompt",
            value = "Hello, this audio contains both English and 中文 text.",  # occasionally contain chinese
            help = "To tailor transcription process : spelling technical vocabulary, enforcing formatting and punctuation, fixing capitalization styles, etc."
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
            result = transcriber.transcribe(temp_file_path, model, language = language[0], initial_prompt = initial_prompt)
            text = transcriber.format_transcribed_text(result, include_timestamp = include_timestamp)
            transcriber.write_file(text, output_file_location + "\\" + file.name[:file.name.index(".")], encoding = encoding)
        
        st.subheader("5. Done !")
        st.success(f"Check `{output_file_location}` for the transcription !")
        
        os.remove(temp_file_path)
        
    else:
        st.info("Please upload an audio file")


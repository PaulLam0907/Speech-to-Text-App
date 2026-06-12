"""
main.py

Python script to launch streamlit app
"""
import os
import sys
from streamlit.web import cli

"""
to run streamlit app.py :
streamlit run app.py

clear cache in streamlit :
streamlit cache clear

to build .exe using cx_Freeze :
copy ffmpeg.exe to same dir as app.py :
python setup.py build

to git push large file :
install git at git-scm.com
create .gitignore manually to exclude venv :
git config user.email "paullam97@gmail.com"
git config user.name "Paul Lam"
git init
git remote add origin https://github.com/PaulLam0907/Speech-to-Text-App
git remote set-url origin https://github.com/PaulLam0907/Speech-to-Text-App
git remote -v
git pull origin main --allow-unrelated-histories
git lfs install
git lfs track "build/**/*"
git add .gitattributes
git commit -m "Upload build"
git push -u origin main
"""

# import subprocess
#
# result = subprocess.run(
#         ["streamlit", "run", "C:\\Python\\SpeechToText\\app.py"],
#         shell = True,
#         capture_output = True,
#         text = True
# )
# print(result.stdout)

if __name__ == "__main__":
    
    try:
        # Robustly identify the folder where the compiled application is executing
        if getattr(sys, "frozen", False):
            self_dir = os.path.dirname(sys.executable)
            
        else:
            self_dir = os.path.dirname(os.path.realpath(__file__))
        
        app_location_path = os.path.join(self_dir, "app.py")
        sys.argv = [
            "streamlit",
            "run",
            app_location_path,
            "--global.developmentMode=false"
        ]
        sys.exit(cli.main())
        
    except Exception as e:
        print(e)
        input("Press \"Enter\" to exit : ")
        

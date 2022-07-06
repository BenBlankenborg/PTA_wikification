# Project Text Analysis: Wikification
The repository made for sharing the code and communicating on final project for Project Text Analysis.

## Programs explanation
The repository contains two versions of the wikificator: `wikification_UI.py` and `wikifcation.py`. Both programs produce an .ent file as output, containing a .pos file data with added relevant named entities and wikipedia links on corresponding tokens. 

### Pre-downloaded packages
Before using the programs some additional libraries must be downloaded:  
- Packages for wikification.py:  
  - spacy: `pip install -U spacy`
  - Necessary spacy pipeline: `python3 -m spacy download en_core_web_sm`
  - NLTK: `pip install --user -U nltk`
  
- Packages for wikification_UI.py (aside from packages above):  
  - StreamLit: `pip3 install streamlit`
  - Jinja2: `sudo apt-get install -y python-jinja2`
  
### Running the programs
To run the `wikification.py` please use the following command:
```
python3 wikification.py <dev/test directory> <direcotory_name>
```
To run the `wikification_UI.py` please use the following command:
```
streamlit run wikification_UI.py
```

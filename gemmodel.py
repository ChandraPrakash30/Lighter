import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("AIzaSyBr86XCTw_3XWGW34KLEYFFSEKL1Owlr-Y"))

for model in genai.list_models():
    print(model.name)


import os
class Params :
    api_key  = os.getenv("OPENAI_API_KEY")
    save_path = r"/"
    appname = ""
    click_idx = 0
    pic_index = 1
    last_step = ""
    start = True
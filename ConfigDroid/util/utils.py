import os
import re
import subprocess
import time
import openai
import cv2
from Params import *
from loguru import logger
import json
from ConfigDroid.util.Adb import *

class Utils:
    
    def __init__(self):
        pass

    @staticmethod
    def subprocess_getoutput(stmt):
        result = subprocess.getoutput(stmt)
        print(result)
        return result

    @staticmethod
    def go_back():
        print(f"run command: {Adb_command.go_back}")
        os.system(Adb_command.go_back)

    @staticmethod
    def get_running_info():
        res = Utils.subprocess_getoutput(Adb_command.running_info)
        real_res = res.split('\n')[0].strip()
        p1 = re.compile(r'[{](.*?)[}]', re.S)
        arr = re.findall(p1, real_res)
        print(arr)
        final_ans = arr[0].split()[-2].split('/')
        if len(final_ans) < 2:
            return
        app_name, activity_name = final_ans
        return {'app': app_name, 'activity': activity_name}

    @staticmethod
    def screen_shot(index: int, bounds):
        os.system(Adb_command.screen_shot.format(index=index))
        os.system(Adb_command.pull_sreen_shot.format(index=index, save_path=Params.save_path))
        image = cv2.imread(f"{Params.save_path}screenshot-{index}.png")
        cv2.rectangle(image, (bounds[0], bounds[1]), (bounds[2], bounds[3]), (0, 0, 255), 4)
        cv2.imwrite(f"{Params.save_path}screenshot-{index}.png", image)

    @staticmethod
    def screen_shot_end(index: int):
        os.system(Adb_command.screen_shot.format(index=index))
        os.system(Adb_command.pull_sreen_shot.format(index=index, save_path=Params.save_path))

    @staticmethod
    def long_click(text_name: str, all_components: list):
        time.sleep(0.5)
        global pic_index
        is_clicked = False
        for component in all_components:
            if component['desc'] == text_name:
                bounds = component['bounds']
                res = Utils.get_bounds(bounds)
                Utils.screen_shot(pic_index, res)
                pic_index += 1
                cmd = f"adb shell input swipe {str((res[0] + res[2]) / 2)} {str((res[1] + res[3]) / 2)} {str((res[0] + res[2]) / 2 + 1)} {str((res[1] + res[3]) / 2 + 1)} 500"
                print(f"run command: {cmd}")
                os.system(cmd)
                is_clicked = True
                break
        print(f"{text_name} is clicked." if is_clicked else f"{text_name} is not found.")

    @staticmethod
    def click(text_name: str, all_components: list):
        time.sleep(0.5)
        global pic_index
        is_clicked = False
        for component in all_components:
            if component['@desc'] == text_name:
                bounds = component['@bounds']
                res = Utils.get_bounds(bounds)
                Utils.screen_shot(pic_index, res)
                pic_index += 1
                cmd = f"adb shell input tap {str((res[0] + res[2]) / 2)} {str((res[1] + res[3]) / 2)}"
                print(f"run command: {cmd}")
                os.system(cmd)
                is_clicked = True
                break
        print(f"{text_name} is clicked." if is_clicked else f"{text_name} is not found.")

    @staticmethod
    def split_page(all_components: list):
        size_str = Utils.subprocess_getoutput(Adb_command.wm_size).split(' ')[-1].split('x')
        width, height = int(size_str[0]), int(size_str[1])

        up_half, down_half = [], []

        for component in all_components:
            bounds = component['@bounds']
            res = Utils.get_bounds(bounds)
            y = (res[1] + res[3]) / 2
            if y < height / 2:
                up_half.append(component)
            else:
                down_half.append(component)

        return up_half, down_half

    @staticmethod
    def getAllComponents(jsondata: dict):
        root = jsondata['hierarchy']
        queue = [root]
        res = []
        node_cnt = 0
        while queue:
            currentNode = queue.pop(0)
            if ('@resource-id' in currentNode and 'com.android.systemui' in currentNode['@resource-id']) or ('@package' in currentNode and 'com.android.systemui' in currentNode['@package']):
                continue
            node_cnt += 1
            if 'node' in currentNode:
                if '@clickable' in currentNode and currentNode['@clickable'] == 'true':
                    if isinstance(currentNode['node'], dict):
                        currentNode['node']['@clickable'] = 'true'
                    else:
                        for e in currentNode['node']:
                            e['@clickable'] = 'true'
                if isinstance(currentNode['node'], dict):
                    queue.append(currentNode['node'])
                else:
                    for e in currentNode['node']:
                        queue.append(e)
            else:
                res.append(currentNode)
        return res

    @staticmethod
    def input_text(content: str, bounds):
        global pic_index
        res = Utils.get_bounds(bounds)
        Utils.screen_shot(pic_index, res)
        pic_index += 1

        cmd = f"adb shell input tap {str((res[0] + res[2]) / 2)} {str((res[1] + res[3]) / 2)}"
        print(f"run command: {cmd}")
        os.system(cmd)

        content = content.replace(' ', '\ ')
        cmd = f"adb shell input text {content}"
        os.system(cmd)

    @staticmethod
    def getOutput(question: str):
        openai.api_key = Params.api_key
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=question,
            temperature=0.5,
            max_tokens=50,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n"]
        )
        return response.choices[0].text

    @staticmethod
    def get_bounds(bounds):
        res = []
        bounds = bounds.split(',')
        res.append(bounds[0].replace('[', ''))
        mid = bounds[1].split('][')
        res.append(mid[0])
        res.append(mid[1])
        res.append(bounds[2].replace(']', ''))
        return [int(e) for e in res]

    @staticmethod
    def find_all_describable_components(all_components: list):
        components_list = []
        for component in all_components:
            info = Utils.get_common_desc(component)
            desc = info['desc']
            if desc:
                component['@desc'] = desc
                components_list.append(component)
        return components_list

    @staticmethod
    def find_all_clickable_components(components_list: list):
        return [{"desc": e["@desc"], "bounds": e["@bounds"]} for e in components_list if e.get('@clickable') == 'true']

    @staticmethod
    def find_all_editable_components(components_list: list):
        return [e for e in components_list if e.get('@class') in ['android.widget.EditText', 'android.widget.AutoCompleteTextView']]

    @staticmethod
    def find_all_widgets(components_list: list):
        widget_list = []
        for component in components_list:
            widget = {
                "WidgetC": component["@class"].split(".")[-1],
                "widgetID": component["@desc"] if not component["@text"] and not component["@content-desc"] else "",
                "widgetT": component["@desc"] if component["@text"] or component["@content-desc"] else "",
                "WidgetAct": "Click" if component.get('@clickable') == 'true' else "none",
                "WidgetV": "0"
            }
            widget_list.append(widget)
        return widget_list

    @staticmethod
    def write_to_json(jsondata, activity_name, components_list, up_half, down_half, widget_list, step):
        jsondata["Page information attribute"] = [{
            "ActivityName": activity_name,
            "Widgets": [e["@desc"] for e in components_list],
            "Layouts": [
                {
                    "Upper half": up_half,
                    "Lower half": down_half
                }
            ]
        }]
        jsondata["Widget information attribute"] = [{}]
        for i, widget in enumerate(widget_list):
            jsondata["Widget information attribute"][0][f"Widget_{i + 1}"] = [widget]

        print("json data:")
        print(jsondata)

        with open(f'./json/{Params.appname}-step{step + 1}.json', 'w') as f:
            json.dump(jsondata, f)

    @staticmethod
    def process_after_gpt(chat_res: str, components_list: list):
        last_step = ""
        if "click" in chat_res.lower():
            target = Utils.get_quote(chat_res)[0]
            Utils.click(target, components_list)
            last_step = f'click "{target}"'

        if "return to previous page" in chat_res.lower():
            Utils.go_back()
            last_step = "return to previous page"
        return last_step

    @staticmethod
    def build_graph(new_running_info: str, is_start: int, activity_name: str, res: str):
        new_activity_name = new_running_info['activity'].replace('.', ' ').split(' ')[-1].replace('Activit', '')
        logger.info(f"new activity_name: {new_activity_name}")

        graph_file_path = f'./graph/{Params.appname}.txt'
        if is_start:
            with open(graph_file_path, 'w', encoding='utf-8'):
                pass

        if not os.path.exists(graph_file_path):
            with open(graph_file_path, 'w', encoding='utf-8'):
                pass

        with open(graph_file_path, 'r', encoding='utf-8') as g_file:
            lines = len(g_file.readlines())

        with open(graph_file_path, 'a', encoding='utf-8') as g_file:
            g_file.write(f"Step {lines + 1}: {activity_name} <- {res} -> {new_activity_name}\n")

    @staticmethod
    def rename_duplicate(alist):
        return [v + str(alist[:i].count(v) + 1) if alist.count(v) > 1 else v for i, v in enumerate(alist)]

    @staticmethod
    def get_common_desc(e: dict):
        text, content, rid, bounds = e['@text'], e['@content-desc'], e['@resource-id'], e['@bounds']
        desc = text or content or rid.split('/')[-1].replace('_', ' ') if rid else ""
        return {"desc": desc, "bounds": bounds}

    @staticmethod
    def get_quote(content: str):
        return re.findall(r'["](.*?)["]', content)

    @staticmethod
    def generate_next_step_prompt(json_data: dict, activity_name: str, clickable_list: list):
        prompt = f"We want to test the {Params.appname} App, which has {len(json_data['Global information attribute'][0]['Activities'])} main function pages, namely: "
        prompt += ', '.join([f'"{e}"' for e in json_data["Global information attribute"][0]["Activities"]])
        prompt += f'.\nThe past test sequence is: '
        prompt += ', '.join([f'"{e}"' for e in json_data["Global information attribute"][0]["Priority"]])
        prompt += f'.\nThe function UI page we are currently testing is "{activity_name}".\n'
        prompt += "Now we can do these:\n"

        for opt_id, e in enumerate(clickable_list, start=1):
            prompt += f'{opt_id}. click "{e["desc"]}"\n'
        prompt += f"{len(clickable_list) + 1}. return to previous page\n"
        prompt += '.\nThere are some defects in the previous test path, please check them out and choose what to do next? Please answer directly with one of the options.\n'
        logger.info(prompt)
        return prompt

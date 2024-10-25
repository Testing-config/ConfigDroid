import json
from pprint import pprint
import xmltodict
from ConfigDroid.util.utils import Utils
import uiautomator2 as u2
from loguru import logger
from Params import Params
from Prompts import Prompts

class Executor:
    last_step = ""
    start = False

    @staticmethod
    def execute(is_start: bool, step: int):
        logger.info("A new turn ...")

        Executor.start = False

        # Refresh the page
        logger.info('Reloading the page...')
        
        # Connect to the device
        d = u2.connect()
        logger.info(d.info)
        
        # Get the UI tree file and save it
        page_source = d.dump_hierarchy(compressed=True, pretty=True)
        with open(Params.save_path + 'hierarchy.xml', 'w', encoding='utf-8') as xml_file:
            xml_file.write(page_source)

        # Convert XML to JSON
        with open(Params.save_path + 'hierarchy.xml', 'r', encoding='utf-8') as xml_file:
            logger.info('Reading hierarchy tree XML file...')
            data_dict = xmltodict.parse(xml_file.read())
            data_str = json.dumps(data_dict)
            with open(Params.save_path + 'hierarchy.json', 'w', encoding='utf-8') as json_file:
                json_file.write(data_str)

        # Get all components
        all_components = Utils.getAllComponents(data_dict)
        logger.info(f"There are {len(all_components)} components on the current page.")
        running_info = Utils.get_running_info()

        # Extract ActivityName
        activity_name = running_info['activity'].replace('.', ' ').split(' ')[-1].replace('Activit', '')
        logger.info(f"Activity name: {activity_name}")

        # Process JSON information
        if not is_start:
            with open(f'./json/{Params.appname}.json', 'r') as jsonfile:
                jsondata = json.load(jsonfile)
            logger.info(jsondata)
        else:
            jsondata = {
                "Global information attribute": [{
                    "App name": Params.appname,
                    "Activities": [activity_name],
                    "Priority": [f'1_{activity_name}']
                }]
            }

        logger.info('Searching for describable components...')
        components_list = Utils.find_all_describable_components(all_components)
        origin_list = [e["@desc"] for e in components_list]
        renamed_list = Utils.rename_duplicate(origin_list)
        for i, e in enumerate(renamed_list):
            components_list[i]["@desc"] = e

        logger.info('Searching for clickable components...')
        clickable_list = Utils.find_all_clickable_components(components_list)

        logger.info('Searching for editable components...')
        edit_list = Utils.find_all_editable_components(components_list)

        up_half, down_half = Utils.split_page(components_list)

        up_half = [e["@desc"] for e in up_half]
        down_half = [e["@desc"] for e in down_half]

        logger.info(f"Up half: {up_half}")
        logger.info(f"Down half: {down_half}")

        # Include WidgetC, WidgetID/WidgetT, WidgetAct, WidgetV
        widget_list = Utils.find_all_widgets(components_list)

        Utils.write_to_json(jsondata, activity_name, components_list, up_half, down_half, widget_list, step)

        prompt = Utils.generate_next_step_prompt(jsondata, activity_name, clickable_list)

        res = Utils.getOutput(Prompts.few_shot + prompt)

        logger.info(f"The ChatGPT output is: {res}")

        Executor.last_step = Utils.process_after_gpt(res, components_list)

        logger.info(Executor.last_step)

        new_running_info = Utils.get_running_info()

        Utils.build_graph(new_running_info, is_start, activity_name, res)

        is_start = False

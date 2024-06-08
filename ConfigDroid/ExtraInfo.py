import openai
import json
import os
from ConfigDroid.util.utils import Util

class ExtractionOfApp:
    # Initialization function
    def __init__(self, app_name, app_node_path, app_edge_path):
        self.Pattern_Of_Test_Path = "{}. At the time<{}>, In the page of <{}>, we do the operation <{}>, and the next page is <{}>."
        self.app_name = app_name
        self.app_node_path = app_node_path
        self.app_edge_path = app_edge_path
        # Create directory if it doesn't exist
        if not os.path.exists('./' + app_name):
            os.makedirs('./' + app_name)
        self.node_candidates = {}
            
    # Get all JSON file names in a folder
    def openJsonWithSub(self, isNode):
        folder_path = self.app_node_path if isNode else self.app_edge_path
        # Get all JSON file names in the folder
        json_files = [file for file in os.listdir(folder_path) if file.endswith('.json')]
        # Get full paths of all JSON files
        json_file_paths = [os.path.join(folder_path, file) for file in json_files]
        return json_file_paths
    
    # Extract UTG information for nodes
    def extractionOfNode(self):
        # node_info format: {state_id: {}}
        node_info = {}
        pop_keys = ['views', 'width', 'height', 'background_services']
        json_file_paths = self.openJsonWithSub(True)
        
        for json_path in json_file_paths:
            with open(json_path, 'r', encoding='utf-8') as f:
                content = f.read()
                msgs = json.loads(content) if content else {}
                # Remove unnecessary keys
                for pop_key in pop_keys:
                    msgs.pop(pop_key, None)
                # Update the name value
                msgs['foreground_activity'] = msgs['foreground_activity'].split('.')[-1]
                node_info[msgs['state_str']] = msgs
        
        print(len(node_info))
        with open(f'./{self.app_name}/node_info.json', 'w', encoding='utf-8') as f:
            json.dump(node_info, f, indent=4, ensure_ascii=False, sort_keys=True)
        return node_info
    
    # Extract UTG information for edges
    def extractionOfEdge(self):
        # edge_info format: {state_id: {}}
        edge_info = {}
        json_file_paths = self.openJsonWithSub(False)
        
        for json_path in json_file_paths:
            with open(json_path, 'r', encoding='utf-8') as f:
                content = f.read()
                msgs = json.loads(content) if content else {}
            # Extract edge information
            event_desc = msgs['event']['event_type']
            if 'view' in msgs['event']:
                if 'class' in msgs['event']['view']:
                    event_desc += f" <{msgs['event']['view']['class'].split('.')[-1]}>"
                if 'text' in msgs['event']['view'] and msgs['event']['view']['text']:
                    event_desc += f" <{msgs['event']['view']['text']}>"
            msgs['event_desc'] = event_desc
            edge_info[f"{msgs['tag']}  {msgs['start_state']}  {msgs['stop_state']}"] = msgs
        
        print(len(edge_info))
        with open(f'./{self.app_name}/edge_info.json', 'w', encoding='utf-8') as f:
            json.dump(edge_info, f, indent=4, ensure_ascii=False, sort_keys=True)
        return
    
    # Extract test path information
    def extractionOfTestPath(self):
        # test_path_info format: {state_id: {}}
        test_path_info = {}
        
        with open(f'./{self.app_name}/node_info.json', 'r', encoding='utf-8') as f:
            content = f.read()
            node_info = json.loads(content) if content else {}
            
        with open(f'./{self.app_name}/edge_info.json', 'r', encoding='utf-8') as f:
            content = f.read()
            edge_info = json.loads(content) if content else {}
        
        cnt = 1
        test_path_list = []
        # Iterate through key-value pairs
        for key, value in edge_info.items():
            words = key.split()
            time = words[0]
            if words[1] not in node_info or words[2] not in node_info:
                print(words[1], words[2])
                continue
            startNode = node_info[words[1]]['foreground_activity']
            endNode = node_info[words[2]]['foreground_activity']
            # Generate path
            test_path_list.append(self.Pattern_Of_Test_Path.format(cnt, time, startNode, value['event_desc'], endNode))
            cnt += 1
        
        print(test_path_list)
        print(len(test_path_list))
        
        with open(f'./{self.app_name}/test_path_info.txt', 'w', encoding='utf-8') as f:
            for item in test_path_list:
                f.write(item + '\n')

    # Generate node candidates using ChatGPT
    def generate_node_candidates_with_chatgpt(self, api_key):
        openai.api_key = api_key
        node_info = self.extractionOfNode()
        
        for state_id, node in node_info.items():
            # Prepare the prompt for ChatGPT
            prompt = f"Given the following node information, generate a list of candidate actions or views: {json.dumps(node)}"
            response = Util.getOutput(prompt)
            # Parse the response from ChatGPT
            candidates = response.choices[0].text.strip().split('\n')
            self.node_candidates[state_id] = candidates
        
        print("Node candidates generated with ChatGPT:", self.node_candidates)

def adb_connect():
    # Placeholder function to simulate ADB connection
    print("Connecting to app via ADB...")

if __name__ == '__main__':
    api_key = "your_openai_api_key_here"  # Replace with your actual OpenAI API key
    e = ExtractionOfApp(
        "Saviry3",
        "/Users/chexing/Documents/学习/科研/自动化测试-功能性测试/测试数据/结果/droidBot/Saviry3/states",
        "/Users/chexing/Documents/学习/科研/自动化测试-功能性测试/测试数据/结果/droidBot/Saviry3/events"
    )
    e.generate_node_candidates_with_chatgpt(api_key)
    adb_connect()
    e.extractionOfEdge()
    e.extractionOfTestPath()

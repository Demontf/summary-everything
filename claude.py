from datetime import datetime
import json
from anthropic import Anthropic

from tools import split_array, save_obj_json
from config import MODEL_CONFIGS, SYSTEM_PROMPTS, TASK_PROMPTS

def call_claude(prompt: str, data: str) -> str:
    config = MODEL_CONFIGS["claude"]
    client = Anthropic(api_key=config.api_key)
    
    print('start to call Claude with data:')
    print(data)
    
    message = client.messages.create(
        model=config.model_name,
        system=SYSTEM_PROMPTS["paper_summary"]["claude"],
        messages=[{
            'role': 'user',
            'content': prompt + data
        }]
    )
    return message.content[0].text

def summary_papers_claude(papers):
    page_size = 15  # Claude has higher token limits than Qwen
    papers_list = split_array(papers, page_size)
    result = []
    idx = 0
    
    for paper in papers_list:
        if len(paper) == 0:
            break
            
        prompt = TASK_PROMPTS["paper_summary"]["claude"]
        response = call_claude(prompt, json.dumps(paper))
        
        try:
            ret_summary = json.loads(response)
        except Exception as e:
            print(f"parse Claude response failed: {e}")
            print(response)
        else:
            print(f"call Claude success, got {len(paper)} paper summaries")
            save_obj_json(f"./log/{datetime.now().strftime('%Y-%m-%d')}/{idx}.json", ret_summary)
            result.append(ret_summary)
            idx += 1
            
    save_obj_json(f"./log/{datetime.now().strftime('%Y-%m-%d')}/summary.json", result)
    return result
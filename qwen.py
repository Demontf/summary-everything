from datetime import datetime


from openai import OpenAI
import json

from tools import split_array, save_obj_json

qwen_model = "qwen-long"  # qwen-turbo-latest
papers_prompt = '请用一句话总结论文研究的问题，采用的方法，提出的观点，效果如何以及有什么价值。返回格式[{"title":"","one":"","id":""}],不要多余字符，要所有论文的一句话中文总结(one),论文题目(title)编号(id),id和title保持和原数据的对应关系，数据如下：'


def call_qwen(prompt, model, data):
    client = OpenAI(
        api_key='',
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    print('start to call Qwen with data:')
    print(data)

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': '你是一个文献整理和分析总结专家'},
            {'role': 'user', 'content': prompt + data}
        ],
    )
    return completion.choices[0].message.content


def summary_papers(papers):
    page_size = 10  # 大了qianwen可能限流，也不能太小，qps是限制100，短时间不能请求多次
    papers_list = split_array(papers, 10)
    result = []
    idx = 0
    for paper in papers_list:
        if len(paper) == 0:
            break
        response = call_qwen(papers_prompt, qwen_model, json.dumps(paper)).replace('```json', '').replace('```',
                                                                                                          '').strip()
        try:
            ret_summary = json.loads(response)
        except:
            print(f"parse Qwen response failed: {e}")
            print(response)
        else:
            print(f"call Qwen success, get {len(paper)} paper summary")
            save_obj_json("./log/" + datetime.now().strftime("%Y-%m-%d") + "/" + str(idx) + ".json", ret_summary)
            result.append(ret_summary)
            idx += 1
    save_obj_json("./log/" + datetime.now().strftime("%Y-%m-%d") + "/summary.json", result)
    return result

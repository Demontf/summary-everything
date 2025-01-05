from datetime import datetime
import json
import os
from typing import List, Dict, Any, Optional

from litellm import completion
from litellm.exceptions import LiteLLMException

from tools import split_array, save_obj_json

class LLMConfig:
    def __init__(
        self,
        model_name: str,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        max_batch_size: int = 10,
        system_prompt: str = "",
        task_prompt: str = "",
    ):
        self.model_name = model_name
        self.api_base = api_base
        self.api_key = api_key
        self.max_batch_size = max_batch_size
        self.system_prompt = system_prompt
        self.task_prompt = task_prompt

class LLMManager:
    # Default configurations for supported models
    MODEL_CONFIGS = {
        "qwen": LLMConfig(
            model_name="qwen/qwen-long",  # LiteLLM format for Qwen
            api_base="https://dashscope.aliyuncs.com/api/v1",
            max_batch_size=10,
            system_prompt="你是一个文献整理和分析总结专家",
            task_prompt='请用一句话总结论文研究的问题，采用的方法，提出的观点，效果如何以及有什么价值。返回格式[{"title":"","one":"","id":""}],不要多余字符，要所有论文的一句话中文总结(one),论文题目(title)编号(id),id和title保持和原数据的对应关系，数据如下：'
        ),
        "claude": LLMConfig(
            model_name="anthropic/claude-3-sonnet-20240229",  # LiteLLM format for Claude
            max_batch_size=15,
            system_prompt="You are an expert at analyzing and summarizing academic papers. Please provide concise and accurate summaries.",
            task_prompt='Please summarize each paper in one sentence, covering the research problem, methodology, key findings, results, and significance. Return the summary in the following JSON format: [{"title":"","one":"","id":""}]. Include all papers with their one-sentence summaries (one), paper titles (title), and IDs (id). Maintain the original ID and title mapping. Here are the papers:'
        ),
        # Add more models here as needed
    }

    def __init__(self, model_type: str = None):
        """Initialize the LLM manager with a specific model type."""
        self.model_type = model_type or os.getenv("SUMMARY_MODEL_TYPE", "qwen")
        if self.model_type not in self.MODEL_CONFIGS:
            raise ValueError(f"Unsupported model type: {self.model_type}")
        
        self.config = self.MODEL_CONFIGS[self.model_type]
        
        # Set API key from environment if not in config
        if not self.config.api_key:
            if self.model_type == "qwen":
                self.config.api_key = os.getenv("QWEN_API_KEY", "")
            elif self.model_type == "claude":
                self.config.api_key = os.getenv("ANTHROPIC_API_KEY", "")

    def call_model(self, data: str) -> str:
        """Call the LLM model with the given data."""
        try:
            print(f'Calling {self.model_type} with data:')
            print(data)
            
            response = completion(
                model=self.config.model_name,
                messages=[
                    {"role": "system", "content": self.config.system_prompt},
                    {"role": "user", "content": self.config.task_prompt + data}
                ],
                api_base=self.config.api_base,
                api_key=self.config.api_key
            )
            
            return response.choices[0].message.content
            
        except LiteLLMException as e:
            print(f"Error calling {self.model_type}: {str(e)}")
            raise

    def summary_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Summarize a list of papers using the configured LLM."""
        papers_list = split_array(papers, self.config.max_batch_size)
        result = []
        idx = 0
        
        for paper_batch in papers_list:
            if not paper_batch:
                break
                
            response = self.call_model(json.dumps(paper_batch))
            
            try:
                ret_summary = json.loads(response)
            except json.JSONDecodeError as e:
                print(f"Failed to parse {self.model_type} response: {e}")
                print(f"Raw response: {response}")
                continue
                
            print(f"Successfully summarized {len(paper_batch)} papers")
            save_obj_json(f"./log/{datetime.now().strftime('%Y-%m-%d')}/{idx}.json", ret_summary)
            result.append(ret_summary)
            idx += 1
            
        save_obj_json(f"./log/{datetime.now().strftime('%Y-%m-%d')}/summary.json", result)
        return result
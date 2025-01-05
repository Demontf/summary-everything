from typing import Dict, Any

class ModelConfig:
    def __init__(self, model_type: str, model_name: str, api_base: str = None, api_key: str = None):
        self.model_type = model_type
        self.model_name = model_name
        self.api_base = api_base
        self.api_key = api_key

# Default configurations for supported models
MODEL_CONFIGS: Dict[str, ModelConfig] = {
    "qwen": ModelConfig(
        model_type="qwen",
        model_name="qwen-long",
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=""  # Set via environment variable
    ),
    "claude": ModelConfig(
        model_type="claude",
        model_name="claude-3-sonnet-20240229",
        api_key=""  # Set via environment variable
    )
}

# System prompts for different tasks
SYSTEM_PROMPTS = {
    "paper_summary": {
        "qwen": "你是一个文献整理和分析总结专家",
        "claude": "You are an expert at analyzing and summarizing academic papers. Please provide concise and accurate summaries."
    }
}

# Task prompts
TASK_PROMPTS = {
    "paper_summary": {
        "qwen": '请用一句话总结论文研究的问题，采用的方法，提出的观点，效果如何以及有什么价值。返回格式[{"title":"","one":"","id":""}],不要多余字符，要所有论文的一句话中文总结(one),论文题目(title)编号(id),id和title保持和原数据的对应关系，数据如下：',
        "claude": 'Please summarize each paper in one sentence, covering the research problem, methodology, key findings, results, and significance. Return the summary in the following JSON format: [{"title":"","one":"","id":""}]. Include all papers with their one-sentence summaries (one), paper titles (title), and IDs (id). Maintain the original ID and title mapping. Here are the papers:'
    }
}
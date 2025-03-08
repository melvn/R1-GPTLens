import time
import os
from openai import OpenAI

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
completion_tokens = 0
prompt_tokens = 0

# Initialize Deepseek client
deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def gpt(prompt, model, temperature=0.7, max_tokens=4000, n=1, stop=None) -> list:
    messages = [{"role": "user", "content": prompt}]
    return chatgpt(messages, model=model, temperature=temperature, max_tokens=max_tokens, n=n, stop=stop)

def chatgpt(messages, model, temperature=0.0, max_tokens=4000, n=1, stop=None) -> list:
    global completion_tokens, prompt_tokens
    outputs = []

    #mapping model name if its r1
    if model == "deepseek-r1":
        model = "deepseek-reasoner"
    
    while n > 0:
        batch_size = min(n, 20)
        n -= batch_size
        
        res = deepseek_client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            stop=stop
        )
        
        outputs.append(res.choices[0].message.content)
        
        completion_tokens += res.usage.completion_tokens
        prompt_tokens += res.usage.prompt_tokens
    
    return outputs

def gpt_usage(backend="deepseek-r1"):
    global completion_tokens, prompt_tokens
    # Deepseek Reasoner pricing (standard rate), not off peak discount rates. 
    # Input: $0.55 per 1M tokens
    # Output: $2.19 per 1M tokens
    input_cost = prompt_tokens / 1000000 * 0.55
    output_cost = completion_tokens / 1000000 * 2.19
    cost = input_cost + output_cost
    return {"completion_tokens": completion_tokens, "prompt_tokens": prompt_tokens, "cost": cost}
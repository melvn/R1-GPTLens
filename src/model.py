import time
import os
from openai import OpenAI

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
completion_tokens = 0
prompt_tokens = 0

# Initialize Deepseek client
deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def gpt(prompt, model, temperature=0.7, max_tokens=4000, n=1, stop=None) -> list:
    messages = [{"role": "user", "content": prompt}]
    return chatgpt(messages, model=model, temperature=temperature, max_tokens=max_tokens, n=n, stop=stop)

def chatgpt(messages, model, temperature=0.0, max_tokens=4000, n=1, stop=None) -> list:
    global completion_tokens, prompt_tokens
    outputs = []

    # Check which client to use based on model name
    # OpenAI models start with "gpt-", while Deepseek models don't
    if model.startswith("gpt-"):
        client = openai_client
    else:
        client = deepseek_client
        #mapping model name if its r1
        if model == "deepseek-r1":
            model = "deepseek-reasoner"
    
    while n > 0:
        batch_size = min(n, 20)
        n -= batch_size
        
        res = client.chat.completions.create(
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
    
    # If the backend is an OpenAI model
    if backend.startswith("gpt-"):
        # OpenAI pricing varies per model
        if "gpt-4" in backend:
            # GPT-4 pricing (approximate)
            input_cost = prompt_tokens / 1000000 * 10.0  # $10 per 1M tokens (approximate)
            output_cost = completion_tokens / 1000000 * 30.0  # $30 per 1M tokens (approximate)
        else:
            # GPT-3.5 pricing (approximate)
            input_cost = prompt_tokens / 1000000 * 0.5  # $0.5 per 1M tokens (approximate)
            output_cost = completion_tokens / 1000000 * 1.5  # $1.5 per 1M tokens (approximate)
    else:
        # Deepseek Reasoner pricing (standard rate), not off peak discount rates. 
        # Input: $0.55 per 1M tokens
        # Output: $2.19 per 1M tokens
        input_cost = prompt_tokens / 1000000 * 0.55
        output_cost = completion_tokens / 1000000 * 2.19
        
    cost = input_cost + output_cost
    return {"completion_tokens": completion_tokens, "prompt_tokens": prompt_tokens, "cost": cost}
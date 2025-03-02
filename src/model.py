import time
import os
from openai import OpenAI
from utils import dotdict

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
completion_tokens = 0
prompt_tokens = 0

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def gpt(prompt, model, temperature=0.7, max_tokens=4000, n=1, stop=None) -> list:
    messages = [{"role": "user", "content": prompt}]
    if model == "gpt-4":
        pass
        time.sleep(30) # to prevent speed limitation exception
    return chatgpt(messages, model=model, temperature=temperature, max_tokens=max_tokens, n=n, stop=stop)


def chatgpt(messages, model, temperature=0.0, max_tokens=4000, n=1, stop=None) -> list:
    global completion_tokens, prompt_tokens
    outputs = []
    
    # Use Deepseek API for deepseek models
    if model.startswith("deepseek"):
        return deepseek_chat(messages, model, temperature, max_tokens, n, stop)
    
    # Original OpenAI implementation
    while n > 0:
        cnt = min(n, 20)
        n -= cnt
        res = openai_client.chat.completions.create(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens,
                                           n=cnt, stop=stop)
        outputs.extend([choice.message.content for choice in res.choices])
        # log completion tokens
        completion_tokens += res.usage.completion_tokens
        prompt_tokens += res.usage.prompt_tokens
    return outputs


def deepseek_chat(messages, model, temperature, max_tokens, n, stop) -> list:
    """Handle chat completions using Deepseek API"""
    global completion_tokens, prompt_tokens
    outputs = []
    
    # Map deepseek model names to actual API model names
    model_map = {
        "deepseek-r1": "deepseek-reasoner",  # currently points to deepseek r1
    }
    
    api_model = model_map.get(model, model)
    
    while n > 0:
        batch_size = min(n, 20)  # Process in batches like the original
        n -= batch_size
        
        # Create multiple requests if n > 1
        for _ in range(batch_size):
            # Note: temperature is passed but has no effect for deepseek-reasoner
            res = deepseek_client.chat.completions.create(
                model=api_model,
                messages=messages,
                max_tokens=max_tokens,
                stop=stop
            )
            
            # For deepseek-reasoner, we might want to capture the reasoning content
            if model.startswith("deepseek-r") and hasattr(res.choices[0].message, 'reasoning_content'):
                # Store reasoning content somewhere if needed
                reasoning = res.choices[0].message.reasoning_content
                # Could log or store this for debugging/analysis
            
            outputs.append(res.choices[0].message.content)
            
            # Track token usage
            completion_tokens += res.usage.completion_tokens
            prompt_tokens += res.usage.prompt_tokens
    
    return outputs
 

def gpt_usage(backend="gpt-4"):
    global completion_tokens, prompt_tokens
    if backend == "gpt-4":
        cost = completion_tokens / 1000 * 0.06 + prompt_tokens / 1000 * 0.03
    elif backend == "gpt-4-turbo-preview":
        cost = completion_tokens / 1000 * 0.03 + prompt_tokens / 1000 * 0.01
    elif backend == "gpt-3.5-turbo":
        cost = completion_tokens / 1000 * 0.002 + prompt_tokens / 1000 * 0.0015
    elif backend == "deepseek-r1":
        # Deepseek Reasoner pricing (standard rate), not off peak discount rates. 
        # Input: $0.55 per 1M tokens
        # Output: $2.19 per 1M tokens
        input_cost = prompt_tokens / 1000000 * 0.55
        output_cost = completion_tokens / 1000000 * 2.19
        cost = input_cost + output_cost
    elif backend.startswith("deepseek"):
        # Generic pricing for other Deepseek models (standard rate)
        # Input: $0.27 per 1M tokens
        # Output: $1.10 per 1M tokens
        input_cost = prompt_tokens / 1000000 * 0.27
        output_cost = completion_tokens / 1000000 * 1.10
        cost = input_cost + output_cost
    return {"completion_tokens": completion_tokens, "prompt_tokens": prompt_tokens, "cost": cost}
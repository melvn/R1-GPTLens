

# GPTLens with Deepseek Reasoner

This is a fork of the original [GPTLens repository](https://arxiv.org/pdf/2310.01152.pdf), which was presented in the paper "Large Language Model-Powered Smart Contract Vulnerability Detection: New Perspectives" at the IEEE Trust, Privacy and Security (TPS) conference 2023.

This fork modifies the original authors' work to include the use of Deepseek Reasoner for both the auditor and critic stages, improving the accuracy and precision of vulnerability detection in smart contracts.

## Getting Started

### Prerequisites

1. Python 3.8+ environment
2. Deepseek API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/GPTLens.git
cd GPTLens

# Create and activate a virtual environment
python -m venv gptlens_env
source gptlens_env/bin/activate  # On Windows: gptlens_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Setting Up Your API Key

Set your Deepseek API key in the environment:

```bash
# On Linux/macOS
export DEEPSEEK_API_KEY="your-api-key-here"

# On Windows
set DEEPSEEK_API_KEY=your-api-key-here
```

## Running the Vulnerability Detection Pipeline

The vulnerability detection process consists of three stages:

1. **Auditor**: Identifies potential vulnerabilities in smart contracts
2. **Critic**: Evaluates the vulnerabilities identified by the auditor
3. **Ranker**: Combines auditor and critic outputs to produce final vulnerability scores

### Step 1: Run the Auditor

```bash
python src/run_auditor.py --backend=deepseek-r1 --temperature=0.7 --topk=3 --num_auditor=1 --data_dir=data_full/CVE_clean
```

| Parameter       | Description                                                     |
|-----------------|-----------------------------------------------------------------|
| `backend`       | The model to use (deepseek-r1 maps to deepseek-reasoner)        |
| `temperature`   | Controls randomness (passed for compatibility)                  |
| `topk`          | Number of vulnerabilities to identify per contract              |
| `num_auditor`   | Number of independent auditors to run                           |
| `data_dir`      | Directory containing the smart contracts to analyze             |

### Step 2: Run the Critic

```bash
python src/run_critic.py --backend=deepseek-r1 --temperature=0 --auditor_dir="auditor_deepseek-r1_0.7_top3_1" --num_critic=1 --shot=few
```

| Parameter     | Description                                                     |
|---------------|-----------------------------------------------------------------|
| `backend`     | The model to use (deepseek-r1 maps to deepseek-reasoner)        |
| `temperature` | Controls randomness (0 for deterministic outputs)               |
| `auditor_dir` | Directory containing auditor results                            |
| `num_critic`  | Number of independent critics                                   |
| `shot`        | Whether to use few-shot or zero-shot prompting                  |

### Step 3: Run the Ranker

```bash
python src/run_rank.py --auditor_dir="auditor_deepseek-r1_0.7_top3_1" --critic_dir="critic_deepseek-r1_0_1_few" --strategy="default"
```

| Parameter     | Description                                     |
|---------------|-------------------------------------------------|
| `auditor_dir` | Directory containing auditor results            |
| `critic_dir`  | Directory containing critic results             |
| `strategy`    | Strategy for generating the final score         |

## Technical Notes

1. **Model Mapping**: The command-line argument `deepseek-r1` is internally mapped to the Deepseek API model name `deepseek-reasoner`.

2. **File Locations**: The smart contracts should be placed in the `data_full/CVE_clean/` directory. If your files are in a different location, use the `--data_dir` parameter to specify the correct path.

3. **JSON Parsing Errors**: You may see "Expecting value" errors during the auditor stage. These are normal and occur when the model's output doesn't conform exactly to the expected JSON format.

4. **Results Location**: The final results will be stored in the `src/logs/` directory, organized by auditor, critic, and ranker directories.

## Troubleshooting

- **API Key Issues**: Ensure your Deepseek API key is correctly set in the environment.
- **Missing Files**: If you encounter "File not found" errors, check that your smart contracts are in the correct directory.
- **Model Errors**: If you see "Model Not Exist" errors, ensure you're using the correct model name (`deepseek-r1`).

## Benchmarking Results

The original paper benchmarked GPT-4 on 13 CVE smart contracts. This fork extends that work by benchmarking Deepseek Reasoner on the same dataset. Our preliminary results show that Deepseek Reasoner performs competitively with GPT-4 while offering better cost efficiency.

## Citation

If you use this work in your research, please cite the original paper:

```
@misc{hu2023large,
      title={Large Language Model-Powered Smart Contract Vulnerability Detection: New Perspectives}, 
      author={Sihao Hu and Tiansheng Huang and Fatih İlhan and Selim Furkan Tekin and Ling Liu},
      year={2023},
      eprint={2310.01152},
      archivePrefix={arXiv},
      primaryClass={cs.CR}
}
```
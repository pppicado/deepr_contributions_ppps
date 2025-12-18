# DeepR Agents

DeepR employs a multi-agent "Council" architecture where different AI models take on specific roles to ensure comprehensive and unbiased research.

## Core Agents (DAG Workflow)

These agents are used in the standard `DAG` and `Ensemble` workflows.

### 1. The Coordinator
- **Role:** Planning & Strategy.
- **Responsibility:** Receives the user's initial prompt and breaks it down into a structured research plan. It identifies key questions to investigate and assigns them to the Researchers.
- **Model:** Typically a high-reasoning model (e.g., GPT-4o).

### 2. The Council Members (Researchers)
- **Role:** Execution & Investigation.
- **Responsibility:** Each member executes the research tasks assigned by the Coordinator. They work in parallel to gather information, analyze data, and generate initial findings.
- **Diversity:** Users can select multiple different models (e.g., Claude 3 Opus, Llama 3) to ensure cognitive diversity and reduce single-model bias.

### 3. The Critics
- **Role:** Quality Control & Peer Review.
- **Responsibility:** They review the findings of the Researchers. The critique process is **blind** (anonymized) to prevent bias based on the identity of the researching model. They point out logical fallacies, missing context, or weak arguments.

### 4. The Chairman
- **Role:** Synthesis & Final Decision.
- **Responsibility:** The Chairman reads the original plan, the research findings, and the critiques. It then synthesizes everything into a final, comprehensive answer for the user.
- **Nature:** Acts as the final arbiter and voice of the Council.

## Diagnostic Orchestration (DxO) Agents

The DxO workflow uses a more flexible, role-based panel approach.

### 1. Lead Researcher
- **Focus:** Primary analysis and synthesis.
- **Goal:** Conduct thorough research analysis and identify key findings and patterns.

### 2. Critical Reviewer
- **Focus:** Evaluation and Falsification.
- **Goal:** Identify gaps, weaknesses, and methodological issues in the proposed arguments.

### 3. Domain Expert
- **Focus:** Specialized Context.
- **Goal:** Provide deep, field-specific knowledge that generalist models might miss.

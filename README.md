

![Placeholder](./assets/placeholder.jpg)

# **IteraMindAI**

Welcome to **IteraMindAI** – a modular, high-performance AI system designed to simulate **iterative reasoning and intelligent task management**. This framework integrates **Google Gemini API**, **Rust**, **Go**, and **Python** to create a powerful system capable of managing complex tasks through continuous refinement and agent orchestration.

---

## **Project Overview**

**IteraMindAI** is built with the goal of achieving **efficient task decomposition, iterative learning, and real-time monitoring**. The system leverages API-driven AI models (Google Gemini), breaking larger tasks into manageable subtasks and iteratively refining solutions through a structured process.

Each module is implemented in the language best suited for its purpose:

- **Google Gemini API**: Provides state-of-the-art generative and analytical capabilities for agent operations.
- **Go**: Backend orchestration for managing iterative workflows and coordinating agent interactions.
- **Python**: API integration and logic for task-specific agents (generation, critique, and integration).
- **Redis**: Enables caching and state management for iterative workflows.

---

## **Features**

- **Iterative Orchestration**: Coordinates multiple agents (generation, critique, integration) for task refinement.
- **Google Gemini Integration**: Replaces local model hosting with API-based AI services, ensuring scalability and robustness.
- **Task Decomposition and Refinement**: Dynamically breaks down and refines complex tasks.
- **Agent-Based Architecture**: Specialized agents (Python) handle different aspects of the workflow.
- **Monitoring and Visualization**: Real-time dashboards using **Prometheus** and **Grafana**.
- **State Management**: Redis for short and long-term memory of iterative processes.

---

## **Tech Stack**

- **Google Gemini API**: Core AI service for generation, analysis, and integration.
- **Go**: Backend service for task orchestration and monitoring.
- **Python**: Agent logic and API integration.
- **Redis**: In-memory storage for efficient data caching and state management.
- **Prometheus & Grafana**: Tools for monitoring system performance and metrics.

---

## **Repository Structure**
```plaintext
/IteraMindAI
│
├── /backend-go                 # Backend and orchestration (Go)
│   ├── /cmd                    # Entry points
│   ├── /internal               # Task management logic
│   ├── /pkg                    # Utility packages
│   └── go.mod                  # Go dependencies
│
├── /integration-python         # Python-based agents for API integration
│   ├── gemini_integration.py   # Handles Google Gemini API interactions
│   ├── agents                  # Agent scripts (generate, criticize, integrate)
│   └── requirements.txt        # Python dependencies
│
├── /monitoring                 # Monitoring setup (Prometheus & Grafana)
│   └── docker-compose.yml      # Docker orchestration for monitoring tools
│
├── /assets                     # Images and placeholders
│   └── placeholder.jpg         # Project logo or visual
│
├── /docs                       # Documentation
├── .gitignore                  # Git ignore file
├── LICENSE                     # License information
├── README.md                   # This README file
└── CONTRIBUTING.md             # Contribution guidelines
```

---

## **Installation**

Follow the steps below to set up **IteraMindAI** on your local machine:

### **Clone the Repository**
```bash
git clone https://github.com/your-username/IteraMindAI.git
cd IteraMindAI
```

### **Set Up the Environments**

- **Python Agents**:
  ```bash
  cd integration-python
  python3 -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r requirements.txt
  ```

- **Go Backend**:
  ```bash
  cd backend-go
  go mod tidy
  go build
  ```

## **Usage**

1. **Launch the Python Agents**:
    - **Start the Agents (Generate, Criticize, Integrate)**:
      ```bash
      cd integration-python
      python python gemini_integration.py
      ```

2. **Launch the Go Backend Orchestrator**:

   Modify prompt := "Example" on main.go
   ```bash
   cd backend-go/cmd
   go run main.go
   ```

---

## **Configuration**

1. **Google Gemini API Key**:
    - Add your API key in `integration-python/config.py`:
      ```python
      API_KEY = "your_google_gemini_api_key"
      ```

2. **Environment Variables**:
    - Create a `.env` file in the root directory and include:
      ```plaintext
      GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key
      ```

---

## **License**

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
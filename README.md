# AI IT Helpdesk Agent

An **AI-powered IT Helpdesk Agent** built using **Python and Ollama** to provide intelligent and practical IT troubleshooting assistance.

The system combines a **local Large Language Model (LLM)** with **Retrieval-Augmented Generation (RAG)**, agent-based tool selection, system diagnostic tools, streaming responses, and conversation memory to provide context-aware solutions for common IT issues.

## Features

- Local LLM inference using **Ollama**
- **Retrieval-Augmented Generation (RAG)**
- IT troubleshooting knowledge base
- Agent-based tool selection
- Internet connectivity checking
- System information retrieval
- RAM usage monitoring
- CPU usage monitoring
- Disk usage monitoring
- Real-time streaming AI responses
- Conversation memory
- Command-Line Interface (CLI)
- Modular Python architecture

## Knowledge Base

The troubleshooting knowledge base covers common IT support topics, including:

- Wi-Fi and Internet connectivity
- Windows troubleshooting
- Printer issues
- Network problems
- Hardware-related issues

## System Tools

The agent can use system-level tools to retrieve real-time information, including:

- Internet connectivity status
- System information
- RAM usage
- CPU usage
- Disk usage

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core development |
| Ollama | Local LLM inference |
| RAG | Knowledge retrieval |
| CLI | User interaction |
| Python System Tools | System monitoring |

## How It Works

1. The user enters an IT-related query through the CLI.
2. The agent analyzes the query.
3. Relevant information is retrieved from the IT knowledge base using RAG.
4. The agent selects appropriate tools when system information is required.
5. Ollama processes the retrieved information and tool results.
6. The agent generates a context-aware troubleshooting response.
7. The response is streamed to the user in real time.
8. Conversation memory maintains relevant context for subsequent queries.

## Streaming Responses

The agent uses Ollama's streaming API to generate and display AI responses progressively.

Instead of waiting for the complete response, users can see the response appear in real time, providing a more interactive and responsive terminal experience.

Example:

```text
You: My printer is offline.

AI Helpdesk: Try these steps:
1. Check that the printer is powered on.
2. Check the network connection.
3. Verify that the correct printer is selected.
4. Restart the printer and try again.
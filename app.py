"""
Command-line application for the AI IT Helpdesk Agent.

Supports ChatGPT-style streaming responses.
"""

import requests

from agent import ITHelpdeskAgent


def print_banner():
    print("=" * 70)
    print("                 AI IT HELPDESK AGENT")
    print("=" * 70)
    print("Powered by Ollama + Python + RAG + Tools + Memory")
    print("Streaming mode: ENABLED")
    print()
    print("Type your IT problem and press Enter.")
    print("Commands:")
    print("  /help   - Show help")
    print("  /clear  - Clear conversation memory")
    print("  /exit   - Exit application")
    print("=" * 70)


def main():

    print_banner()

    agent = ITHelpdeskAgent()

    # ============================================================
    # LOAD KNOWLEDGE BASE
    # ============================================================

    try:

        print("\nLoading knowledge base...")

        agent.initialize()

        print(
            f"Loaded {len(agent.knowledge_base.documents)} "
            "knowledge-base documents."
        )

    except Exception as error:

        print("\nFailed to initialize the knowledge base.")
        print(f"Error: {error}")
        return

    print("\nAgent is ready.\n")

    # ============================================================
    # MAIN CHAT LOOP
    # ============================================================

    while True:

        try:

            question = input("You: ").strip()

        except (KeyboardInterrupt, EOFError):

            print("\n\nGoodbye!")
            break

        if not question:
            continue

        # ========================================================
        # COMMANDS
        # ========================================================

        if question.lower() == "/exit":

            print("Goodbye!")
            break

        if question.lower() == "/help":

            print(
                "\nExamples:\n"
                "- My laptop is connected to Wi-Fi but there is no internet.\n"
                "- My computer is running very slowly.\n"
                "- My printer is offline.\n"
                "- Check my internet connection.\n"
                "- How much RAM is currently being used?\n"
                "- What operating system am I using?\n"
                "- How much disk space do I have?\n"
                "- Check my CPU usage.\n"
            )

            continue

        if question.lower() == "/clear":

            agent.memory.clear()

            print("\nConversation memory cleared.\n")

            continue

        # ========================================================
        # STREAMING RESPONSE
        # ========================================================

        try:

            print("\nAI Helpdesk: ", end="", flush=True)

            # ----------------------------------------------------
            # IMPORTANT:
            #
            # process_stream() returns pieces of the answer.
            # We print each piece immediately.
            # ----------------------------------------------------

            for chunk in agent.process_stream(question):

                print(
                    chunk,
                    end="",
                    flush=True,
                )

            print("\n")

        except requests.exceptions.ConnectionError:

            print(
                "\n\nCould not connect to Ollama."
            )

            print(
                "Make sure Ollama is running at "
                "http://localhost:11434\n"
            )

        except Exception as error:

            print(
                "\n\nAn error occurred while processing "
                "your request."
            )

            print(f"Details: {error}")

            print(
                "\nCheck that Ollama is running and that "
                "the required models are installed.\n"
            )


if __name__ == "__main__":
    main()
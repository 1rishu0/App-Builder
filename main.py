# Used to parse command-line arguments (e.g., --recursion-limit)
# Provides access to system-specific parameters and functions (like exiting)
# helps print detailed error tracebacks for debugging
import argparse
import sys
import traceback

# Import the compiled state graph (the LangGraph agent) from your agent.graph module
from agent.graph import agent

# Define the main function that executes when the program runs
def main():
    # Initialize an argument parser to allow command-line configuration
    parser = argparse.ArgumentParser(description="Run Engineering Project Planner")

    # Add a command-line argument '--recursion-limit' (or '-r' as a short form)
    # This controls how many times recursive processing (looping through steps) is allowed
    # Default is 100, so if user doesn't specify, recursion limit is 100
    parser.add_argument("--recursion-limit","-r", type=int, default=100,
                        help="Recursion limit for processing (default: 100)")

    # Parse the provided command-line arguements and store them in 'args'
    args = parser.parse_args()

    try:
        # Prompt the user for input - asking them to describe their project
        user_prompt = input("Enter your project prompt: ")

        # Call the LangGraph agent's invoke() method
        # The first dictionary is the input state (with 'user_prompt')
        # The second dictionary is the configuration (with 'recursion_limit')
        result = agent.invoke(
            {"user_prompt": user_prompt},
            {"recursion_limit": args.recursion_limit}
        )

        # Print the final state returned by the graph after all agents (planner -> architect -> coder) run
        print("Final State:", result)

    # Handle if the user presses Ctrl + C to cancel execution
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        # Exit the program gracefully with status code 0 (normal exit)
        sys.exit(0)

    # Handle any unexpected errors during execution
    except Exception as e:
        # Print the full traceback for debugging (shows where the error occurred)
        traceback.print_exc()
        # Print the actual error message to standard error
        print(f"Error: {e}", file=sys.stderr)
        # Exit the program with status code 1 (indicating an error)
        sys.exit(1)

# This block ensures that the script runs only when executed directly
# (not when imported as a module in another file)
if __name__ == "__main__":
    # call the main() function to start the program
    main()
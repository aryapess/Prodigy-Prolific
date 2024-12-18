from flask import Flask, request, redirect
import prodigy
from prodigy.components.loaders import JSONL

# Flask setup
app = Flask(__name__)

# Define the base Prodigy URL (replace localhost with ngrok or hosting URL for public access)
PRODIGY_BASE_URL = "https://9af3-71-123-35-120.ngrok-free.app"  # Change to your hosted URL

@prodigy.recipe(
    "single_or_multiple_choice",
    dataset=("Dataset to save annotations", "positional", None, str),
    file_path=("Path to the JSONL file", "positional", None, str),
)
def single_or_multiple_choice(dataset, file_path):
    """
    A custom recipe for showing one multiple-choice or single-choice question at a time per task.
    The task configuration will adapt based on whether the question is multiple-choice or single-choice.
    """
    # Load the data from the JSONL file
    stream = JSONL(file_path)

    def set_choice_style(example):
        """
        Modify each example's config based on whether it's single-choice or multiple-choice.
        - For single-choice, auto-accept should be enabled and choice_style is set to 'single'.
        - For multiple-choice, auto-accept is disabled and choice_style is set to 'multiple'.
        """
        if example.get("choice_style") == "multiple":
            example["config"] = {"choice_auto_accept": False, "choice_style": "multiple"}
        else:
            example["config"] = {"choice_auto_accept": True, "choice_style": "single"}
        return example

    # Apply the function to each example in the stream
    stream = (set_choice_style(example) for example in stream)

    # Flask route to handle Prolific URL and redirect to Prodigy
    @app.route("/")
    def redirect_to_prodigy():
        """
        Capture Prolific URL, extract session ID, and redirect to Prodigy.
        """
        prolific_pid = request.args.get("PROLIFIC_PID")
        session_id = request.args.get("SESSION_ID")

        if prolific_pid and session_id:
            # Construct Prodigy URL with the session ID
            prodigy_url = f"{PRODIGY_BASE_URL}/?session={session_id}"
            print(f"Redirecting Prolific user to Prodigy: {prodigy_url}")
            return redirect(prodigy_url)
        else:
            return "Error: Missing required parameters (PROLIFIC_PID or SESSION_ID).", 400

    # Run Flask server
    print("Starting Flask server...")
    app.run(port=5000)  # Run Flask on port 5000

    # Return Prodigy configuration
    return {
        "dataset": dataset,  # The dataset where annotations will be saved
        "view_id": "choice",  # Built-in choice interface for multiple-choice questions
        "stream": stream,  # Stream from the JSONL file
        "config": {
            "force_stream_order": True,  # Ensure the order of examples is preserved
            "global_css": """
                /* Align text to the left */
                .prodigy-content {
                    text-align: left;
                    max-width: 800px;  /* Adjust width if necessary */
                    margin: 0 auto;    /* Center the content block itself */
                }
                
                /* Ensure choices align to the left too */
                .prodigy-choice {
                    text-align: left;
                }
            """
        }
    }

import prodigy
from prodigy.components.loaders import JSONL

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



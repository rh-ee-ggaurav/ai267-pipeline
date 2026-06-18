"""
================================================================================
OBJECTIVE: Automate Social Media Content Moderation using AI Logic
--------------------------------------------------------------------------------
Component 1: Checks a text comment for specific blocked words ("spam", "buy").
Component 2: Decides whether to approve the post or flag it for review.
Pipeline:    Connects the safety check output directly to the decision system.
================================================================================
"""

from kfp import dsl
from kfp import compiler

# ==============================================================================
# COMPONENT 1: THE SAFETY FILTER (AI Text Analysis)
# ==============================================================================
@dsl.component(base_image="python:3.11-slim")
def check_text_safety(user_comment: str) -> str:
    """Analyzes text to see if it contains banned words."""
    print(f"Filter Step: Analyzing comment: '{user_comment}'")
    
    # Simple rule-based AI simulation
    cleaned_text = user_comment.lower()
    if "spam" in cleaned_text or "buy now" in cleaned_text:
        status = "REJECT"
    else:
        status = "APPROVE"
        
    print(f"Filter Step: Analysis complete. Result status -> {status}")
    return status


# ==============================================================================
# COMPONENT 2: THE ENFORCEMENT SYSTEM (Action Taker)
# ==============================================================================
@dsl.component(base_image="python:3.11-slim")
def enforce_moderation(moderation_status: str):
    """Takes action based on the upstream filter's decision status."""
    print(f"Enforcement Step: Received status: {moderation_status}")
    
    if moderation_status == "REJECT":
        print("Enforcement Action: [REJECTED] Comment hidden! Sent to human moderators.")
    else:
        print("Enforcement Action: [APPROVED] Comment approved! Published to feed.")


# ==============================================================================
# THE PIPELINE ORCHESTRATION (The RHOAI Blueprint)
# ==============================================================================
@dsl.pipeline(
    name="ai-content-moderator-pipeline",
    description="A real-world style pipeline that filters text data and takes action."
)
def moderation_flow(user_text_input: str = "This is a great tutorial, thanks!"):
    """
    1. The user types a comment into the RHOAI Dashboard text box.
    2. RHOAI defaults to a polite compliment if left blank.
    3. Component 1 runs and spits out either 'APPROVE' or 'REJECT'.
    4. Component 2 reads that result string and applies the enforcement rules.
    """
    
    # Step 1: Run the safety scan task on the user's dashboard text input
    filter_task = check_text_safety(user_comment=user_text_input)
    
    # Step 2: Grab the string output ('APPROVE' or 'REJECT') and pour it into Step 2
    action_task = enforce_moderation(moderation_status=filter_task.output)


# ==============================================================================
# COMPILATION
# ==============================================================================
if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=moderation_flow,
        package_path="rhoai_moderator_pipeline.yaml"
    )
    print("\n>>> Success! 'rhoai_moderator_pipeline.yaml' has been generated. <<<")

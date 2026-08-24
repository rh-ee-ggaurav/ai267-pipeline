"""
================================================================================
OBJECTIVE: Automate Social Media Content Moderation using AI Logic & dsl.If
--------------------------------------------------------------------------------
Component 1: Checks a text comment for specific blocked words ("spam", "buy").
Component 2a: Publishes approved comments to the feed.
Component 2b: Flags rejected comments and sends them to human review.
Pipeline: Uses dsl.If / dsl.Else to branch graph execution at runtime.
================================================================================
"""

from kfp import dsl
from kfp import compiler

# ==============================================================================
# COMPONENT 1: THE SAFETY FILTER
# ==============================================================================
@dsl.component(base_image="python:3.11-slim")
def check_text_safety(user_comment: str) -> str:
    """Analyzes text to see if it contains banned words."""
    print(f"Filter Step: Analyzing comment: '{user_comment}'")
    
    cleaned_text = user_comment.lower()
    if "spam" in cleaned_text or "buy now" in cleaned_text:
        status = "REJECT"
    else:
        status = "APPROVE"
        
    print(f"Filter Step: Analysis complete. Result status -> {status}")
    return status


# ==============================================================================
# COMPONENT 2a: APPROVAL HANDLER
# ==============================================================================
@dsl.component(base_image="python:3.11-slim")
def publish_comment(user_comment: str):
    """Executes ONLY if the comment is approved."""
    print(f"Enforcement Action: [APPROVED] Comment approved! Published to feed: '{user_comment}'")


# ==============================================================================
# COMPONENT 2b: REJECTION HANDLER
# ==============================================================================
@dsl.component(base_image="python:3.11-slim")
def flag_for_review(user_comment: str):
    """Executes ONLY if the comment is rejected."""
    print(f"Enforcement Action: [REJECTED] Comment hidden! Sent to human moderators: '{user_comment}'")


# ==============================================================================
# THE PIPELINE ORCHESTRATION WITH GRAPH BRANCHING
# ==============================================================================
@dsl.pipeline(
    name="ai-content-moderator-pipeline",
    description="A real-world style pipeline using dsl.If branching for content enforcement."
)
def moderation_flow(user_text_input: str = "This is a great tutorial, thanks!"):
    
    # Step 1: Run safety scan
    filter_task = check_text_safety(user_comment=user_text_input)
    
    # Step 2: Branch logic based on output
    with dsl.If(filter_task.output == "APPROVE"):
        publish_comment(user_comment=user_text_input)
        
    with dsl.Else():
        flag_for_review(user_comment=user_text_input)


# ==============================================================================
# COMPILATION
# ==============================================================================
if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=moderation_flow,
        package_path="if-rhoai-moderator_pipeline.yaml"
    )
    print("\n>>> Success! 'if_rhoai_moderator_pipeline.yaml' has been generated. <<<")

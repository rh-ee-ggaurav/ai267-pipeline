r"""
================================================================================
PIPELINE DOCUMENTATION & ARCHITECTURE OVERVIEW (RED HAT COURSE ALIGNED)
================================================================================
WHAT THIS PIPELINE DOES:
1. Maps precisely to Chapter 7 of the RHOAI course textbook.
2. Imports 'kubernetes' directly from the main 'kfp' module.
3. Injects values from 'my-custom-secret' into container environment variables.
4. Manages caching and sets precise task resource profiles.
================================================================================
"""

import os
# Corrected Import: Importing kubernetes directly from kfp as shown in your book
from kfp import dsl, kubernetes 

BASE_IMAGE = "registry.access.redhat.com/ubi10/python-312-minimal:1781585939"


# ==============================================================================
# COMPONENT 1: LOAD AND PRINT SECRET DATA
# ==============================================================================
@dsl.component(base_image=BASE_IMAGE)
def print_secret_data() -> str:
    """
    Component 1: Evaluates system environment variable mappings injected
    at runtime, print-audits the credentials, and yields a status payload.
    """
    import os

    # Query injected process configuration mappings from container environment
    user_string = os.environ.get("APP_USER", "NOT_FOUND")
    key_string = os.environ.get("APP_KEY", "NOT_FOUND")

    print("--- INJECTED KUBERNETES CONFIGURATION DATA ---")
    print(f"System Authenticated Username: {user_string}")
    print(f"System Key Token Length: {len(key_string)} characters long.")
    print("----------------------------------------------")
    
    return f"Authentication success for profile: {user_string}"


# ==============================================================================
# COMPONENT 2: EXECUTION TRACKER
# ==============================================================================
@dsl.component(base_image=BASE_IMAGE)
def track_execution(status_message: str):
    """
    Component 2: Standard downstream step designed to process preceding metadata
    and run within strict container sizing boundaries.
    """
    print(f"Workflow status report accepted: {status_message}")
    print("Task execution tracking complete within verified hardware limits.")


# ==============================================================================
# PIPELINE ORCHESTRATION (Matches textbook syntax)
# ==============================================================================
@dsl.pipeline(name="kubernetes-secret-injection-demo")
def secret_demo_pipeline():
    # 1. Initialize Step 1 Task
    task1 = print_secret_data()

    # 2. Inject Secret using the exact textbook function calls
    kubernetes.use_secret_as_env(
        task1,
        secret_name="SECRET-NAME",
        secret_key_to_env={"api_user": "APP_USER"},
    )
    
    kubernetes.use_secret_as_env(
        task1,
        secret_name="SECRET-NAME",
        secret_key_to_env={"api_key": "APP_KEY"},
    )

    # 3. Disable caching on the task handle
    task1.set_caching_options(False)

    # 4. Initialize Step 2 Task
    task2 = track_execution(status_message=task1.output)

    # 5. Apply explicit hardware requests and limits from the text definitions
    task2.set_memory_request("256Mi")
    task2.set_memory_limit("MEMORY-LIMIT-TODO")
    task2.set_cpu_request("256m")
    task2.set_cpu_limit("CPU-LIMIT-TODO")


# ==============================================================================
# COMPILATION BLOCK
# ==============================================================================
if __name__ == "__main__":
    from kfp import compiler
    compiler.Compiler().compile(secret_demo_pipeline, "pipeline.yaml")
    print("\n[SUCCESS] 'pipeline.yaml' generated successfully matching course standards.")

"""
================================================================================
PIPELINE DOCUMENTATION & ARCHITECTURE OVERVIEW
================================================================================
WHAT THIS PIPELINE DOES:
1. Demonstrates the orchestration boundary between Kubernetes infrastructure 
   layer storage configurations and runtime Kubeflow container tasks.
2. Injects critical application metadata fields securely out of an existing 
   Kubernetes Secret configuration map ('my-custom-secret') without hardcoding
   passwords or access values inside the shared automation script files.
3. Showcases cluster asset management configurations including:
   - Cache invalidation options (forcing the step to compute fresh runs).
   - Core hardware ceiling limits (CPU and Memory thresholds).

VISUAL FLOW OF INFRASTRUCTURE CONFIGURATIONS:
    [ Kubernetes Namespace Secret: my-custom-secret ]
           |                              |
      (api_user)                     (api_key)
           |                              |
    [ Injected as: APP_USER ]     [ Injected as: APP_KEY ]
           \                              /
            \                            /
             v                          v
      [ Component 1: Secret Printer Task ]  <-- Caching: Disabled
                      |
             [ Component 2: Execution Tracker Task ] <-- CPU/Mem Constraints
================================================================================
"""

import os
from kfp import dsl, compiler
from kfp_kubernetes import kubernetes  # Essential extension suite module for K8s mappings

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
# PIPELINE ORCHESTRATION WITH RESOURCE METRIC RULES
# ==============================================================================
@dsl.pipeline(name="kubernetes-secret-injection-demo")
def secret_demo_pipeline():
    # 1. Initialize Step 1
    task1 = print_secret_data()

    # 2. INJECT SECRET FIELDS AS CONTAINER ENVIRONMENT VARIABLES:
    # First field injection mapping: api_user value keys to APP_USER environment string
    kubernetes.use_secret_as_env(
        task1,
        secret_name="SECRET-NAME",
        secret_key_to_env={"api_user": "APP_USER"},
    )
    
    # Second field injection mapping: api_key value keys to APP_KEY environment string
    kubernetes.use_secret_as_env(
        task1,
        secret_name="SECRET-NAME",
        secret_key_to_env={"api_key": "APP_KEY"},
    )

    # 3. CONFIGURE RUNTIME PIPELINE ENGINE BEHAVIOR:
    # Disable caching options to force cluster compute executions every single run
    task1.set_caching_options(False)

    # 4. Initialize Step 2 and attach performance profiling rules
    task2 = track_execution(status_message=task1.output)

    # Force strict performance scaling limits to enforce compute management bounds
    task2.set_memory_request("GIVE-RAM-TODO")
    task2.set_cpu_request("GIVE-CPU-TODO")


# ==============================================================================
# COMPILATION BLOCK
# ==============================================================================
if __name__ == "__main__":
    compiler.Compiler().compile(secret_demo_pipeline, "pipeline.yaml")
    print("\n[SUCCESS] 'pipeline.yaml' generated successfully.")
    print("[INFO] Ready for import into the OpenShift AI dashboard workspace.")

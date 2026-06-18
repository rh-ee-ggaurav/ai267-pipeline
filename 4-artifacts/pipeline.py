"""
================================================================================
PIPELINE DOCUMENTATION & ARCHITECTURE OVERVIEW
================================================================================
WHAT THIS PIPELINE DOES:
1. Imports a manually uploaded employee dataset (CSV) from an explicit S3 
   bucket path using the Kubeflow Pipelines (KFP) Importer component.
2. Converts that S3 path string into a formally tracked KFP 'Dataset' artifact.
3. Showcases One-to-Many Artifact reuse by passing this single source artifact 
   node into TWO parallel components at the exact same time:
     - Component 1 (Printer): Reads and audits the raw content directly in the logs.
     - Component 2 (Filter): Streams, filters, and separates the data into two 
       distinct, clean files based on employee roles.
4. Explains how to override generic system filenames inside the S3 storage 
   layer to enforce specific outputs named 'manager.csv' and 'developer.csv'.

VISUAL FLOW OF ARTIFACTS ON THE DASHBOARD:
             [ s3://dspa-artifacts/mydata/data.csv ]  <-- Manual Upload
                              |
                     [ Importer Task ]
                              |
                     (Dataset Artifact Node)
                     /                     \
                    /                       \
        [ Component 1: Printer ]    [ Component 2: Filter/Splitter ]
        (Reads & logs content)       (Creates & uploads new files)
                                      /                     \
                                     /                       \
                       (manager_dataset Node)       (developer_dataset Node)
                            |                                    |
                     [ manager.csv ]                      [ developer.csv ]
================================================================================
"""

import os
from kfp import dsl, compiler
from kfp.dsl import importer, Input, Output, Dataset

# Define the explicit Red Hat UBI minimal container image to guarantee compliance 
# with OpenShift cluster security policies and bypass network pip installs.
BASE_IMAGE = "registry.access.redhat.com/ubi10/python-312-minimal:1781585939"


# ==============================================================================
# COMPONENT 1: READ AND PRINT ONLY (Pure Consumer Component)
# ==============================================================================
@dsl.component(base_image=BASE_IMAGE)
def print_dataset(csv_in: Input[Dataset]):
    """
    Component 1: Purely a data consumer. It receives the localized file descriptor 
    from the central importer node, reads it using native Python file I/O, and 
    streams the raw content directly to the standard container logs for auditing.
    """
    # Open and parse the localized staging copy of the S3 file
    with open(csv_in.path, "r") as f:
        content = f.read()
        
    print("--- RAW DATA FETCHED FROM S3 ---")
    print(content.strip())
    print("--------------------------------")


# ==============================================================================
# COMPONENT 2: FILTER AND CREATE SPECIFIC FILENAMES
# ==============================================================================
@dsl.component(base_image=BASE_IMAGE)
def filter_by_role(
    dataset: Input[Dataset],
    manager_dataset: Output[Dataset],
    developer_dataset: Output[Dataset]
):
    """
    Component 2: Reads from the primary imported dataset, extracts target rows, 
    manipulates file system paths to rename the outputs, and registers two fresh
    documents ('manager.csv' and 'developer.csv') back to the S3 bucket.
    """
    import os

    # 1. Read the input rows from the shared artifact dependency
    with open(dataset.path, "r") as f:
        lines = f.readlines()

    header = lines[0]

    # 2. BYPASSING THE SYSTEM DEFAULT NAMES:
    # By default, KFP creates a generic file named 'data' with no extension.
    # To override this, we strip 'data' from the directory using os.path.dirname.
    manager_dir = os.path.dirname(manager_dataset.path)
    developer_dir = os.path.dirname(developer_dataset.path)

    # 3. Create the clean target file names requested
    manager_file_path = os.path.join(manager_dir, "manager.csv")
    developer_file_path = os.path.join(developer_dir, "developer.csv")

    # 4. Filter the rows and write directly to the newly named local paths
    with open(manager_file_path, "w") as f_mgr, open(developer_file_path, "w") as f_dev:
        f_mgr.write(header)
        f_dev.write(header)
        
        for line in lines[1:]:
            if "Manager" in line:
                f_mgr.write(line)
            elif "Developer" in line:
                f_dev.write(line)
                
    # 5. OVERWRITING THE METADATA PATH REFERENCES:
    # We must explicitly reassign the metadata '.path' variables to our new files.
    # This instructs OpenShift to grab 'manager.csv' and 'developer.csv' during
    # the post-execution sync phase and push them up to the storage bucket.
    manager_dataset.path = manager_file_path
    developer_dataset.path = developer_file_path

    print(f"Created explicit named file: {manager_file_path}")
    print(f"Created explicit named file: {developer_file_path}")


# ==============================================================================
# PIPELINE ORCHESTRATION (Parallel Consumer Blueprint)
# ==============================================================================
@dsl.pipeline(name="named-file-s3-pipeline")
def job_pipeline(
    # Default path pointing to your manually uploaded dataset inside the bucket
    s3_data_path: str = "s3://dspa-artifacts/mydata/data.csv"
):
    # STEP 1: Turn your raw S3 URI string into a trackable KFP Artifact node.
    # This acts as the single data gatekeeper for your pipeline.
    import_data_task = importer(
        artifact_uri=s3_data_path,
        artifact_class=Dataset,
        reimport=False,
    )
    
    # STEP 2: Pass the imported S3 artifact directly into the printer task.
    task1 = print_dataset(csv_in=import_data_task.output)
    
    # STEP 3: Pass the EXACT SAME imported S3 artifact into the filter task.
    # Because task1 and task2 both consume import_data_task.output and do not
    # depend on each other, OpenShift executes them concurrently in parallel!
    task2 = filter_by_role(dataset=import_data_task.output)


# ==============================================================================
# COMPILATION TRIGGER
# ==============================================================================
if __name__ == "__main__":
    # Compile the Python script down into a Kubernetes-compatible YAML template
    compiler.Compiler().compile(job_pipeline, "pipeline.yaml")
    print("\n[SUCCESS] 'pipeline.yaml' generated successfully.")
    print("[INFO] Upload this YAML file to your OpenShift AI Dashboard to run it.")

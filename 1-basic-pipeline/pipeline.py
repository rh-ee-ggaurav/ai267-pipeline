"""
================================================================================
OBJECTIVE: Calculate Worked Salary and Deduct 30% Tax
--------------------------------------------------------------------------------
Component 1: Multiplies hours by hourly rate to calculate the gross salary.
Component 2: Takes that gross salary and calculates a flat 30% tax on it.
Pipeline:    Connects them so the salary calculated in Step 1 drops straight 
             into the tax calculation in Step 2.
================================================================================
"""

from kfp import dsl
from kfp import compiler

# ==============================================================================
# COMPONENT 1: THE SALARY CALCULATOR (HR Department)
# ==============================================================================
@dsl.component(base_image="registry.access.redhat.com/ubi10/python-312-minimal:1781585939")
def calculate_salary(hours_worked: float, hourly_rate: float) -> float:
    """Multiplies hours by the rate to find the total gross salary earned."""
    gross_salary = hours_worked * hourly_rate
    print(f"HR Component: Worked {hours_worked} hours at ${hourly_rate}/hour.")
    print(f"HR Component: Calculated Gross Salary = ${gross_salary}")
    return gross_salary


# ==============================================================================
# COMPONENT 2: THE TAX DEDUCTION CALCULATOR (Tax Office)
# ==============================================================================
@dsl.component(base_image="registry.access.redhat.com/ubi10/python-312-minimal:1781585939")
def calculate_30_percent_tax(gross_salary: float):
    """Takes the calculated gross salary and computes a flat 30% tax."""
    tax_owed = gross_salary * 0.30
    print(f"Tax Component: Received Gross Salary input of ${gross_salary}")
    print(f"Tax Component: 30% Tax Owed = ${tax_owed}")


# ==============================================================================
# THE PIPELINE ORCHESTRATION (The Workflow Graph)
# ==============================================================================
@dsl.pipeline(
    name="payroll-and-tax-pipeline",
    description="Calculates gross earnings first, then computes a 30% tax deduction."
)
def payroll_flow(input_hours: float = 40.0, input_rate: float = 25.0):
    """
    1. The user inputs 'input_hours' and 'input_rate' in the RHOAI Dashboard.
    2. Component 1 runs to compute the total gross salary.
    3. Component 2 automatically grabs that salary and applies the 30% tax rule.
    """
    
    # Step 1: Run the salary calculation task
    salary_task = calculate_salary(hours_worked=input_hours, hourly_rate=input_rate)
    
    # Step 2: Pass the output from the salary task directly into the tax component
    tax_task = calculate_30_percent_tax(gross_salary=salary_task.output)


# ==============================================================================
# COMPILATION STEP
# ==============================================================================
if __name__ == "__main__":
    compiler.Compiler().compile(
        #We are calling function created in line no 45
        pipeline_func=payroll_flow,
        #We are giving output file name
        package_path="payroll_pipeline.yaml"
    )
    print("\n>>> Success! 'payroll_pipeline.yaml' has been generated. <<<")

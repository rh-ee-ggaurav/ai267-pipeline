from typing import NamedTuple
from kfp import dsl, compiler

# ==============================================================================
# STEP 1: CREATE THE WORDS (Position-matching determines where data goes)
# ==============================================================================
@dsl.component(base_image="python:3.11-slim")
def create_words() -> NamedTuple("outputs", [("greeting", str), ("name", str)]):
    """
    HOW THE SYSTEM KNOWS WHICH WORD FILLS WHICH SLOT:
    
    1. Look at the Output Contract order (Left-to-Right):
       Slot #1 is 'greeting'  |  Slot #2 is 'name'
       
    2. Look at the return line order (Left-to-Right):
       Item #1 is 'word1'     |  Item #2 is 'word2'
       
    Python matches them up strictly by their position in line:
       Item #1 (word1) automatically pours into Slot #1 (greeting)
       Item #2 (word2) automatically pours into Slot #2 (name)
    """
    word1 = "Hello"
    word2 = "Gaurav"
    
    # Position #1 is word1 ("Hello"). Position #2 is word2 ("Gaurav").
    return (word1, word2)


# ==============================================================================
# STEP 2: BUILD THE SENTENCE (Takes TWO inputs, generates ONE single output)
# ==============================================================================
@dsl.component(base_image="python:3.11-slim")
def build_sentence(greeting: str, name: str) -> str:
    """
    Inputs: 'greeting' and 'name' are filled by the pipeline conveyor belt.
    Output: Returns a single finished text string back to the pipeline.
    """
    sentence = f"{greeting}, {name}! Welcome to OpenShift AI."
    return sentence


# ==============================================================================
# STEP 3: THE PIPELINE ORCHESTRATION (The Conveyor Belt)
# ==============================================================================
@dsl.pipeline(name="greeting-pipeline")
def greeting_pipeline():
    
    # LINE A: We run the first component and name its tracking container 'step1'
    step1 = create_words()
    
    # LINE B: We run the second component and fill its input variables.
    # Because 'step1' has multiple outputs, we look inside 'step1.outputs'
    # and use brackets [""] to grab the exact named keys we mapped in Step 1.
    step2 = build_sentence(
        greeting=step1.outputs["greeting"], 
        name=step1.outputs["name"]
    )


# ==============================================================================
# STEP 4: COMPILATION (Building the Blueprint)
# ==============================================================================
if __name__ == "__main__":
    # Compiles our Python structure into the 'greeting_pipeline.yaml' file
    compiler.Compiler().compile(greeting_pipeline, "greeting_pipeline.yaml")
    print("\n>>> Success! 'greeting_pipeline.yaml' has been generated. <<<")

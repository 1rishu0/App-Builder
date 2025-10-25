# Here we store all the schema for all the agents
# Pydantic model → used to define data structures with automatic validation and type checking.
# ConfigDict → used to configure model behavior because with having this in class you can add additional element outside the class
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

class File(BaseModel):

    path: str = Field(description="The path of the file to be created or modified")

    purpose: str = Field(
        description="The Purpose of the file, e.g. 'main application logic', 'data processing module', etc."
    )

# this is the schema which is used for planner agent to build a plan with this 5 elements
# files element in plan class require list of File class now which hold itself two more element for files
class Plan(BaseModel):

    name: str = Field(description="The name of the app to be build")

    description: str = Field(description="A oneline description of the app to be built, e.g. 'A web application for managing personal finances'")

    techstack: str = Field(description="The tech stack to be used for the app, e.g. 'python', 'javascript', 'react', 'flask', etc.")

    features: list[str] = Field(description="A list of features that the app should have, e.g. 'user authentication', 'data visualization', etc.")

    files: list[File] = Field(description="A list of Files to be created, each with 'path' and 'purpose'")

# this class is used for the task description of the particular filepath
class ImplementationTask(BaseModel):

    filepath: str = Field(description="The path to the file to be modified")

    task_description: str = Field(description="A description of the task to be performed on the file, e.g. 'add user authentication', 'implement data processing logic', etc.")

# this is the schema class for the architect agent
class TaskPlan(BaseModel):

    implementation_steps: list[ImplementationTask] = Field(description="A list of Steps to be taken to implement the task")

    # the model will accept extra fields not defined in the model schema, instead of raising an error.
    model_config = ConfigDict(extra="allow")

# define a data model called CoderState using Pydantic's BaseModel for validation and structure
class CoderState(BaseModel):

    # stores the complete plan (of type TaskPlan) that describes what tasks need to be implemented
    task_plan: TaskPlan = Field(description="The plan for the task to be implemented")

    # keeps track of which step (by index) in the implementation sequence the coder is currently working on
    current_step_idx: int = Field(0, description="The index of the current step in the implementation steps")

    # Optionally stores the text/content of the file being edited or created during the current step
    current_file_content: Optional[str] = Field(
        None, description="The content of the file currently being edited or created"
    )
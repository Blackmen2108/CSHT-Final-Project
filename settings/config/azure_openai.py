from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class AzureOpenAISettings(BaseSettings):
    azure_open_ai__api_key: Optional[str] = Field(
        ...,
        env="AZURE_OPEN_AI__API_KEY",
        description="Azure OpenAI API Key",
        frozen=True,
    )
    azure_open_ai__endpoint: Optional[str] = Field(
        ...,
        env="AZURE_OPEN_AI__ENDPOINT",
        description="Azure OpenAI Endpoints",
        frozen=True,
    )
    azure_open_ai__chat_completion_deployment_name: Optional[str] = Field(
        ...,
        env="AZURE_OPEN_AI__CHAT_COMPLETION_DEPLOYMENT_NAME",
        description="Deployment name of the API",
        frozen=True,
    )
    # azure_open_ai__chat_completion_deployment_name_long: Optional[str] = Field(
    #     ...,
    #     env="AZURE_OPEN_AI__CHAT_COMPLETION_DEPLOYMENT_NAME_LONG",
    #     description="Deployment name of the API for long output model",
    #     frozen=True,
    # )
    # prompt_template: Optional[str] = Field(
    #     ..., env="PROMPT_TEMPLATE", description="Prompt Template", frozen=True
    # )
    number_of_tries_gpt: Optional[int] = Field(
        ...,
        env="NUMBER_OF_TRIES_GPT",
        description="Number of tries to get the response from GPT",
        frozen=True,
    )

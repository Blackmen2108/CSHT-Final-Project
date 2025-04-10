from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings

class AzureBlobStorageSettings(BaseSettings):
    blob_container_name: str = Field(..., env='BLOB_CONTAINER_NAME', description="Azure Blob Container folder that use to store the document", frozen=True)
    blob_connection_string: str = Field(..., env='BLOB_CONNECTION_STRING', description="Connecion string to Azure Blob Storage", frozen=True)
    blob_account_key: str = Field(..., env='BLOB_ACCOUNT_KEY', description="Account Key taken from connection string to generate SAS", frozen=True)
    blob_account_name: str = Field(..., env='BLOB_ACCOUNT_NAME', description="Account name taken from connection string to generate SAS", frozen=True)
    valid_file_type: List[str] = Field(..., env='VALID_FILE_TYPE', description="Valid file type use for upload process", frozen=True)
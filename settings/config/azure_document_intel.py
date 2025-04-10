from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class AzureDocumentIntelligenceSettings(BaseSettings):
    document_intelligence_api_key: Optional[str] = Field(..., env='DOCUMENT_INTELLIGENCE_API_KEY', description="Azure Blob Container folder that use to store the document", frozen=True)
    document_intelligence_domain_url: Optional[str] = Field(..., env='DOCUMENT_INTELLIGENCE_DOMAIN_URL', description="Connecion string to Azure Blob Storage", frozen=True)
    classification_model: Optional[str] = Field(..., env='CLASSIFICATION_MODEL', description="Model used to classify the document", frozen=True)
    analyze_model: Optional[str] = Field(..., env='ANALYZE_MODEL', description="Model used to analyze the document", frozen=True)
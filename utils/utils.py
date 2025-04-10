import datetime
import hashlib
from urllib.parse import unquote
from azure.storage.blob import BlobClient, BlobSasPermissions, generate_blob_sas
from settings.settings import azure_settings
from settings.invalid_config_exception import InvalidConfigException
import magic


class Utilities:
    @staticmethod
    def get_hash(data_bytes: bytes, suffix: str = "", extension: str = "") -> str:
        sha1 = hashlib.sha1(usedforsecurity=False)
        sha1.update(data_bytes)
        return sha1.hexdigest() + suffix + extension

    @staticmethod
    def generate_sas_token(url: str, container_name: str, blob_name: str) -> str:
        # Create a SAS token that's valid for a certain time and for particular blob only
        blob_client = BlobClient.from_connection_string(
            conn_str=azure_settings.blob.blob_connection_string,
            container_name=container_name,
            blob_name=blob_name,
        )
        # Start time will subtract by 15 seconds to deal with fluctuation between time server
        # If dont have 15 seconds minus, sometime server time will run behind actual start time -> error
        start_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
            seconds=60
        )
        # Expiry time will be 1 hour for the blob
        expiry_time = start_time + datetime.timedelta(hours=1)
        blob_name = blob_client.blob_name
        # Unquote due to SAS token
        blob_name = unquote(blob_name)

        # FUTURE WORK: need some try catch to cater for unable to create token cases. First one need to be ValueError
        # Consider to remove list=True since each token only need read only for that blob
        sas_token = generate_blob_sas(
            account_name=azure_settings.blob.blob_account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=azure_settings.blob.blob_account_key,
            permission=BlobSasPermissions(read=True, list=True),
            expiry=expiry_time,
            start=start_time,
        )

        return sas_token

    @staticmethod
    def get_content_type(file_bytes: bytes) -> str:
        """Use libmagic wrapper to guess the MimeType/FileType of the bytes stream

        Args:
            file_bytes (bytes): Bytes stream of a file

        Returns:
            str: MimeType, i.e. content type
        """
        return magic.from_buffer(
            file_bytes,
            mime=True,
        )

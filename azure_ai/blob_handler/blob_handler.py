from io import BytesIO
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError, ResourceExistsError, ResourceNotFoundError
from settings.settings import azure_settings
from settings.custom_logger import Logger

class AzureBlobStorageHandler:
    def __init__(self):
        self.logger = Logger(self.__class__.__name__)
        self.__blob_service_client = BlobServiceClient.from_connection_string(
            conn_str=azure_settings.blob.blob_connection_string
        )

    def check_exists(
        self, blob_name: str, container_name: str, extension_name: str
    ) -> str | None:
        """
        Check if a blob exists in the specified container.

        Args:
            blob_name (str): The name of the blob to check, without extension
            container_name (str): The name of the container to check in
            extension_name (str): The file extension to append to the blob name

        Returns:
            str | None: The URL of the blob if it exists, None otherwise
        """
        container_client = self.__blob_service_client.get_container_client(
            container=container_name
        )
        name = f"{blob_name}.{extension_name}"
        blob_client = container_client.get_blob_client(blob=name)
        if blob_client.exists():
            return blob_client.url

        return None

    def upload_blob_file(
        self,
        blob_name: str,
        container_name: str,
        content: str | bytes,
        extension: str = "txt",
        timeout: int = 120,
        overwrite: bool = False,
        skip_if_existed: bool = False,
        **kwargs,
    ) -> str | None:
        """
        Uploads a file to the specified container in the blob storage.

        Args:
            file_path (str): The path to the file to be uploaded.
            container_name (str): The name of the container where the file will be uploaded.
            blob_name (str, optional): The name of the blob. If not provided, an uuid will
                be provided with file_type as name. Defaults to None.
            overwrite (bool, optional): Indicates whether to overwrite an existing blob with
                the same name. Defaults to False.
            metadata (Dict[str, str], optional): Additional metadata to be associated with the
                blob. Defaults to {"version": "experiment"}.
            timeout (int, optional): The timeout for the upload operation. Defaults to 120 seconds.
            skip_if_existed (bool, optional): Indicates whether to skip upload if the blob
                already exists. Defaults to False.
            **kwargs: Additional keyword arguments. Currently supports "additional_sas" to
                specify path to generate sas if sas is require.

        Returns:
            str | None: The URL of the uploaded blob, or None if the upload fails.
        """
        # Get size of content in MB

        if skip_if_existed:
            blob_url = self.check_exists(blob_name, container_name, extension)
            if blob_url:
                return blob_url

        try:
            if isinstance(content, BytesIO):
                content_size_mb = content.getbuffer().nbytes / (1024 * 1024)
            else:
                content_size_mb = len(content.encode("utf-8")) / (1024 * 1024)

            self.logger.info(f"Content size: {content_size_mb:.2f} MB")
        except AttributeError:
            self.logger.debug(
                f"Content is not a BytesIO or string, skip content size calculation"
            )

        if type(content) == bytes:
            str_bytes = content
        else:
            str_bytes = bytes(str(content), "utf-8")

        container_client = self.__blob_service_client.get_container_client(
            container=container_name
        )
        blob_client = ""
        blob_name = f"{blob_name}.{extension}"
        try:
            blob_client = container_client.upload_blob(
                name=blob_name,
                data=str_bytes,
                blob_type="BlockBlob",
                overwrite=overwrite,
                connection_timeout=timeout,
            )
            self.logger.info(f"Uploaded {blob_name} to container {container_name}")
            # If specify additional_sas -> will return url with sas
            if "additional_sas" in kwargs:
                full_container_name = (
                    container_name + f"/{kwargs.get('additional_sas')}"
                )
                sas_key = f"{blob_client.url}?{self.__create_service_sas_blob(url=blob_client.url, container_name=full_container_name)}"
                return sas_key
            return blob_client.url
        except ResourceExistsError as e:  # File Already exist in blob storage
            if skip_if_existed:
                blob_client = container_client.get_blob_client(blob=blob_name)
                return blob_client.url

            self.logger.warning(
                f"Blob {blob_name} for container {container_name} already exists:\n {str(e)}"
            )
        except ResourceNotFoundError as e:  # Container do not exist
            self.logger.warning(f"Container or blob not found: {str(e)}")
        except AzureError as e:  # General Azure Error
            import traceback

            self.logger.error(f"Azure error occurred: {str(e)}")
            self.logger.error(f"Exception error: {traceback.format_exc()}")
            self.logger.error(f"File {blob_name} will not be uploaded!!!!")
        except Exception as e:  # Catch master exception to make sure program continue
            import traceback

            self.logger.error(
                f"An exception happened while trying to upload file to container {container_name} with blob_name {blob_name}"
            )
            self.logger.error(f"Exception error: {traceback.format_exc()}")
            self.logger.error(f"File {blob_name} will not be uploaded!!!!")
        return None

    def download_blob_file(self, blob_name: str, container_name: str) -> bytes | None:
        container_client = self.__blob_service_client.get_container_client(
            container=container_name
        )
        blob_client = container_client.get_blob_client(blob=blob_name)
        try:
            blob_url = blob_client.url
            blob_name = blob_client.blob_name
            file = blob_name.split('/')[-1]
            file_type = blob_name.split('.')[-1]
            file_path = f"data/{file}"
            with open(file_path, "wb") as f:
                f.write(blob_client.download_blob().readall())
            if "cds" in blob_name:
                return {"project_name": "cds wiki", "file": blob_name, "original_url": blob_url, "document_type": file_type, "file_path": file_path}
            elif "Toll Gates" in blob_name:
                return {"project_name": "toll gates", "file": blob_name, "original_url": blob_url, "document_type": file_type, "file_path": file_path}
        except ResourceNotFoundError as e:
            self.logger.warning(
                f"Blob name {blob_name} not found in container {container_name}:\n {str(e)}"
            )
        return None

    def get_list_files(self, container_name: str) -> list[str]:
        container_client = self.__blob_service_client.get_container_client(
            container=container_name
        )
        # TODO: Since list_blobs() is paginated, we need to loop through all blobs
        # to get all file names. Find a better way to do this.
        return [blob.name for blob in container_client.list_blobs()]
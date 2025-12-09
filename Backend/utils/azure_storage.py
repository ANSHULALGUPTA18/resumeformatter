"""
Azure Blob Storage Integration for Persistent Data Storage
Stores templates, CAI contacts, and other data in Azure Blob Storage
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AzureStorageManager:
    """
    Manages persistent storage in Azure Blob Storage
    Handles templates, CAI contacts, and other application data
    """
    
    def __init__(self):
        """Initialize Azure Storage Manager"""
        # Get connection string from environment variables
        self.connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        
        if not self.connection_string:
            logger.warning("AZURE_STORAGE_CONNECTION_STRING not found. Using local storage fallback.")
            self.blob_service_client = None
            self.use_local_fallback = True
        else:
            try:
                self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
                self.use_local_fallback = False
                logger.info("✅ Azure Blob Storage connected successfully")
            except Exception as e:
                logger.error(f"❌ Failed to connect to Azure Blob Storage: {e}")
                self.blob_service_client = None
                self.use_local_fallback = True
        
        # Container names
        self.templates_container = "templates"
        self.cai_contacts_container = "cai-contacts"
        self.data_container = "app-data"
        
        # Initialize containers
        if not self.use_local_fallback:
            self._ensure_containers_exist()
    
    def _ensure_containers_exist(self):
        """Ensure all required containers exist"""
        containers = [self.templates_container, self.cai_contacts_container, self.data_container]
        
        for container_name in containers:
            try:
                container_client = self.blob_service_client.get_container_client(container_name)
                container_client.create_container()
                logger.info(f"✅ Created container: {container_name}")
            except ResourceExistsError:
                logger.info(f"✅ Container already exists: {container_name}")
            except Exception as e:
                logger.error(f"❌ Failed to create container {container_name}: {e}")
    
    def _get_local_fallback_path(self, container: str, blob_name: str) -> str:
        """Get local file path for fallback storage"""
        base_dir = os.path.expanduser("~/.resume_formatter_storage")
        os.makedirs(os.path.join(base_dir, container), exist_ok=True)
        return os.path.join(base_dir, container, blob_name)
    
    # ===== TEMPLATE STORAGE =====
    
    def upload_template_file(self, template_id: str, file_path: str, filename: str) -> bool:
        """
        Upload template file to Azure Blob Storage
        
        Args:
            template_id: Unique template identifier
            file_path: Local path to template file
            filename: Original filename
            
        Returns:
            bool: Success status
        """
        blob_name = f"{template_id}/{filename}"
        
        if self.use_local_fallback:
            # Local fallback
            try:
                local_path = self._get_local_fallback_path(self.templates_container, blob_name)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                import shutil
                shutil.copy2(file_path, local_path)
                logger.info(f"✅ Template stored locally: {blob_name}")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to store template locally: {e}")
                return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.templates_container, 
                blob=blob_name
            )
            
            with open(file_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True)
            
            logger.info(f"✅ Template uploaded to Azure: {blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to upload template: {e}")
            return False
    
    def download_template_file(self, template_id: str, filename: str, local_path: str) -> bool:
        """
        Download template file from Azure Blob Storage
        
        Args:
            template_id: Unique template identifier
            filename: Original filename
            local_path: Where to save the file locally
            
        Returns:
            bool: Success status
        """
        blob_name = f"{template_id}/{filename}"
        
        if self.use_local_fallback:
            # Local fallback
            try:
                source_path = self._get_local_fallback_path(self.templates_container, blob_name)
                if os.path.exists(source_path):
                    import shutil
                    shutil.copy2(source_path, local_path)
                    logger.info(f"✅ Template retrieved locally: {blob_name}")
                    return True
                else:
                    logger.warning(f"⚠️ Template not found locally: {blob_name}")
                    return False
            except Exception as e:
                logger.error(f"❌ Failed to retrieve template locally: {e}")
                return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.templates_container, 
                blob=blob_name
            )
            
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            with open(local_path, 'wb') as download_file:
                download_file.write(blob_client.download_blob().readall())
            
            logger.info(f"✅ Template downloaded from Azure: {blob_name}")
            return True
            
        except ResourceNotFoundError:
            logger.warning(f"⚠️ Template not found in Azure: {blob_name}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to download template: {e}")
            return False
    
    def delete_template_file(self, template_id: str, filename: str) -> bool:
        """Delete template file from storage"""
        blob_name = f"{template_id}/{filename}"
        
        if self.use_local_fallback:
            try:
                local_path = self._get_local_fallback_path(self.templates_container, blob_name)
                if os.path.exists(local_path):
                    os.remove(local_path)
                    # Remove directory if empty
                    try:
                        os.rmdir(os.path.dirname(local_path))
                    except OSError:
                        pass  # Directory not empty
                logger.info(f"✅ Template deleted locally: {blob_name}")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to delete template locally: {e}")
                return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.templates_container, 
                blob=blob_name
            )
            blob_client.delete_blob()
            logger.info(f"✅ Template deleted from Azure: {blob_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete template: {e}")
            return False
    
    def upload_thumbnail(self, template_id: str, thumbnail_path: str) -> bool:
        """
        Upload thumbnail image to Azure Blob Storage
        
        Args:
            template_id: Unique template identifier
            thumbnail_path: Local path to thumbnail file
            
        Returns:
            bool: Success status
        """
        blob_name = f"{template_id}/thumbnail.png"
        
        if self.use_local_fallback:
            try:
                local_path = self._get_local_fallback_path(self.templates_container, blob_name)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                import shutil
                shutil.copy2(thumbnail_path, local_path)
                logger.info(f"✅ Thumbnail stored locally: {blob_name}")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to store thumbnail locally: {e}")
                return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.templates_container, 
                blob=blob_name
            )
            
            with open(thumbnail_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True)
            
            logger.info(f"✅ Thumbnail uploaded to Azure: {blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to upload thumbnail: {e}")
            return False
    
    def download_thumbnail(self, template_id: str, local_path: str) -> bool:
        """
        Download thumbnail from Azure Blob Storage
        
        Args:
            template_id: Unique template identifier
            local_path: Where to save the thumbnail locally
            
        Returns:
            bool: Success status
        """
        blob_name = f"{template_id}/thumbnail.png"
        
        if self.use_local_fallback:
            try:
                source_path = self._get_local_fallback_path(self.templates_container, blob_name)
                if os.path.exists(source_path):
                    import shutil
                    shutil.copy2(source_path, local_path)
                    logger.info(f"✅ Thumbnail retrieved locally: {blob_name}")
                    return True
                else:
                    logger.warning(f"⚠️ Thumbnail not found locally: {blob_name}")
                    return False
            except Exception as e:
                logger.error(f"❌ Failed to retrieve thumbnail locally: {e}")
                return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.templates_container, 
                blob=blob_name
            )
            
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            with open(local_path, 'wb') as download_file:
                download_file.write(blob_client.download_blob().readall())
            
            logger.info(f"✅ Thumbnail downloaded from Azure: {blob_name}")
            return True
            
        except ResourceNotFoundError:
            logger.warning(f"⚠️ Thumbnail not found in Azure: {blob_name}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to download thumbnail: {e}")
            return False
    
    def thumbnail_exists(self, template_id: str) -> bool:
        """
        Check if thumbnail exists in storage
        
        Args:
            template_id: Unique template identifier
            
        Returns:
            bool: True if thumbnail exists
        """
        blob_name = f"{template_id}/thumbnail.png"
        
        if self.use_local_fallback:
            local_path = self._get_local_fallback_path(self.templates_container, blob_name)
            return os.path.exists(local_path)
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.templates_container, 
                blob=blob_name
            )
            return blob_client.exists()
        except Exception as e:
            logger.error(f"❌ Failed to check thumbnail existence: {e}")
            return False
    
    def delete_thumbnail(self, template_id: str) -> bool:
        """
        Delete thumbnail from storage
        
        Args:
            template_id: Unique template identifier
            
        Returns:
            bool: Success status
        """
        blob_name = f"{template_id}/thumbnail.png"
        
        if self.use_local_fallback:
            try:
                local_path = self._get_local_fallback_path(self.templates_container, blob_name)
                if os.path.exists(local_path):
                    os.remove(local_path)
                    logger.info(f"✅ Thumbnail deleted locally: {blob_name}")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to delete thumbnail locally: {e}")
                return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.templates_container, 
                blob=blob_name
            )
            blob_client.delete_blob()
            logger.info(f"✅ Thumbnail deleted from Azure: {blob_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete thumbnail: {e}")
            return False
    
    # ===== CAI CONTACTS STORAGE =====
    
    def save_cai_contact(self, contact_data: Dict[str, Any]) -> bool:
        """
        Save CAI contact data to persistent storage
        
        Args:
            contact_data: Contact information dictionary
            
        Returns:
            bool: Success status
        """
        blob_name = "cai_contact.json"
        
        if self.use_local_fallback:
            try:
                local_path = self._get_local_fallback_path(self.cai_contacts_container, blob_name)
                with open(local_path, 'w', encoding='utf-8') as f:
                    json.dump(contact_data, f, ensure_ascii=False, indent=2)
                logger.info("✅ CAI contact saved locally")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to save CAI contact locally: {e}")
                return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.cai_contacts_container, 
                blob=blob_name
            )
            
            json_data = json.dumps(contact_data, ensure_ascii=False, indent=2)
            blob_client.upload_blob(json_data.encode('utf-8'), overwrite=True)
            
            logger.info("✅ CAI contact saved to Azure")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save CAI contact: {e}")
            return False
    
    def get_cai_contact(self) -> Dict[str, Any]:
        """
        Get CAI contact data from persistent storage
        
        Returns:
            Dict: Contact information or empty dict if not found
        """
        blob_name = "cai_contact.json"
        default_contact = {"name": "", "phone": "", "email": ""}
        
        if self.use_local_fallback:
            try:
                local_path = self._get_local_fallback_path(self.cai_contacts_container, blob_name)
                if os.path.exists(local_path):
                    with open(local_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    logger.info("✅ CAI contact retrieved locally")
                    return data
                else:
                    logger.info("ℹ️ No CAI contact found locally")
                    return default_contact
            except Exception as e:
                logger.error(f"❌ Failed to retrieve CAI contact locally: {e}")
                return default_contact
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.cai_contacts_container, 
                blob=blob_name
            )
            
            blob_data = blob_client.download_blob().readall()
            contact_data = json.loads(blob_data.decode('utf-8'))
            
            logger.info("✅ CAI contact retrieved from Azure")
            return contact_data
            
        except ResourceNotFoundError:
            logger.info("ℹ️ No CAI contact found in Azure")
            return default_contact
        except Exception as e:
            logger.error(f"❌ Failed to retrieve CAI contact: {e}")
            return default_contact
    
    # ===== TEMPLATE METADATA STORAGE =====
    
    def save_template_metadata(self, templates_data: List[Dict[str, Any]]) -> bool:
        """
        Save template metadata to persistent storage
        
        Args:
            templates_data: List of template metadata dictionaries
            
        Returns:
            bool: Success status
        """
        blob_name = "templates_metadata.json"
        
        # Add timestamp
        metadata = {
            "last_updated": datetime.now().isoformat(),
            "templates": templates_data
        }
        
        if self.use_local_fallback:
            try:
                local_path = self._get_local_fallback_path(self.data_container, blob_name)
                with open(local_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                logger.info("✅ Template metadata saved locally")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to save template metadata locally: {e}")
                return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.data_container, 
                blob=blob_name
            )
            
            json_data = json.dumps(metadata, ensure_ascii=False, indent=2)
            blob_client.upload_blob(json_data.encode('utf-8'), overwrite=True)
            
            logger.info("✅ Template metadata saved to Azure")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save template metadata: {e}")
            return False
    
    def get_template_metadata(self) -> List[Dict[str, Any]]:
        """
        Get template metadata from persistent storage
        
        Returns:
            List: Template metadata or empty list if not found
        """
        blob_name = "templates_metadata.json"
        
        if self.use_local_fallback:
            try:
                local_path = self._get_local_fallback_path(self.data_container, blob_name)
                if os.path.exists(local_path):
                    with open(local_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    logger.info("✅ Template metadata retrieved locally")
                    return metadata.get("templates", [])
                else:
                    logger.info("ℹ️ No template metadata found locally")
                    return []
            except Exception as e:
                logger.error(f"❌ Failed to retrieve template metadata locally: {e}")
                return []
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.data_container, 
                blob=blob_name
            )
            
            blob_data = blob_client.download_blob().readall()
            metadata = json.loads(blob_data.decode('utf-8'))
            
            logger.info("✅ Template metadata retrieved from Azure")
            return metadata.get("templates", [])
            
        except ResourceNotFoundError:
            logger.info("ℹ️ No template metadata found in Azure")
            return []
        except Exception as e:
            logger.error(f"❌ Failed to retrieve template metadata: {e}")
            return []
    
    # ===== UTILITY METHODS =====
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test Azure Storage connection
        
        Returns:
            Dict: Connection status and details
        """
        if self.use_local_fallback:
            return {
                "connected": False,
                "storage_type": "local_fallback",
                "message": "Using local storage fallback",
                "containers": ["local filesystem"]
            }
        
        try:
            # List containers to test connection
            containers = []
            for container in self.blob_service_client.list_containers():
                containers.append(container.name)
            
            return {
                "connected": True,
                "storage_type": "azure_blob",
                "message": "Successfully connected to Azure Blob Storage",
                "containers": containers
            }
            
        except Exception as e:
            return {
                "connected": False,
                "storage_type": "azure_blob",
                "message": f"Failed to connect: {str(e)}",
                "containers": []
            }


# Singleton instance
_storage_manager = None

def get_storage_manager() -> AzureStorageManager:
    """Get or create the singleton storage manager"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = AzureStorageManager()
    return _storage_manager

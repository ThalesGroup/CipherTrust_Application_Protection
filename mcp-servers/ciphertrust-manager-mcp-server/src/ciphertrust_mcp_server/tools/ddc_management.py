from typing import Optional
from pydantic import BaseModel
from .base import BaseTool

# --- SYSTEM ---
class DDCSystemParams(BaseModel):
    domain: Optional[str] = None
    auth_domain: Optional[str] = None

# --- LICENSE ---
class DDCLicenseParams(BaseModel):
    domain: Optional[str] = None
    auth_domain: Optional[str] = None

class DDCLicenseInfoParams(BaseModel):
    domain: Optional[str] = None
    auth_domain: Optional[str] = None

# --- SETTINGS ---
class DDCSettingsParams(BaseModel):
    domain: Optional[str] = None
    auth_domain: Optional[str] = None

# --- SETTINGS HDFS ---
class DDCSettingsHDFSGetParams(BaseModel):
    domain: Optional[str] = None
    auth_domain: Optional[str] = None

class DDCSettingsHDFSModifyParams(BaseModel):
    hadoop_connection_id: Optional[str] = None
    folder: Optional[str] = None
    hdfs_uri: Optional[str] = None
    jsonfile: Optional[str] = None
    domain: Optional[str] = None
    auth_domain: Optional[str] = None

# --- SETTINGS LIVY ---
class DDCSettingsLivyGetParams(BaseModel):
    domain: Optional[str] = None
    auth_domain: Optional[str] = None

class DDCSettingsLivyModifyParams(BaseModel):
    hadoop_connection_id: Optional[str] = None
    livy_uri: Optional[str] = None
    jsonfile: Optional[str] = None
    domain: Optional[str] = None
    auth_domain: Optional[str] = None

# --- RAW DATA ---
class DDCRawDataDecryptParams(BaseModel):
    input: str
    output: Optional[str] = None
    domain: Optional[str] = None
    auth_domain: Optional[str] = None

# --- COUNTRIES ---
class DDCCountriesListParams(BaseModel):
    id: Optional[str] = None
    limit: Optional[int] = None
    name: Optional[str] = None
    skip: Optional[int] = None
    domain: Optional[str] = None
    auth_domain: Optional[str] = None

class DDCManagementTool(BaseTool):
    name = "ddc_management"
    description = "Manage Data Discovery resources, settings, and reports."

    def get_schema(self):
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": [
                    "system", "license", "license_info", "settings", "settings_hdfs_get", "settings_hdfs_modify", "settings_livy_get", "settings_livy_modify", "raw_data_decrypt", "countries_list"
                ]},
                "hadoop_connection_id": {"type": "string", "nullable": True},
                "folder": {"type": "string", "nullable": True},
                "hdfs_uri": {"type": "string", "nullable": True},
                "livy_uri": {"type": "string", "nullable": True},
                "jsonfile": {"type": "string", "nullable": True},
                "input": {"type": "string", "nullable": True},
                "output": {"type": "string", "nullable": True},
                "id": {"type": "string", "nullable": True},
                "limit": {"type": "integer", "nullable": True},
                "name": {"type": "string", "nullable": True},
                "skip": {"type": "integer", "nullable": True},
                **self.get_domain_auth_params(),
            },
            "required": ["action"],
        }

    async def execute(self, **kwargs):
        action = kwargs.get("action")
        if action == "system":
            params = DDCSystemParams(**kwargs)
            cmd = ["ddc", "system"]
            self.add_domain_auth_params(cmd, kwargs)
            return self.execute_command(cmd)
        elif action == "license":
            params = DDCLicenseParams(**kwargs)
            cmd = ["ddc", "license"]
            self.add_domain_auth_params(cmd, kwargs)
            return self.execute_command(cmd)
        elif action == "license_info":
            params = DDCLicenseInfoParams(**kwargs)
            cmd = ["ddc", "license", "info"]
            self.add_domain_auth_params(cmd, kwargs)
            return self.execute_command(cmd)
        elif action == "settings":
            params = DDCSettingsParams(**kwargs)
            cmd = ["ddc", "settings"]
            self.add_domain_auth_params(cmd, kwargs)
            return self.execute_command(cmd)
        elif action == "settings_hdfs_get":
            params = DDCSettingsHDFSGetParams(**kwargs)
            cmd = ["ddc", "settings", "hdfs", "get"]
            self.add_domain_auth_params(cmd, kwargs)
            return self.execute_command(cmd)
        elif action == "settings_hdfs_modify":
            params = DDCSettingsHDFSModifyParams(**kwargs)
            cmd = ["ddc", "settings", "hdfs", "modify"]
            if params.hadoop_connection_id:
                cmd += ["--hadoop-connection-id", params.hadoop_connection_id]
            if params.folder:
                cmd += ["--folder", params.folder]
            if params.hdfs_uri:
                cmd += ["--hdfs-uri", params.hdfs_uri]
            if params.jsonfile:
                cmd += ["--jsonfile", params.jsonfile]
            self.add_domain_auth_params(cmd, kwargs)
            return self.execute_command(cmd)
        elif action == "settings_livy_get":
            params = DDCSettingsLivyGetParams(**kwargs)
            cmd = ["ddc", "settings", "livy", "get"]
            self.add_domain_auth_params(cmd, kwargs)
            return self.execute_command(cmd)
        elif action == "settings_livy_modify":
            params = DDCSettingsLivyModifyParams(**kwargs)
            cmd = ["ddc", "settings", "livy", "modify"]
            if params.hadoop_connection_id:
                cmd += ["--hadoop-connection-id", params.hadoop_connection_id]
            if params.livy_uri:
                cmd += ["--livy-uri", params.livy_uri]
            if params.jsonfile:
                cmd += ["--jsonfile", params.jsonfile]
            self.add_domain_auth_params(cmd, kwargs)
            return self.execute_command(cmd)
        elif action == "raw_data_decrypt":
            params = DDCRawDataDecryptParams(**kwargs)
            cmd = ["ddc", "raw-data", "decrypt", "--input", params.input]
            if params.output:
                cmd += ["--output", params.output]
            self.add_domain_auth_params(cmd, kwargs)
            return self.execute_command(cmd)
        elif action == "countries_list":
            params = DDCCountriesListParams(**kwargs)
            cmd = ["ddc", "countries", "list"]
            if params.id:
                cmd += ["--id", params.id]
            if params.limit is not None:
                cmd += ["--limit", str(params.limit)]
            if params.name:
                cmd += ["--name", params.name]
            if params.skip is not None:
                cmd += ["--skip", str(params.skip)]
            self.add_domain_auth_params(cmd, kwargs)
            return self.execute_command(cmd)
        else:
            return f"Unknown action: {action}"

DDC_MANAGEMENT_TOOLS = [DDCManagementTool] 
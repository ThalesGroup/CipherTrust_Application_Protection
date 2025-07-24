"""Network diagnostic tools for CipherTrust Manager."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


class NetworkPingParams(BaseModel):
    """Parameters for network ping."""
    destination: str = Field(..., description="Destination hostname or IP address to ping")
    interface: Optional[str] = Field(None, description="Network interface to use for communication")
    count: Optional[int] = Field(None, description="Count of packets to send to remote host")
    timeout_secs: Optional[int] = Field(None, description="Time to wait for response from host system")
    ipv4: bool = Field(False, description="Use IPv4 for communication")
    ipv6: bool = Field(False, description="Use IPv6 for communication")


class NetworkCheckPortParams(BaseModel):
    """Parameters for network port check."""
    destination: str = Field(..., description="Destination hostname or IP address")
    port: int = Field(..., description="Port to check accessibility")
    interface: Optional[str] = Field(None, description="Network interface to use for communication")
    timeout_secs: Optional[int] = Field(None, description="Time to wait for response from host system")
    ipv4: bool = Field(False, description="Use IPv4 for communication")
    ipv6: bool = Field(False, description="Use IPv6 for communication")


class NetworkLookupParams(BaseModel):
    """Parameters for network lookup."""
    target: str = Field(..., description="IP address or hostname to lookup")


class NetworkTracerouteParams(BaseModel):
    """Parameters for network traceroute."""
    destination: str = Field(..., description="Destination hostname or IP address to trace")
    first: Optional[int] = Field(None, description="Start from the first_ttl hop")
    interface: Optional[str] = Field(None, description="Network interface to use for communication")
    ipv4: bool = Field(False, description="Use IPv4 for communication")
    ipv6: bool = Field(False, description="Use IPv6 for communication")
    max_hops: Optional[int] = Field(None, description="Maximum number of hops to search for target")
    port: Optional[int] = Field(None, description="Port to access")
    queries: Optional[int] = Field(None, description="Number of probes per each hop")
    send_wait: Optional[int] = Field(None, description="Minimal time interval between probes")
    tcp: bool = Field(False, description="Use TCP SYN for tracerouting")
    udp: bool = Field(False, description="Use UDP to particular port for tracerouting")


class NetworkInterfacesListParams(BaseModel):
    """Parameters for listing network interfaces."""
    # No parameters needed for interfaces list
    pass


class NetworkManagementTool(BaseTool):
    name = "network_management"
    description = "Network management operations (ping, checkport, lookup, traceroute, interfaces_list)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["ping", "checkport", "lookup", "traceroute", "interfaces_list"]},
                **NetworkPingParams.model_json_schema()["properties"],
                **NetworkCheckPortParams.model_json_schema()["properties"],
                **NetworkLookupParams.model_json_schema()["properties"],
                **NetworkTracerouteParams.model_json_schema()["properties"],
                **NetworkInterfacesListParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, action: str, **kwargs: Any) -> Any:
        if action == "ping":
            params = NetworkPingParams(**kwargs)
            if params.ipv4 and params.ipv6:
                raise ValueError("Cannot specify both IPv4 and IPv6 options")
            args = ["network", "ping", "--destination", params.destination]
            if params.interface:
                args.extend(["--interface", params.interface])
            if params.count is not None:
                args.extend(["--count", str(params.count)])
            if params.timeout_secs is not None:
                args.extend(["--timeout-secs", str(params.timeout_secs)])
            if params.ipv4:
                args.append("--ipv4")
            elif params.ipv6:
                args.append("--ipv6")
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "checkport":
            params = NetworkCheckPortParams(**kwargs)
            if params.ipv4 and params.ipv6:
                raise ValueError("Cannot specify both IPv4 and IPv6 options")
            args = ["network", "checkport", "--destination", params.destination, "--port", str(params.port)]
            if params.interface:
                args.extend(["--interface", params.interface])
            if params.timeout_secs is not None:
                args.extend(["--timeout-secs", str(params.timeout_secs)])
            if params.ipv4:
                args.append("--ipv4")
            elif params.ipv6:
                args.append("--ipv6")
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "lookup":
            params = NetworkLookupParams(**kwargs)
            args = ["network", "lookup", "--target", params.target]
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "traceroute":
            params = NetworkTracerouteParams(**kwargs)
            if params.ipv4 and params.ipv6:
                raise ValueError("Cannot specify both IPv4 and IPv6 options")
            if params.tcp and params.udp:
                raise ValueError("Cannot specify both TCP and UDP options")
            args = ["network", "traceroute", "--destination", params.destination]
            if params.first is not None:
                args.extend(["--first", str(params.first)])
            if params.interface:
                args.extend(["--interface", params.interface])
            if params.max_hops is not None:
                args.extend(["--max-hops", str(params.max_hops)])
            if params.port is not None:
                args.extend(["--port", str(params.port)])
            if params.queries is not None:
                args.extend(["--queries", str(params.queries)])
            if params.send_wait is not None:
                args.extend(["--send-wait", str(params.send_wait)])
            if params.ipv4:
                args.append("--ipv4")
            elif params.ipv6:
                args.append("--ipv6")
            if params.tcp:
                args.append("--tcp")
            elif params.udp:
                args.append("--udp")
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "interfaces_list":
            args = ["network", "interfaces", "list"]
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")

NETWORK_TOOLS = [NetworkManagementTool]

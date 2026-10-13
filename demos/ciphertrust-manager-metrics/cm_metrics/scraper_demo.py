"""Optional offline demo metrics generator."""

from __future__ import annotations

import random
import time


DEMO_TEMPLATE = """
node_cpu_seconds_total{{cpu="0",mode="idle"}} {cpu_idle}
node_cpu_seconds_total{{cpu="0",mode="user"}} {cpu_user}
node_cpu_seconds_total{{cpu="0",mode="system"}} {cpu_sys}
node_cpu_seconds_total{{cpu="1",mode="idle"}} {cpu_idle2}
node_cpu_seconds_total{{cpu="1",mode="user"}} {cpu_user2}
node_cpu_seconds_total{{cpu="1",mode="system"}} {cpu_sys2}
node_memory_MemTotal_bytes {mem_total}
node_memory_MemAvailable_bytes {mem_avail}
node_memory_MemFree_bytes {mem_free}
node_memory_Buffers_bytes {mem_buffers}
node_memory_Cached_bytes {mem_cached}
node_memory_SReclaimable_bytes {mem_sreclaim}
node_boot_time_seconds {boot_time}
node_time_seconds {now}
node_filesystem_size_bytes{{device="/dev/sda1",fstype="ext4",mountpoint="/"}} {fs_size}
node_filesystem_free_bytes{{device="/dev/sda1",fstype="ext4",mountpoint="/"}} {fs_free}
node_network_receive_bytes_total{{device="eth0"}} {net_rx}
node_network_transmit_bytes_total{{device="eth0"}} {net_tx}
node_netstat_Tcp_CurrEstab {tcp_estab}
node_disk_read_bytes_total{{device="sda"}} {disk_read}
node_disk_written_bytes_total{{device="sda"}} {disk_write}
http_response_time_seconds_sum{{code="200",method="GET",path="/v1/vault/keys2",service="key_vault"}} {http_sum_keys}
http_response_time_seconds_count{{code="200",method="GET",path="/v1/vault/keys2",service="key_vault"}} {http_cnt_keys}
http_response_time_seconds_sum{{code="200",method="POST",path="/encrypt",service="crypto"}} {http_sum_enc}
http_response_time_seconds_count{{code="200",method="POST",path="/encrypt",service="crypto"}} {http_cnt_enc}
http_response_time_seconds_sum{{code="200",method="POST",path="/decrypt",service="crypto"}} {http_sum_dec}
http_response_time_seconds_count{{code="200",method="POST",path="/decrypt",service="crypto"}} {http_cnt_dec}
http_response_time_seconds_count{{code="500",method="GET",path="/v1/system/info",service="system"}} {http_cnt_500}
httpclient_response_time_seconds_sum{{method="GET",path="/internal/keys"}} {httpclient_sum}
httpclient_response_time_seconds_count{{method="GET",path="/internal/keys"}} {httpclient_cnt}
ciphertrust_httpclient_network_latency_seconds_sum{{service="api",upstream_service="key_vault"}} {lat_sum}
ciphertrust_httpclient_network_latency_seconds_count{{service="api",upstream_service="key_vault"}} {lat_cnt}
ciphertrust_user_management_total_users {users}
ciphertrust_user_management_group_users {group_users}
ciphertrust_license_manager_number_of_active_connector_licenses {lic_active}
ciphertrust_license_manager_number_of_inactive_connector_licenses {lic_inactive}
ciphertrust_license_manager_total_number_of_license_units {lic_units}
ciphertrust_license_manager_number_of_consumed_license_units {lic_consumed}
ciphertrust_audit_log_records_total{{service="audit_log"}} {audit_records}
ciphertrust_audit_log_client_logs_total{{service="audit_log"}} {audit_client}
ciphertrust_key_vault_deks_total{{algorithm="AES",state="Active"}} {keys_aes}
ciphertrust_key_vault_deks_total{{algorithm="RSA",state="Active"}} {keys_rsa}
ciphertrust_key_vault_deks_total{{algorithm="EC",state="Active"}} {keys_ec}
ciphertrust_key_vault_deks_total{{algorithm="AES",state="Pre-Active"}} {keys_aes_pre}
ciphertrust_key_vault_key_rotations{{source="scheduler"}} {rot_sched}
ciphertrust_key_vault_key_rotations{{source="manual"}} {rot_manual}
ciphertrust_backup_number_of_backups_taken_sum {backup_sum}
ciphertrust_backup_number_of_backups_taken_count {backup_cnt}
ciphertrust_nae_xml_response_time_seconds_sum {nae_sum}
ciphertrust_nae_xml_response_time_seconds_count {nae_cnt}
ciphertrust_nae_xml_processing_time_seconds_sum {nae_proc_sum}
ciphertrust_nae_xml_processing_time_seconds_count {nae_proc_cnt}
ciphertrust_nae_operations_total{{operation="KeyGenerate",status="success"}} {nae_kg_ok}
ciphertrust_nae_operations_total{{operation="KeyGenerate",status="failed"}} {nae_kg_fail}
ciphertrust_nae_operations_total{{operation="Encrypt",status="success"}} {nae_enc_ok}
ciphertrust_nae_operations_total{{operation="Decrypt",status="success"}} {nae_dec_ok}
ciphertrust_kmip_operations_total{{operation="Create",status="success"}} {kmip_create}
ciphertrust_kmip_operations_total{{operation="Register",status="success"}} {kmip_reg}
ciphertrust_kmip_operations_total{{operation="Activate",status="success"}} {kmip_act}
ciphertrust_kmip_operations_total{{operation="Create",status="failed"}} {kmip_create_fail}
ciphertrust_cte_management_cte_clients{{clients_type="FS",service="cte_management"}} {cte_clients_fs}
ciphertrust_cte_management_cte_clients{{clients_type="CTE-U",service="cte_management"}} {cte_clients_cteu}
ciphertrust_cte_management_cte_clients{{clients_type="CSI",service="cte_management"}} {cte_clients_csi}
ciphertrust_cte_management_clients_health_status{{health_status="HEALTHY",service="cte_management"}} {cte_healthy}
ciphertrust_cte_management_clients_health_status{{health_status="NOT CONNECTED",service="cte_management"}} {cte_not_connected}
ciphertrust_cte_management_clients_health_status{{health_status="UNREGISTERED",service="cte_management"}} {cte_unregistered}
ciphertrust_cte_management_cte_groups{{group_name="ClientGroup",service="cte_management"}} {cte_groups}
ciphertrust_cte_management_cte_guardpoints{{guard_state="ACTIVE",service="cte_management"}} {cte_gp_active}
ciphertrust_cte_management_cte_guardpoints{{guard_state="DISABLED",service="cte_management"}} {cte_gp_inactive}
ciphertrust_cluster_connected{{host="cm-node-2.local"}} 1
ciphertrust_cluster_connected{{host="cm-node-3.local"}} 1
ciphertrust_cluster_write_lag{{host="cm-node-2.local"}} {cluster_lag}
ciphertrust_cluster_replay_lag{{host="cm-node-2.local"}} {cluster_replay}
ciphertrust_cluster_replication_blocked{{host="cm-node-2.local"}} 0
docker_container_start_time_seconds{{name="key_management"}} {svc_start1}
docker_container_start_time_seconds{{name="crypto"}} {svc_start2}
docker_container_start_time_seconds{{name="nae"}} {svc_start3}
docker_container_running_state{{name="key_management"}} 1
docker_container_running_state{{name="crypto"}} 1
docker_container_running_state{{name="nae"}} 1
docker_container_restart_count{{name="key_management"}} 0
docker_container_restart_count{{name="crypto"}} 1
docker_container_restart_count{{name="nae"}} 0
docker_container_cpu_used_total{{name="key_management"}} {svc_cpu_used1}
docker_container_cpu_used_total{{name="crypto"}} {svc_cpu_used2}
docker_container_cpu_used_total{{name="nae"}} {svc_cpu_used3}
docker_container_cpu_capacity_total{{name="key_management"}} {svc_cpu_cap1}
docker_container_cpu_capacity_total{{name="crypto"}} {svc_cpu_cap2}
docker_container_cpu_capacity_total{{name="nae"}} {svc_cpu_cap3}
docker_container_memory_used_bytes{{name="key_management"}} {svc_mem1}
docker_container_memory_used_bytes{{name="crypto"}} {svc_mem2}
docker_container_memory_used_bytes{{name="nae"}} {svc_mem3}
docker_container_network_in_bytes{{name="key_management"}} {svc_net_in1}
docker_container_network_out_bytes{{name="key_management"}} {svc_net_out1}
docker_container_disk_read_bytes{{name="key_management"}} {svc_disk_r1}
docker_container_disk_write_bytes{{name="key_management"}} {svc_disk_w1}
process_cpu_seconds_total{{service="api"}} {proc_cpu}
process_resident_memory_bytes{{service="api"}} {proc_mem}
process_start_time_seconds{{service="api"}} {proc_start}
ciphertrust_jwt_processing_time_seconds_sum {jwt_sum}
ciphertrust_jwt_processing_time_seconds_count {jwt_cnt}
ciphertrust_auth_policies_cache_hits {auth_hits}
ciphertrust_kek_count {kek_count}
ciphertrust_applications_total {apps}
ciphertrust_accounts_total {accounts}
node_tcp_connection_states{{state="established",port="443"}} {tcp_443}
node_tcp_connection_states{{state="established",port="8443"}} {tcp_8443}
node_tcp_connection_states{{state="established",port="9000"}} {tcp_9000}
akeyless_gateway_cpu_utilization_percent {sec_cpu}
akeyless_gateway_memory_utilization_percent {sec_mem}
akeyless_gateway_transactions_total {sec_tx}
akeyless_gateway_http_requests_total{{code="200"}} {sec_http_ok}
akeyless_gateway_http_requests_total{{code="500"}} {sec_http_err}
"""


class DemoGenerator:
    def __init__(self) -> None:
        self.t0 = time.time() - 86_400
        self.counters = {
            "cpu_idle": 10_000.0,
            "cpu_user": 1_200.0,
            "cpu_sys": 400.0,
            "net_rx": 5_000_000_000.0,
            "net_tx": 2_000_000_000.0,
            "disk_read": 800_000_000.0,
            "disk_write": 400_000_000.0,
            "http_cnt_keys": 12_000.0,
            "http_sum_keys": 240.0,
            "http_cnt_enc": 50_000.0,
            "http_sum_enc": 800.0,
            "http_cnt_dec": 48_000.0,
            "http_sum_dec": 720.0,
            "http_cnt_500": 12.0,
            "httpclient_cnt": 80_000.0,
            "httpclient_sum": 160.0,
            "lat_cnt": 80_000.0,
            "lat_sum": 40.0,
            "audit_records": 250_000.0,
            "audit_client": 180_000.0,
            "rot_sched": 420.0,
            "rot_manual": 35.0,
            "backup_cnt": 48.0,
            "backup_sum": 960.0,
            "nae_cnt": 30_000.0,
            "nae_sum": 90.0,
            "nae_proc_cnt": 30_000.0,
            "nae_proc_sum": 60.0,
            "nae_kg_ok": 5_000.0,
            "nae_kg_fail": 12.0,
            "nae_enc_ok": 40_000.0,
            "nae_dec_ok": 39_500.0,
            "kmip_create": 8_000.0,
            "kmip_reg": 1_200.0,
            "kmip_act": 7_500.0,
            "kmip_create_fail": 8.0,
            "proc_cpu": 900.0,
            "jwt_cnt": 20_000.0,
            "jwt_sum": 40.0,
            "auth_hits": 100_000.0,
            "sec_tx": 15_000.0,
            "sec_http_ok": 14_800.0,
            "sec_http_err": 20.0,
        }

    def tick(self) -> str:
        for key in list(self.counters):
            bump = random.uniform(0.5, 8.0)
            if "fail" in key or "500" in key or "err" in key:
                bump = random.choice([0, 0, 0, 1])
            self.counters[key] += bump

        mem_total = 16 * 1024**3
        mem_avail = mem_total * random.uniform(0.35, 0.55)
        fs_size = 200 * 1024**3
        fs_free = fs_size * random.uniform(0.45, 0.65)
        now = time.time()
        values = {
            **self.counters,
            "cpu_idle2": self.counters["cpu_idle"] * 0.98,
            "cpu_user2": self.counters["cpu_user"] * 1.05,
            "cpu_sys2": self.counters["cpu_sys"] * 0.9,
            "mem_total": mem_total,
            "mem_avail": mem_avail,
            "mem_free": mem_avail * 0.4,
            "mem_buffers": 256 * 1024**2,
            "mem_cached": 2 * 1024**3,
            "mem_sreclaim": 128 * 1024**2,
            "boot_time": self.t0,
            "now": now,
            "fs_size": fs_size,
            "fs_free": fs_free,
            "tcp_estab": random.randint(80, 220),
            "users": 128,
            "group_users": 96,
            "lic_active": 12,
            "lic_inactive": 2,
            "lic_units": 1000,
            "lic_consumed": random.randint(420, 480),
            "keys_aes": 1840,
            "keys_rsa": 320,
            "keys_ec": 210,
            "keys_aes_pre": 45,
            "cte_clients_fs": 10,
            "cte_clients_cteu": 8,
            "cte_clients_csi": 3,
            "cte_healthy": 0,
            "cte_not_connected": 13,
            "cte_unregistered": 7,
            "cte_groups": 4,
            "cte_gp_active": 8,
            "cte_gp_inactive": 2,
            "cluster_lag": random.uniform(0.01, 0.2),
            "cluster_replay": random.uniform(0.01, 0.15),
            "svc_start1": now - random.uniform(3600, 86400),
            "svc_start2": now - random.uniform(3600, 86400),
            "svc_start3": now - random.uniform(3600, 86400),
            "svc_cpu_used1": self.counters.setdefault("svc_cpu_used1", 1000.0),
            "svc_cpu_used2": self.counters.setdefault("svc_cpu_used2", 2000.0),
            "svc_cpu_used3": self.counters.setdefault("svc_cpu_used3", 800.0),
            "svc_cpu_cap1": self.counters.setdefault("svc_cpu_cap1", 10000.0),
            "svc_cpu_cap2": self.counters.setdefault("svc_cpu_cap2", 10000.0),
            "svc_cpu_cap3": self.counters.setdefault("svc_cpu_cap3", 10000.0),
            "svc_mem1": random.uniform(400, 900) * 1024**2,
            "svc_mem2": random.uniform(300, 700) * 1024**2,
            "svc_mem3": random.uniform(250, 600) * 1024**2,
            "svc_net_in1": self.counters.setdefault("svc_net_in1", 1_000_000.0),
            "svc_net_out1": self.counters.setdefault("svc_net_out1", 800_000.0),
            "svc_disk_r1": self.counters.setdefault("svc_disk_r1", 500_000.0),
            "svc_disk_w1": self.counters.setdefault("svc_disk_w1", 400_000.0),
            "proc_mem": random.uniform(200, 500) * 1024**2,
            "proc_start": now - 7200,
            "kek_count": 8,
            "apps": 24,
            "accounts": 6,
            "tcp_443": random.randint(40, 120),
            "tcp_8443": random.randint(10, 40),
            "tcp_9000": random.randint(5, 25),
            "sec_cpu": random.uniform(10, 40),
            "sec_mem": random.uniform(30, 70),
        }
        for key in (
            "svc_cpu_used1",
            "svc_cpu_used2",
            "svc_cpu_used3",
            "svc_cpu_cap1",
            "svc_cpu_cap2",
            "svc_cpu_cap3",
            "svc_net_in1",
            "svc_net_out1",
            "svc_disk_r1",
            "svc_disk_w1",
        ):
            self.counters[key] = self.counters.get(key, 1000.0) + random.uniform(1, 20)
            values[key] = self.counters[key]
        return DEMO_TEMPLATE.format(**values)

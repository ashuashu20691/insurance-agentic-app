# =============================================================================
# Outputs
# =============================================================================

# -----------------------------------------------------------------------------
# Networking
# -----------------------------------------------------------------------------

output "vcn_id" {
  description = "OCID of the VCN"
  value       = oci_core_vcn.insurance_vcn.id
}

output "public_subnet_id" {
  description = "OCID of the public subnet"
  value       = oci_core_subnet.public_subnet.id
}

output "private_subnet_id" {
  description = "OCID of the private subnet"
  value       = oci_core_subnet.private_subnet.id
}

# -----------------------------------------------------------------------------
# Autonomous Database
# -----------------------------------------------------------------------------

output "adb_id" {
  description = "OCID of the Autonomous Database"
  value       = oci_database_autonomous_database.insurance_adb.id
}

output "adb_connection_strings" {
  description = "Connection strings for the Autonomous Database"
  value       = oci_database_autonomous_database.insurance_adb.connection_strings
  sensitive   = true
}

output "adb_service_console_url" {
  description = "Service Console URL for the Autonomous Database"
  value       = oci_database_autonomous_database.insurance_adb.service_console_url
}

output "adb_tns_name" {
  description = "TNS name for database connection"
  value       = "${lower(var.adb_db_name)}_high"
}

# -----------------------------------------------------------------------------
# Compute
# -----------------------------------------------------------------------------

output "app_instance_id" {
  description = "OCID of the application instance"
  value       = oci_core_instance.app_instance.id
}

output "app_public_ip" {
  description = "Public IP of the application instance"
  value       = oci_core_instance.app_instance.public_ip
}

output "app_private_ip" {
  description = "Private IP of the application instance"
  value       = oci_core_instance.app_instance.private_ip
}

# -----------------------------------------------------------------------------
# Application URLs
# -----------------------------------------------------------------------------

output "streamlit_ui_url" {
  description = "URL for the Streamlit UI"
  value       = "http://${oci_core_instance.app_instance.public_ip}:8501"
}

output "fastapi_url" {
  description = "URL for the FastAPI backend"
  value       = "http://${oci_core_instance.app_instance.public_ip}:8000"
}

output "fastapi_docs_url" {
  description = "URL for FastAPI Swagger documentation"
  value       = "http://${oci_core_instance.app_instance.public_ip}:8000/docs"
}

# -----------------------------------------------------------------------------
# SSH Connection
# -----------------------------------------------------------------------------

output "ssh_connection" {
  description = "SSH command to connect to the instance"
  value       = "ssh opc@${oci_core_instance.app_instance.public_ip}"
}

# -----------------------------------------------------------------------------
# Object Storage
# -----------------------------------------------------------------------------

output "wallet_bucket_name" {
  description = "Name of the bucket containing the ADB wallet"
  value       = oci_objectstorage_bucket.wallet_bucket.name
}

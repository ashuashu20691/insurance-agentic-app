# =============================================================================
# Variables
# =============================================================================

# -----------------------------------------------------------------------------
# OCI Provider
# -----------------------------------------------------------------------------

variable "tenancy_ocid" {
  description = "OCID of the tenancy"
  type        = string
}

variable "user_ocid" {
  description = "OCID of the user"
  type        = string
}

variable "fingerprint" {
  description = "Fingerprint of the API key"
  type        = string
}

variable "private_key_path" {
  description = "Path to the private key file"
  type        = string
}

variable "region" {
  description = "OCI region"
  type        = string
  default     = "us-chicago-1"
}

variable "compartment_ocid" {
  description = "OCID of the compartment"
  type        = string
}

# -----------------------------------------------------------------------------
# Project
# -----------------------------------------------------------------------------

variable "project_name" {
  description = "Project name prefix for resources"
  type        = string
  default     = "insurance-claims"
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "InsuranceClaimsProcessing"
    Environment = "Production"
    ManagedBy   = "Terraform"
  }
}

# -----------------------------------------------------------------------------
# Networking
# -----------------------------------------------------------------------------

variable "vcn_cidr" {
  description = "CIDR block for VCN"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "private_subnet_cidr" {
  description = "CIDR block for private subnet"
  type        = string
  default     = "10.0.2.0/24"
}

# -----------------------------------------------------------------------------
# Autonomous Database
# -----------------------------------------------------------------------------

variable "adb_db_name" {
  description = "Database name (alphanumeric, max 14 chars)"
  type        = string
  default     = "INSURANCEDB"
}

variable "adb_admin_password" {
  description = "Admin password for ADB"
  type        = string
  sensitive   = true
}

variable "adb_wallet_password" {
  description = "Password for ADB wallet"
  type        = string
  sensitive   = true
}

variable "adb_is_free_tier" {
  description = "Use Always Free tier"
  type        = bool
  default     = false
}

variable "adb_cpu_core_count" {
  description = "CPU core count (for non-ECPU)"
  type        = number
  default     = 1
}

variable "adb_ocpu_count" {
  description = "OCPU count"
  type        = number
  default     = 1
}

variable "adb_compute_count" {
  description = "ECPU compute count"
  type        = number
  default     = 2
}

variable "adb_storage_size_in_tbs" {
  description = "Storage size in TB"
  type        = number
  default     = 1
}

variable "adb_auto_scaling_enabled" {
  description = "Enable auto scaling for compute"
  type        = bool
  default     = true
}

variable "adb_auto_scaling_storage_enabled" {
  description = "Enable auto scaling for storage"
  type        = bool
  default     = false
}

variable "adb_license_model" {
  description = "License model: LICENSE_INCLUDED or BRING_YOUR_OWN_LICENSE"
  type        = string
  default     = "LICENSE_INCLUDED"
}

# -----------------------------------------------------------------------------
# Compute
# -----------------------------------------------------------------------------

variable "compute_shape" {
  description = "Compute instance shape"
  type        = string
  default     = "VM.Standard.E4.Flex"
}

variable "compute_ocpus" {
  description = "Number of OCPUs for flex shapes"
  type        = number
  default     = 2
}

variable "compute_memory_in_gbs" {
  description = "Memory in GB for flex shapes"
  type        = number
  default     = 16
}

variable "ssh_public_key" {
  description = "SSH public key for instance access"
  type        = string
}

# -----------------------------------------------------------------------------
# Application
# -----------------------------------------------------------------------------

variable "app_oracle_user" {
  description = "Oracle database user for the application"
  type        = string
  default     = "insurance_user"
}

variable "app_oracle_password" {
  description = "Oracle database password for the application"
  type        = string
  sensitive   = true
}

# -----------------------------------------------------------------------------
# OCI GenAI
# -----------------------------------------------------------------------------

variable "oci_genai_endpoint" {
  description = "OCI GenAI service endpoint"
  type        = string
  default     = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"
}

variable "oci_genai_model_id" {
  description = "OCI GenAI model ID"
  type        = string
  default     = "cohere.command-a-03-2025"
}


# -----------------------------------------------------------------------------
# Load Balancer (Optional)
# -----------------------------------------------------------------------------

variable "enable_load_balancer" {
  description = "Enable load balancer for production deployment"
  type        = bool
  default     = false
}


# -----------------------------------------------------------------------------
# Container Deployment (Alternative)
# -----------------------------------------------------------------------------

variable "enable_container_deployment" {
  description = "Use Container Instances instead of VM"
  type        = bool
  default     = false
}

variable "container_ocpus" {
  description = "OCPUs for container instance"
  type        = number
  default     = 2
}

variable "container_memory_in_gbs" {
  description = "Memory in GB for container instance"
  type        = number
  default     = 8
}

variable "api_container_image" {
  description = "Container image URL for FastAPI"
  type        = string
  default     = ""
}

variable "ui_container_image" {
  description = "Container image URL for Streamlit"
  type        = string
  default     = ""
}

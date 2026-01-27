# =============================================================================
# Oracle Autonomous Database 23ai
# =============================================================================

resource "oci_database_autonomous_database" "insurance_adb" {
  compartment_id = var.compartment_ocid
  db_name        = var.adb_db_name
  display_name   = "${var.project_name}-adb"

  # Database Configuration
  db_version                          = "23ai"
  db_workload                         = "OLTP"
  is_free_tier                        = var.adb_is_free_tier
  cpu_core_count                      = var.adb_cpu_core_count
  data_storage_size_in_tbs            = var.adb_storage_size_in_tbs
  ocpu_count                          = var.adb_ocpu_count
  compute_model                       = "ECPU"
  compute_count                       = var.adb_compute_count
  is_auto_scaling_enabled             = var.adb_auto_scaling_enabled
  is_auto_scaling_for_storage_enabled = var.adb_auto_scaling_storage_enabled

  # Admin Credentials
  admin_password = var.adb_admin_password

  # Network Configuration
  subnet_id                   = oci_core_subnet.private_subnet.id
  nsg_ids                     = [oci_core_network_security_group.adb_nsg.id]
  is_mtls_connection_required = true
  whitelisted_ips             = []

  # License
  license_model = var.adb_license_model

  freeform_tags = var.common_tags

  lifecycle {
    ignore_changes = [admin_password]
  }
}

# Network Security Group for ADB
resource "oci_core_network_security_group" "adb_nsg" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.insurance_vcn.id
  display_name   = "${var.project_name}-adb-nsg"

  freeform_tags = var.common_tags
}

resource "oci_core_network_security_group_security_rule" "adb_ingress" {
  network_security_group_id = oci_core_network_security_group.adb_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = var.vcn_cidr
  source_type               = "CIDR_BLOCK"

  tcp_options {
    destination_port_range {
      min = 1521
      max = 1522
    }
  }
}

resource "oci_core_network_security_group_security_rule" "adb_egress" {
  network_security_group_id = oci_core_network_security_group.adb_nsg.id
  direction                 = "EGRESS"
  protocol                  = "all"
  destination               = "0.0.0.0/0"
  destination_type          = "CIDR_BLOCK"
}

# Download ADB Wallet
resource "oci_database_autonomous_database_wallet" "adb_wallet" {
  autonomous_database_id = oci_database_autonomous_database.insurance_adb.id
  password               = var.adb_wallet_password
  base64_encode_content  = true
  generate_type          = "SINGLE"
}

# Store wallet in Object Storage
resource "oci_objectstorage_bucket" "wallet_bucket" {
  compartment_id = var.compartment_ocid
  namespace      = data.oci_objectstorage_namespace.ns.namespace
  name           = "${var.project_name}-wallet-bucket"
  access_type    = "NoPublicAccess"

  freeform_tags = var.common_tags
}

data "oci_objectstorage_namespace" "ns" {
  compartment_id = var.compartment_ocid
}

resource "oci_objectstorage_object" "wallet_object" {
  bucket    = oci_objectstorage_bucket.wallet_bucket.name
  namespace = data.oci_objectstorage_namespace.ns.namespace
  object    = "adb_wallet.zip"
  content   = oci_database_autonomous_database_wallet.adb_wallet.content
}

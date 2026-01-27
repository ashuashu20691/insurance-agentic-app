# =============================================================================
# Compute Instance for Application
# =============================================================================

resource "oci_core_instance" "app_instance" {
  compartment_id      = var.compartment_ocid
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  display_name        = "${var.project_name}-app"
  shape               = var.compute_shape

  dynamic "shape_config" {
    for_each = var.compute_shape == "VM.Standard.E4.Flex" || var.compute_shape == "VM.Standard.A1.Flex" ? [1] : []
    content {
      ocpus         = var.compute_ocpus
      memory_in_gbs = var.compute_memory_in_gbs
    }
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.oracle_linux.images[0].id
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.public_subnet.id
    assign_public_ip = true
    nsg_ids          = [oci_core_network_security_group.app_nsg.id]
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data = base64encode(templatefile("${path.module}/scripts/cloud-init.yaml", {
      adb_wallet_bucket    = oci_objectstorage_bucket.wallet_bucket.name
      adb_wallet_namespace = data.oci_objectstorage_namespace.ns.namespace
      adb_tns_name         = "${lower(var.adb_db_name)}_high"
      oracle_user          = var.app_oracle_user
      oracle_password      = var.app_oracle_password
      oci_compartment_id   = var.compartment_ocid
      oci_region           = var.region
      oci_genai_endpoint   = var.oci_genai_endpoint
      oci_genai_model_id   = var.oci_genai_model_id
    }))
  }

  freeform_tags = var.common_tags

  depends_on = [
    oci_database_autonomous_database.insurance_adb,
    oci_objectstorage_object.wallet_object
  ]
}

# Network Security Group for App
resource "oci_core_network_security_group" "app_nsg" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.insurance_vcn.id
  display_name   = "${var.project_name}-app-nsg"

  freeform_tags = var.common_tags
}

# SSH Access
resource "oci_core_network_security_group_security_rule" "app_ssh_ingress" {
  network_security_group_id = oci_core_network_security_group.app_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6"
  source                    = "0.0.0.0/0"
  source_type               = "CIDR_BLOCK"

  tcp_options {
    destination_port_range {
      min = 22
      max = 22
    }
  }
}

# Streamlit UI Access
resource "oci_core_network_security_group_security_rule" "app_streamlit_ingress" {
  network_security_group_id = oci_core_network_security_group.app_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6"
  source                    = "0.0.0.0/0"
  source_type               = "CIDR_BLOCK"

  tcp_options {
    destination_port_range {
      min = 8501
      max = 8501
    }
  }
}

# FastAPI Access (internal)
resource "oci_core_network_security_group_security_rule" "app_api_ingress" {
  network_security_group_id = oci_core_network_security_group.app_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6"
  source                    = var.vcn_cidr
  source_type               = "CIDR_BLOCK"

  tcp_options {
    destination_port_range {
      min = 8000
      max = 8000
    }
  }
}

# All Egress
resource "oci_core_network_security_group_security_rule" "app_egress" {
  network_security_group_id = oci_core_network_security_group.app_nsg.id
  direction                 = "EGRESS"
  protocol                  = "all"
  destination               = "0.0.0.0/0"
  destination_type          = "CIDR_BLOCK"
}

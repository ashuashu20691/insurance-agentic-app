# =============================================================================
# IAM - Dynamic Group and Policies for Instance Principal
# =============================================================================

# Dynamic Group for Compute Instance
resource "oci_identity_dynamic_group" "app_dynamic_group" {
  compartment_id = var.tenancy_ocid
  name           = "${var.project_name}-app-dg"
  description    = "Dynamic group for insurance claims app instances"
  matching_rule  = "ALL {instance.compartment.id = '${var.compartment_ocid}'}"

  freeform_tags = var.common_tags
}

# Policy for GenAI Access
resource "oci_identity_policy" "genai_policy" {
  compartment_id = var.compartment_ocid
  name           = "${var.project_name}-genai-policy"
  description    = "Policy to allow app instances to use OCI GenAI"

  statements = [
    "Allow dynamic-group ${oci_identity_dynamic_group.app_dynamic_group.name} to use generative-ai-family in compartment id ${var.compartment_ocid}",
    "Allow dynamic-group ${oci_identity_dynamic_group.app_dynamic_group.name} to manage generative-ai-chat in compartment id ${var.compartment_ocid}",
  ]

  freeform_tags = var.common_tags
}

# Policy for Object Storage (wallet access)
resource "oci_identity_policy" "objectstorage_policy" {
  compartment_id = var.compartment_ocid
  name           = "${var.project_name}-objectstorage-policy"
  description    = "Policy to allow app instances to access Object Storage"

  statements = [
    "Allow dynamic-group ${oci_identity_dynamic_group.app_dynamic_group.name} to read objects in compartment id ${var.compartment_ocid} where target.bucket.name='${oci_objectstorage_bucket.wallet_bucket.name}'",
  ]

  freeform_tags = var.common_tags
}

# Policy for ADB Access
resource "oci_identity_policy" "adb_policy" {
  compartment_id = var.compartment_ocid
  name           = "${var.project_name}-adb-policy"
  description    = "Policy to allow app instances to access Autonomous Database"

  statements = [
    "Allow dynamic-group ${oci_identity_dynamic_group.app_dynamic_group.name} to use autonomous-databases in compartment id ${var.compartment_ocid}",
  ]

  freeform_tags = var.common_tags
}

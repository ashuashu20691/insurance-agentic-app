# =============================================================================
# Container Instance Deployment (Alternative to VM)
# Set enable_container_deployment = true to use this instead of VM
# =============================================================================

# Container Registry Repository
resource "oci_artifacts_container_repository" "app_repo" {
  count = var.enable_container_deployment ? 1 : 0

  compartment_id = var.compartment_ocid
  display_name   = "${var.project_name}-app"
  is_public      = false

  freeform_tags = var.common_tags
}

# Container Instance
resource "oci_container_instances_container_instance" "app_container" {
  count = var.enable_container_deployment ? 1 : 0

  compartment_id           = var.compartment_ocid
  availability_domain      = data.oci_identity_availability_domains.ads.availability_domains[0].name
  display_name             = "${var.project_name}-container"
  container_restart_policy = "ALWAYS"

  shape = "CI.Standard.E4.Flex"
  shape_config {
    ocpus         = var.container_ocpus
    memory_in_gbs = var.container_memory_in_gbs
  }

  vnics {
    subnet_id             = oci_core_subnet.public_subnet.id
    is_public_ip_assigned = true
    nsg_ids               = [oci_core_network_security_group.app_nsg.id]
  }

  # FastAPI Container
  containers {
    display_name = "fastapi"
    image_url    = var.api_container_image

    environment_variables = {
      OCI_COMPARTMENT_ID     = var.compartment_ocid
      OCI_SERVICE_ENDPOINT   = var.oci_genai_endpoint
      OCI_MODEL_ID           = var.oci_genai_model_id
      ORACLE_USER            = var.app_oracle_user
      ORACLE_PASSWORD        = var.app_oracle_password
      ORACLE_DSN             = "${lower(var.adb_db_name)}_high"
      ORACLE_WALLET_LOCATION = "/app/wallet"
    }

    resource_config {
      vcpus_limit         = var.container_ocpus / 2
      memory_limit_in_gbs = var.container_memory_in_gbs / 2
    }

    health_checks {
      health_check_type   = "HTTP"
      port                = 8000
      path                = "/health"
      interval_in_seconds = 30
      timeout_in_seconds  = 10
      failure_threshold   = 3
    }
  }

  # Streamlit Container
  containers {
    display_name = "streamlit"
    image_url    = var.ui_container_image

    environment_variables = {
      API_URL = "http://localhost:8000"
    }

    resource_config {
      vcpus_limit         = var.container_ocpus / 2
      memory_limit_in_gbs = var.container_memory_in_gbs / 2
    }

    health_checks {
      health_check_type   = "HTTP"
      port                = 8501
      path                = "/"
      interval_in_seconds = 30
      timeout_in_seconds  = 10
      failure_threshold   = 3
    }
  }

  freeform_tags = var.common_tags

  depends_on = [oci_database_autonomous_database.insurance_adb]
}

# Output for Container Instance
output "container_instance_id" {
  description = "OCID of the container instance"
  value       = var.enable_container_deployment ? oci_container_instances_container_instance.app_container[0].id : null
}

output "container_public_ip" {
  description = "Public IP of the container instance"
  value       = var.enable_container_deployment ? oci_container_instances_container_instance.app_container[0].vnics[0].private_ip : null
}

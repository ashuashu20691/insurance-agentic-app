# =============================================================================
# Load Balancer (Optional - for production with multiple instances)
# =============================================================================

resource "oci_load_balancer_load_balancer" "app_lb" {
  count = var.enable_load_balancer ? 1 : 0

  compartment_id = var.compartment_ocid
  display_name   = "${var.project_name}-lb"
  shape          = "flexible"

  shape_details {
    minimum_bandwidth_in_mbps = 10
    maximum_bandwidth_in_mbps = 100
  }

  subnet_ids = [oci_core_subnet.public_subnet.id]

  is_private = false

  freeform_tags = var.common_tags
}

# Backend Set for Streamlit UI
resource "oci_load_balancer_backend_set" "ui_backend_set" {
  count = var.enable_load_balancer ? 1 : 0

  load_balancer_id = oci_load_balancer_load_balancer.app_lb[0].id
  name             = "ui-backend-set"
  policy           = "ROUND_ROBIN"

  health_checker {
    protocol          = "HTTP"
    port              = 8501
    url_path          = "/"
    return_code       = 200
    interval_ms       = 10000
    timeout_in_millis = 3000
    retries           = 3
  }
}

# Backend Set for FastAPI
resource "oci_load_balancer_backend_set" "api_backend_set" {
  count = var.enable_load_balancer ? 1 : 0

  load_balancer_id = oci_load_balancer_load_balancer.app_lb[0].id
  name             = "api-backend-set"
  policy           = "ROUND_ROBIN"

  health_checker {
    protocol          = "HTTP"
    port              = 8000
    url_path          = "/health"
    return_code       = 200
    interval_ms       = 10000
    timeout_in_millis = 3000
    retries           = 3
  }
}

# Backend for UI
resource "oci_load_balancer_backend" "ui_backend" {
  count = var.enable_load_balancer ? 1 : 0

  load_balancer_id = oci_load_balancer_load_balancer.app_lb[0].id
  backendset_name  = oci_load_balancer_backend_set.ui_backend_set[0].name
  ip_address       = oci_core_instance.app_instance.private_ip
  port             = 8501
  weight           = 1
}

# Backend for API
resource "oci_load_balancer_backend" "api_backend" {
  count = var.enable_load_balancer ? 1 : 0

  load_balancer_id = oci_load_balancer_load_balancer.app_lb[0].id
  backendset_name  = oci_load_balancer_backend_set.api_backend_set[0].name
  ip_address       = oci_core_instance.app_instance.private_ip
  port             = 8000
  weight           = 1
}

# Listener for UI (port 80)
resource "oci_load_balancer_listener" "ui_listener" {
  count = var.enable_load_balancer ? 1 : 0

  load_balancer_id         = oci_load_balancer_load_balancer.app_lb[0].id
  name                     = "ui-listener"
  default_backend_set_name = oci_load_balancer_backend_set.ui_backend_set[0].name
  port                     = 80
  protocol                 = "HTTP"
}

# Listener for API (port 8000)
resource "oci_load_balancer_listener" "api_listener" {
  count = var.enable_load_balancer ? 1 : 0

  load_balancer_id         = oci_load_balancer_load_balancer.app_lb[0].id
  name                     = "api-listener"
  default_backend_set_name = oci_load_balancer_backend_set.api_backend_set[0].name
  port                     = 8000
  protocol                 = "HTTP"
}

# Output for Load Balancer
output "load_balancer_ip" {
  description = "Public IP of the load balancer"
  value       = var.enable_load_balancer ? oci_load_balancer_load_balancer.app_lb[0].ip_address_details[0].ip_address : null
}

output "load_balancer_ui_url" {
  description = "URL for the UI via load balancer"
  value       = var.enable_load_balancer ? "http://${oci_load_balancer_load_balancer.app_lb[0].ip_address_details[0].ip_address}" : null
}

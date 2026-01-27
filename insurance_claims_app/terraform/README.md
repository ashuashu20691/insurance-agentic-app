# Insurance Claims Processing System - Terraform Deployment

This Terraform configuration deploys the Insurance Claims Processing System on Oracle Cloud Infrastructure (OCI).

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         OCI Region                               │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                          VCN                               │  │
│  │  ┌─────────────────────┐  ┌─────────────────────────────┐ │  │
│  │  │   Public Subnet     │  │      Private Subnet          │ │  │
│  │  │  ┌───────────────┐  │  │  ┌───────────────────────┐  │ │  │
│  │  │  │   Compute     │  │  │  │  Oracle Autonomous    │  │ │  │
│  │  │  │   Instance    │──┼──┼──│  Database 23ai        │  │ │  │
│  │  │  │  (App Server) │  │  │  │  (Vector Storage)     │  │ │  │
│  │  │  └───────────────┘  │  │  └───────────────────────┘  │ │  │
│  │  │         │           │  │                              │ │  │
│  │  │    ┌────┴────┐      │  │                              │ │  │
│  │  │    │ Ports:  │      │  │                              │ │  │
│  │  │    │ 8501 UI │      │  │                              │ │  │
│  │  │    │ 8000 API│      │  │                              │ │  │
│  │  │    └─────────┘      │  │                              │ │  │
│  │  └─────────────────────┘  └─────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                    ┌─────────┴─────────┐                        │
│                    │   OCI GenAI       │                        │
│                    │ (Cohere Command-A)│                        │
│                    └───────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

## Resources Created

| Resource | Description |
|----------|-------------|
| VCN | Virtual Cloud Network with public/private subnets |
| Internet Gateway | For public internet access |
| NAT Gateway | For private subnet outbound access |
| Service Gateway | For OCI service access |
| Compute Instance | VM running FastAPI + Streamlit |
| Autonomous Database | Oracle 23ai with vector storage |
| Object Storage | Bucket for ADB wallet |
| IAM Policies | For GenAI and database access |
| Load Balancer | Optional, for production scaling |

## Prerequisites

1. OCI account with appropriate permissions
2. OCI CLI configured (`~/.oci/config`)
3. Terraform >= 1.5.0
4. SSH key pair for instance access

## Quick Start

```bash
# 1. Clone and navigate to terraform directory
cd insurance_claims_app/terraform

# 2. Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# 3. Initialize Terraform
terraform init

# 4. Review the plan
terraform plan

# 5. Apply the configuration
terraform apply

# 6. Get outputs
terraform output
```

## Configuration

### Required Variables

| Variable | Description |
|----------|-------------|
| `tenancy_ocid` | Your OCI tenancy OCID |
| `user_ocid` | Your OCI user OCID |
| `fingerprint` | API key fingerprint |
| `private_key_path` | Path to OCI API private key |
| `compartment_ocid` | Target compartment OCID |
| `adb_admin_password` | ADB admin password |
| `adb_wallet_password` | ADB wallet password |
| `app_oracle_password` | Application DB user password |
| `ssh_public_key` | SSH public key for instance |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `region` | us-chicago-1 | OCI region |
| `compute_shape` | VM.Standard.E4.Flex | Instance shape |
| `compute_ocpus` | 2 | OCPUs for flex shape |
| `compute_memory_in_gbs` | 16 | Memory in GB |
| `adb_compute_count` | 2 | ADB ECPU count |
| `enable_load_balancer` | false | Enable LB for HA |

## Post-Deployment Setup

After Terraform completes:

1. SSH into the instance:
   ```bash
   ssh opc@<public_ip>
   ```

2. Upload application files:
   ```bash
   scp -r ../insurance_claims_app/* opc@<public_ip>:/opt/insurance-claims/app/
   ```

3. Run the setup script:
   ```bash
   sudo /opt/insurance-claims/setup.sh
   ```

4. Access the application:
   - UI: `http://<public_ip>:8501`
   - API: `http://<public_ip>:8000`
   - API Docs: `http://<public_ip>:8000/docs`

## Database Setup

After deployment, create the application user:

```sql
-- Connect as ADMIN
CREATE USER insurance_user IDENTIFIED BY "YourPassword123#";
GRANT CONNECT, RESOURCE TO insurance_user;
GRANT UNLIMITED TABLESPACE TO insurance_user;
GRANT CREATE TABLE, CREATE VIEW, CREATE SEQUENCE TO insurance_user;
```

## Security Considerations

- ADB uses mTLS with wallet-based authentication
- Instance uses Instance Principal for OCI API access
- Sensitive variables marked as `sensitive = true`
- Private subnet for database isolation
- NSGs restrict traffic to required ports only

## Costs

Estimated monthly costs (varies by region):
- Compute (E4.Flex 2 OCPU): ~$30-50
- ADB (2 ECPU): ~$100-150
- Networking: ~$10-20
- Object Storage: < $1

Use `adb_is_free_tier = true` for Always Free tier (limited resources).

## Cleanup

```bash
terraform destroy
```

## Troubleshooting

### Instance not starting
- Check cloud-init logs: `sudo cat /var/log/cloud-init-output.log`

### Database connection issues
- Verify wallet is downloaded: `ls /opt/insurance-claims/wallet/`
- Check TNS name in `.env` matches ADB

### GenAI not working
- Verify IAM policies are applied
- Check compartment OCID in `.env`

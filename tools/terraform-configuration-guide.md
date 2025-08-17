# Terraform Configuration Guide

## Overview
Infrastructure as Code (IaC) configuration for Solitude platform using Terraform alongside Pulumi.

## Project Structure
```
terraform/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── production/
├── modules/
│   ├── gcp-foundation/
│   ├── kubernetes/
│   ├── networking/
│   ├── security/
│   └── workloads/
├── global/
└── scripts/
```

## GCP Foundation Setup

### Provider Configuration
```hcl
terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "solitude-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
```

### State Management
- **Backend**: GCS bucket with versioning enabled
- **State Locking**: Enabled via GCS native locking
- **Encryption**: Default GCS encryption at rest

## Core Modules

### GCP Foundation Module
```hcl
module "gcp_foundation" {
  source = "../../modules/gcp-foundation"
  
  project_id         = var.project_id
  region            = var.region
  environment       = var.environment
  enable_apis       = [
    "compute.googleapis.com",
    "container.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudkms.googleapis.com",
  ]
}
```

### Networking Module
```hcl
module "networking" {
  source = "../../modules/networking"
  
  project_id    = var.project_id
  region        = var.region
  network_name  = "solitude-${var.environment}"
  
  subnets = {
    "gke-subnet" = {
      ip_cidr_range = "10.0.0.0/20"
      secondary_ranges = {
        pods     = "10.4.0.0/14"
        services = "10.8.0.0/20"
      }
    }
  }
}
```

### GKE Cluster Configuration
```hcl
module "gke" {
  source = "../../modules/kubernetes"
  
  cluster_name     = "solitude-${var.environment}"
  location         = var.region
  network          = module.networking.network_name
  subnetwork       = module.networking.subnets["gke-subnet"].name
  
  node_pools = {
    default = {
      machine_type = "n2-standard-4"
      min_count    = 3
      max_count    = 10
      disk_size_gb = 100
    }
    gpu = {
      machine_type = "n1-standard-8"
      accelerator_type = "nvidia-tesla-t4"
      accelerator_count = 1
      min_count    = 0
      max_count    = 5
    }
  }
}
```

## Secrets Management

### Google Secret Manager Integration
```hcl
resource "google_secret_manager_secret" "app_secrets" {
  for_each = var.app_secrets
  
  secret_id = each.key
  
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "app_secrets" {
  for_each = google_secret_manager_secret.app_secrets
  
  secret      = each.value.id
  secret_data = each.value.secret_value
}
```

### Infisical Integration
- Customer secrets managed via Infisical
- Infrastructure secrets in GCP Secret Manager
- WorkOS credentials stored securely

## GPU Infrastructure

### GPU Node Pool Configuration
```hcl
resource "google_container_node_pool" "gpu_pool" {
  name       = "gpu-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = var.gpu_node_count

  node_config {
    machine_type = "n1-standard-8"
    
    guest_accelerator {
      type  = "nvidia-tesla-t4"
      count = 1
    }
    
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
    
    labels = {
      workload = "gpu"
    }
    
    taint {
      key    = "nvidia.com/gpu"
      value  = "present"
      effect = "NO_SCHEDULE"
    }
  }
  
  autoscaling {
    min_node_count = 0
    max_node_count = 5
  }
}
```

## Environment Variables

### Development
```hcl
# terraform/environments/dev/terraform.tfvars
project_id    = "solitude-dev"
region        = "us-central1"
environment   = "dev"
instance_count = 1
```

### Staging
```hcl
# terraform/environments/staging/terraform.tfvars
project_id    = "solitude-staging"
region        = "us-central1"
environment   = "staging"
instance_count = 2
```

### Production
```hcl
# terraform/environments/production/terraform.tfvars
project_id    = "solitude-prod"
region        = "us-central1"
environment   = "production"
instance_count = 3
enable_ha     = true
```

## Deployment Workflow

### Initial Setup
```bash
# Initialize backend
cd terraform/environments/dev
terraform init

# Plan changes
terraform plan -out=tfplan

# Apply changes
terraform apply tfplan
```

### CI/CD Integration
```yaml
# .github/workflows/terraform.yml
name: Terraform
on:
  pull_request:
    paths:
      - 'terraform/**'
      
jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: hashicorp/setup-terraform@v2
      
      - name: Terraform Init
        run: terraform init
        
      - name: Terraform Plan
        run: terraform plan
```

## Best Practices

### Resource Naming
- Use consistent naming: `{product}-{environment}-{resource}`
- Example: `solitude-prod-gke-cluster`

### Tagging Strategy
```hcl
locals {
  common_tags = {
    Environment = var.environment
    Project     = "solitude"
    ManagedBy   = "terraform"
    Team        = "platform"
  }
}
```

### Security Considerations
1. Enable GKE Workload Identity
2. Use least-privilege IAM roles
3. Encrypt secrets at rest
4. Enable VPC native clusters
5. Configure Private GKE clusters

### Cost Optimization
1. Use preemptible nodes for non-critical workloads
2. Enable cluster autoscaling
3. Configure resource quotas
4. Use committed use discounts

## Integration with Pulumi

Terraform handles:
- GCP foundation resources
- Networking infrastructure
- GKE cluster provisioning
- IAM and security policies

Pulumi handles:
- Kubernetes deployments
- Application configuration
- Dynamic resource provisioning
- Complex orchestration logic

## Monitoring & Observability

### Honeycomb Integration
```hcl
resource "kubernetes_secret" "honeycomb" {
  metadata {
    name      = "honeycomb-api-key"
    namespace = "monitoring"
  }
  
  data = {
    api_key = google_secret_manager_secret_version.honeycomb_key.secret_data
  }
}
```

## Common Commands

```bash
# Format code
terraform fmt -recursive

# Validate configuration
terraform validate

# Show current state
terraform show

# Import existing resources
terraform import module.gke.google_container_cluster.primary projects/solitude-prod/locations/us-central1/clusters/solitude-prod

# Destroy resources (careful!)
terraform destroy
```

## Troubleshooting

### State Lock Issues
```bash
# Force unlock (use with caution)
terraform force-unlock <LOCK_ID>
```

### Module Updates
```bash
# Update modules
terraform get -update
```

### Debugging
```bash
# Enable debug logging
export TF_LOG=DEBUG
terraform plan
```

## Related Documentation
- [[solitude]] - Main project documentation
- [[solitude-architecture]] - System architecture
- [[database-architecture]] - Database design
- [[projects-hub]] - Projects overview

---
Last Updated: 2025-01-08
Tags: #terraform #infrastructure #gcp #kubernetes #iac
terraform {
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.45"
    }
  }
}

provider "hcloud" {
  token = var.hcloud_token
}

resource "hcloud_ssh_key" "default" {
  name       = "cloudobsinfra-key"
  public_key = file("~/.ssh/id_rsa.pub")
}

resource "hcloud_firewall" "app_firewall" {
  name = "cloudobsinfra-firewall"

  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "22"
    source_ips = ["0.0.0.0/0", "::/0"]
  }

  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "80"
    source_ips = ["0.0.0.0/0", "::/0"]
  }

  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "443"
    source_ips = ["0.0.0.0/0", "::/0"]
  }
}

resource "hcloud_server" "app_server" {
  name         = "cloudobsinfra-server"
  server_type  = "cx23"
  image        = "ubuntu-24.04"
  location     = "nbg1"
  ssh_keys     = [hcloud_ssh_key.default.id]
  firewall_ids = [hcloud_firewall.app_firewall.id]
}

output "server_ip" {
  value = hcloud_server.app_server.ipv4_address
}
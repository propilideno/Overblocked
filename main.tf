#     _    __  __ ___ 
#    / \  |  \/  |_ _|
#   / _ \ | |\/| || | 
#  / ___ \| |  | || | 
# /_/   \_\_|  |_|___|
data "aws_ami" "selected" {
  most_recent = true
  owners      = ["099720109477"] # Canonical
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

#  ____  _____ ___  _   _ ___ ____  _____ ____  
# |  _ \| ____/ _ \| | | |_ _|  _ \| ____|  _ \ 
# | |_) |  _|| | | | | | || || |_) |  _| | | | |
# |  _ <| |__| |_| | |_| || ||  _ <| |___| |_| |
# |_| \_\_____\__\_\\___/|___|_| \_\_____|____/ 

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.37" # >= (5.37.0) and < (6.0.0)
    }
  }
}

locals {
  project = "gamedev"
  key_name = "lalmeida-rsa"
  ip_grupo = [
    "${chomp(data.http.ipv4.response_body)}/32", # Your IP
    "0.0.0.0/0" # Internet
  ]
  user_data = <<-EOF
  #cloud-config
  
  runcmd:
    - |
      #!/bin/bash
      curl -fsSL https://get.docker.com | sudo sh    # Install Docker
      sudo apt install -y docker-compose             # Install Docker Compose
      usermod -aG docker ubuntu                      # Add ubuntu user to docker group
      sudo systemctl enable --now docker             # Start Docker
  
      # ADD YOUR SCRIPTS HERE
  EOF
}

#   ____ _   _ ____ _____ ___  __  __ ___ _____   _    ____  _     _____ 
#  / ___| | | / ___|_   _/ _ \|  \/  |_ _|__  /  / \  | __ )| |   | ____|
# | |   | | | \___ \ | || | | | |\/| || |  / /  / _ \ |  _ \| |   |  _|  
# | |___| |_| |___) || || |_| | |  | || | / /_ / ___ \| |_) | |___| |___ 
#  \____|\___/|____/ |_| \___/|_|  |_|___/____/_/   \_\____/|_____|_____|

locals {
  region = "sa-east-1"
  prefix = "lab"
  instance_type = "t3.medium"
  create_spot_instance = false
  open_ports = [
    "8765"
  ]
}

provider "aws" {
  region = local.region
  default_tags {
    tags = {
      Project = local.project
      Prefix = local.prefix
    }
  }
}

resource "aws_security_group" "instance_sg" {
  name        = "${local.prefix}-${local.project}-${random_string.suffix.result}"
  description = "Security Group for EC2 Instance"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description      = "Allow SSH"
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks     = local.ip_grupo
    #security_groups = [] # Add here more security groups
  }

  ingress {
    description      = "Allow RDP"
    from_port        = 3389
    to_port          = 3389
    protocol         = "tcp"
    cidr_blocks     = local.ip_grupo
    #security_groups = [] # Add here more security groups
  }

  dynamic "ingress" {
    for_each = toset(local.open_ports)
    content {
      description = "Allow for open_ports"
      from_port        = ingress.value
      to_port          = ingress.value
      protocol         = "tcp"
      cidr_blocks     = local.ip_grupo
      # cidr_blocks      = ["0.0.0.0/0"]
    }
  }

  ingress {
    description      = "Allow Subnet Internal Traffic"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
		cidr_blocks =   [data.aws_subnet.default-lab.cidr_block]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "machine" {
  ami                   = data.aws_ami.selected.id
  instance_type          = local.instance_type
  key_name               = local.key_name
  monitoring             = true
  vpc_security_group_ids = [aws_security_group.instance_sg.id]
  subnet_id              = data.aws_subnet.default-lab.id
  associate_public_ip_address = true
  user_data = local.user_data

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
  }

  tags = {
    Name = "${local.prefix}-${local.project}-${random_string.suffix.result}"
  }

  # Wait for cloud-init to finish
  provisioner "remote-exec" {
    inline = [
      "cloud-init status --wait"
    ]
  }

  connection {
    type       = "ssh"
    user      = "ubuntu"
    host       = self.public_ip
    #private_key = file("./your_private_key.pem")
  }
}

#  ____    _  _____  _    
# |  _ \  / \|_   _|/ \   
# | | | |/ _ \ | | / _ \  
# | |_| / ___ \| |/ ___ \ 
# |____/_/   \_\_/_/   \_\

data "aws_vpc" "default" {
  default = true
}

data "aws_subnet" "default-lab" {
  filter {
    name   = "tag:Name"
    values = ["subnet-lab"]
  }
}

data "http" "ipv4" {
  url = "https://ipv4.icanhazip.com"
}

# data "http" "ipv6" {
#   url = "https://ipv6.icanhazip.com"
# }

resource "random_string" "suffix" {
  length = 5
  special = false
  lower  = false
}

#   ___  _   _ _____ ____  _   _ _____ 
#  / _ \| | | |_   _|  _ \| | | |_   _|
# | | | | | | | | | | |_) | | | | | |  
# | |_| | |_| | | | |  __/| |_| | | |  
#  \___/ \___/  |_| |_|    \___/  |_|  

output "public_ip" {
  value = aws_instance.machine.public_ip
}

output "private_ip" {
  value = aws_instance.machine.private_ip
}

output "connection_instruction" {
  value = "ssh ubuntu@${aws_instance.machine.public_ip} -i your_private_key.pem"
}

# Huawei Cloud IaC in CodeArts

This repository contains the code required to deploy a minimal structure to
implement an Infrastructure as Code (IaC) pipeline in Huawei Cloud CodeArts.

## Usage

### Infrastructure

First, create the resources using the code inside `terraform` folder.

Requirements:

- Terraform installed - <https://developer.hashicorp.com/terraform/downloads>

Follow the steps below inside `terraform` folder:

1. Make a copy of `terraform.tfvars.example` named `terraform.tfvars` and
   set AK, SK and passwords;
2. Run `terraform init` the first time to download provider files;
3. Run `terraform plan` to check what will be done;
4. Run `terraform apply` to provision the infrastructure.

### CodeArts

1. Create an Agent Pool: <https://support.huaweicloud.com/intl/en-us/usermanual-devcloud/devcloud_01_0016.html>

2. Enter the Agent Pool created and click on **Create Agent**:
   a. Enable options **Auto Install JDK**, **Auto Install Git** and **Auto Install Docker**
   b. Set a fake AK (e.g `XXXXXXXXXXXXXXXXXXXX`)
   c. Set a fake SK (e.g. `XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)
   d. (Optional) Set an Agent Name (e.g. `ecs-executor`)
   e. Check the option "I have read and agree to the Provacy Statement..."
   f. Click on **Generate Command** and copy it

   #TODO: add screenshot

3. Edit the install command: remove `-a XXXX...` and `-s XXXX...` at the end,
   and add `-8 true` to the end

   ```plain
   Before (example):

   export AGENT_INSTALL_URL=https://cloudoctopus-agent-sa-brazil-1.obs.sa-brazil-1.myhuaweicloud.com/latest/install-octopus-agent.sh;export AGENT_INSTALL_FILE=install-octopus-agent.sh;if [ -f `which curl` ];then curl -# -k -o ${AGENT_INSTALL_FILE} ${AGENT_INSTALL_URL};else wget --no-check-certificate ${AGENT_INSTALL_URL} -O ${AGENT_INSTALL_FILE};fi;bash install-octopus-agent.sh  -u true -c *** -r sa-brazil-1 -f *** -h cloudoctopus-agent-sa-brazil-1.obs.sa-brazil-1.myhuaweicloud.com -n ecs-executor -w /opt/agent_1777498746834 -g true -j true -b true -d true -z myhuaweicloud.com -o true -a XXXXXXXXXXXXXXXXXXXX -s b06E8nNPaPIgL0HsDz93cMVMOKmLOrktQj1pl2UQE1BtQ1cs3GiOzt+RoNpglIYcXCOxrMJ5UFjuZ9UTcizX2I3cihI6IoZzED1my0/cnwXaz7YWINpOYHSdRDwCJBL8RiCGkrgu+MO9y4v+OfWkxxBuY9ljN/oeDy1aSmM+ReYUvwoiV7raW6eeAe32aiuW32M2bx8bu7jFmEgsklCvMQq9JBVz3TJTkb62xDCDPf2c0DdG4qui6irbgTDMliI+0d/+mSPLZ/nMuyzUj+uSdtdq1HCM+maEZCNxT3TiVEYLbcJ48EfhMY3iB3HNMMKagr1aPLI4vqF3gtmOCHXzt0H5x4jy1094w3vHRqNGkMW/rPkzXYfH81I2Ewhfz3zHC70qM2ThuZr9VpZ4aI6hJhABjDqyeWTl0jGRRc3ZsvY+yzt6O15kNnwj/Km1a86xnPGBbLwVkKFz/lM1EAsee3hldtdDZcOqMoUFr1zJz/3HgDkGIhbKCdD/O+m64vvt


   After (example):

   export AGENT_INSTALL_URL=https://cloudoctopus-agent-sa-brazil-1.obs.sa-brazil-1.myhuaweicloud.com/latest/install-octopus-agent.sh;export AGENT_INSTALL_FILE=install-octopus-agent.sh;if [ -f `which curl` ];then curl -# -k -o ${AGENT_INSTALL_FILE} ${AGENT_INSTALL_URL};else wget --no-check-certificate ${AGENT_INSTALL_URL} -O ${AGENT_INSTALL_FILE};fi;bash install-octopus-agent.sh  -u true -c *** -r sa-brazil-1 -f *** -h cloudoctopus-agent-sa-brazil-1.obs.sa-brazil-1.myhuaweicloud.com -n ecs-executor -w /opt/agent_1777498746834 -g true -j true -b true -d true -z myhuaweicloud.com -o true -8 true
   ```

4. Log in to `ecs-executor` and run the modified command. If the message
   `End Install Octopus Agent,Agent output logs have been printed to [ /opt/octopus-agent/logs/octopus-agent.log ]`
   is displayed, the installation is successful.

## References

- Huawei Cloud Terraform provider documentation: <https://registry.terraform.io/providers/huaweicloud/huaweicloud/latest/docs>
- Huawei Cloud Terraform boilerplate: <https://github.com/huaweicloud-latam/terraform-boilerplate>

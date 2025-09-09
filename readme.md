# Make the EC2 Ready 
sudo yum update -y   # Amazon Linux
sudo yum install -y docker
sudo service docker start
sudo usermod -aG docker ec2-user
sudo systemctl enable docker

# install git 
sudo yum update -y
sudo yum install -y git

# setup git profile 
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Setup repo and run the application
git clone <your-repo>
cd <repo>

# create a .env file 
nano .env 
################### content of the file ###########################
USERNAME=cortellis-api-username
PASSWORD=cortellis-api-password
###################################################################

docker build -t getaddress-mcp-server .
docker run -p 8000:8000 getaddress-mcp-server


# mcp client config 
{
  "servers": {
    "AddressServer": {
      "type": "http",
      "url": "http://ec2-18-246-212-234.us-west-2.compute.amazonaws.com:8000/mcp"
    }
  }
}

Url should be the domain of the ec2

# dummy questions that can be asked 
1. Please find the validity categories of biomarker troponin 
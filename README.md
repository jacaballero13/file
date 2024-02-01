# How to install Odoo13 Community Version, PostgreSql 9.6 and PgAdmin on Ubuntu 20.04
as
## Set-up and Commands

### Update the System:
 - sudo apt-get update -y && sudo apt-get upgrade -y
 
### Import PostgreSQL 9.6 GPG public key:
 - wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
 
### Add PostgreSQL 9.6 repository:
 - echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/postgresql-pgdg.list > /dev/null
 - sudo apt-get update -y
 
### Installing PostgreSQL 9.6:
 - sudo apt-get install postgresql-9.6
 - systemctl status postgresql
 - systemctl is-enabled postgresql
 
### Install Wkhtmltopdf:
 - wget https://github.com/wkhtmltopdf/wkhtmltopdf/release/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb
 - sudo dpkg -l wkhtml_0.12.5-1.bionic_amd64.deb
 - sudo apt -f install
 
### Verify that wkhtmltopdf is successfully installed:
 - which wkhtmltopdf
 - which wkhtmltoimage
 
### Install pgAdmin:
Pre-requisite --> curl

 - sudo apt install curl
 
### Add public key using curl:
 - sudo curl https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo apt-key add
 
### Add pgAdmin respository and update server’s packages:
 - sudo sh -c ‘echo “deb https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb release -cs) pgadmin4 main” > /etc/apt/resources.list.d/pgadmin4.list && apt update’

### Install pgAdmin:
 - sudo apt install pgadmin4
 
### Install Oddo 13:
 - sudo wget -O – https://nightly.odoo.com/odoo.key | sudo apt-key add –
 - sudo echo “deb http://nightly.odoo.com/13.0/nightly/deb/ ./” | sudo tee -a 
   /etc/apt/sources.list.d/odoo.list
 - sudo apt-get update
 - sudo apt-get install odoo
 - systemctl status odoo
 - systemctl is-enabled odoo

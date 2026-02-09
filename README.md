# MTLS SSL Certificates Generator
# generate documentation
This project provides a simple tool to generate SSL certificates for mutual TLS (mTLS) authentication. It automates the process of creating a Certificate Authority (CA), server certificates, and client certificates.

## Features
- Generates a self-signed Certificate Authority (CA)
- Creates server certificates signed by the CA
- Creates client certificates signed by the CA
- Easy-to-use command-line interface

## How to Use
1. Clone the repository
2. No need to create a virtual environment or install dependencies, just run the script directly or via VSCode Run and Debug

## Via VSCode Run and Debug
1. In VSCode go to Run and Debug tab and you can go one by one through "Create CA", "Create Server Certificate", "Create Client Certificate" configurations.
2. Follow the prompts to enter the required information.

## Via command line
1. For help with command-line options, run:
   ```
   python3 mtls_ssl_generator.py --help
    ```
2. Example process
    ```
    To create a fresh new CA.pem with CA.key from which you can later create server and client certificates:
      python3 mtls_ssl_generator.py --create-ca --organization-unit MyOrganizationUnit --common-name MyOrganizationUnit-Root-CA
      
    To create a server certificate signed by the above created CA - you need to specify the CA path (just the organization unit name, the script will look for CA.pem and CA.key in the generated_certificates directory):
      python3 mtls_ssl_generator.py --create-server --common-name mqtt-server --ca-path MyOrganizationUnit

    To create a client certificate signed by the above created CA - you need to specify the CA path (just the organization unit name, the script will look for CA.pem and CA.key in the generated_certificates directory):
      python3 mtls_ssl_generator.py --create-client --common-name myclient --ca-path MyOrganizationUnit

3. Output files will be saved in the generated_certificates directory.


Right now there are hardcoded values for My Organization. - Country = DE, Organization = My Organization<br>
You can specify Common Name (CN) and Organization Unit (OU)<br>
Validity is set to 10 years
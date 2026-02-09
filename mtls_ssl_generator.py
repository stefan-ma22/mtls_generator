import argparse
import subprocess
import sys
from pathlib import Path

def run(cmd):
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True)

def ensure_ou_directory_exists(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def ensure_ca_exists(ca_directory: Path):
    ca_key = ca_directory / "ca.key"
    ca_pem = ca_directory / "ca.pem"

    if not ca_key.exists() or not ca_pem.exists():
        raise FileNotFoundError(f"CA not found in {ca_directory}. Please create CA first.")

def create_ca(organization_unit_as_subdirectory: Path, common_name: str):
    ensure_ou_directory_exists(organization_unit_as_subdirectory)

    ca_key = organization_unit_as_subdirectory / "ca.key"
    ca_pem = organization_unit_as_subdirectory / "ca.pem"

    if ca_pem.exists():
        print(f"CA already exists in {organization_unit_as_subdirectory}, refusing to overwrite")
        return

    run(["openssl", "genrsa", "-out", str(ca_key), "4096"])

    run([
        "openssl", "req", "-x509", "-new", "-nodes",
        "-key", str(ca_key),
        "-sha256",
        "-days", "3650",
        "-out", str(ca_pem),
        "-subj", f"/C=DE/O=MyOrganization/OU=MyUnit/CN={common_name}"
    ])
    
    print(f"Created ca.pem in {organization_unit_as_subdirectory}/ca.pem")
    print(f"Created ca.key in {organization_unit_as_subdirectory}/ca.key")

def create_server(ca_directory: Path, output_directory: Path, hostname: str):
    ensure_ou_directory_exists(output_directory)
    ensure_ca_exists(ca_directory)

    ext = output_directory / "server.ext"
    ext.write_text(
        f"""\
            authorityKeyIdentifier=keyid,issuer
            basicConstraints=CA:FALSE
            keyUsage=digitalSignature,keyEncipherment
            extendedKeyUsage=serverAuth
            subjectAltName=@alt

            [alt]
            DNS.1={hostname}
            IP.1=127.0.0.1
        """)

    run(["openssl", "genrsa", "-out", str(output_directory / "server.key"), "2048"])

    run([
        "openssl", "req", "-new",
        "-key", str(output_directory / "server.key"),
        "-out", str(output_directory / "server.csr"),
        "-subj", f"/C=DE/O=MyOrganization/OU=MyUnit/CN={hostname}"
    ])

    run([
        "openssl", "x509", "-req",
        "-in", str(output_directory / "server.csr"),
        "-CA", str(ca_directory / "ca.pem"),
        "-CAkey", str(ca_directory / "ca.key"),
        "-CAcreateserial",
        "-out", str(output_directory / "server.pem"),
        "-days", "825",
        "-sha256",
        "-extfile", str(ext)
    ])
    
    # Cleanup
    ext.unlink()
    (output_directory / "server.csr").unlink()

def create_client(ca_directory: Path, output_directory: Path, common_name: str):
    ensure_ou_directory_exists(output_directory)

    ext = output_directory / f"{common_name}.ext"
    ext.write_text(
        f"""\
            authorityKeyIdentifier=keyid,issuer
            basicConstraints=CA:FALSE
            keyUsage=digitalSignature
            extendedKeyUsage=clientAuth
        """)

    run(["openssl", "genrsa", "-out", str(output_directory / f"{common_name}.key"), "2048"])

    run([
        "openssl", "req", "-new",
        "-key", str(output_directory / f"{common_name}.key"),
        "-out", str(output_directory / f"{common_name}.csr"),
        "-subj", f"/C=DE/O=MyOrganization/OU=MyOrganizationUnit/CN={common_name}"
    ])

    run([
        "openssl", "x509", "-req",
        "-in", str(output_directory / f"{common_name}.csr"),
        "-CA", str(ca_directory / "ca.pem"),
        "-CAkey", str(ca_directory / "ca.key"),
        "-CAcreateserial",
        "-out", str(output_directory / f"{common_name}.pem"),
        "-days", "825",
        "-sha256",
        "-extfile", str(ext)
    ])
    
    # Cleanup
    ext.unlink()
    (output_directory / f"{common_name}.csr").unlink()

def main():
    parser = argparse.ArgumentParser(description="mTLS certificate generator")
    parser.add_argument("--organization-unit", action="store", help="Name of the CA organization unit to also use as directory name")
    parser.add_argument("--create-ca", action="store_true", help="Use if you want to create a new CA")
    parser.add_argument("--create-server", action="store_true", help="Use if you want to create server cert for mTLS from existing CA")
    parser.add_argument("--create-client", action="store_true", help="Use if you want to create client cert for mTLS from existing CA")
    parser.add_argument("--ca-path",  action="store", help="Path to the directory where is CA from which you create server/client certificates")
    parser.add_argument("--common-name", action="store", help="Common name for the CA/Server/Client certificates")
    
    # add help for the script when no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        # example usage
        print("\nExample usage:")
        print("To create a fresh new CA.pem with CA.key from which you can later create server and client certificates:")
        print("  python3 mtls_ssl_generator.py --create-ca --organization-unit MyOrganizationUnit --common-name MyOrganizationUnit-Root-CA\n")
        print("To create a server certificate signed by the above created CA - you need to specify the CA path:")
        print("  python3 mtls_ssl_generator.py --create-server --common-name mqttt-server --ca-path MyOrganizationUnit\n")
        print("To create a client certificate signed by the above created CA - you need to specify the CA path:")
        print("  python3 mtls_ssl_generator.py --create-client --common-name myclient --ca-path MyOrganizationUnit\n")
        return
    
    args = parser.parse_args()
    
    # ensure generated_certificates directory exists
    ensure_ou_directory_exists(Path("generated_certificates"))

    ca_directory = Path("generated_certificates") / (args.organization_unit if args.create_ca else Path(args.ca_path))

    if args.create_ca:
        create_ca(ca_directory, args.common_name)

    if args.create_server:
        create_server(ca_directory, ca_directory / "server", args.common_name)

    if args.create_client:
        create_client(ca_directory, ca_directory / "clients" / args.common_name, args.common_name)

    if not (args.create_ca or args.create_server or args.create_client):
        parser.print_help()

if __name__ == "__main__":
   main()
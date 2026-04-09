# apps/finance/cert_push.py
"""
MikroTik Certificate Push Service
===================================
After Let's Encrypt renewal, generates a .p12 bundle (no password)
and pushes it to the MikroTik router via SCP, then imports and binds
it to the hotspot profile and SSL services via SSH.

RouterOS 7.22 - certificate import is CLI only (not available via API).
Uses paramiko for SCP file transfer and SSH command execution.
"""
import os
import io
import logging
import tempfile

logger = logging.getLogger(__name__)

CERT_DIR      = '/etc/letsencrypt/live/teralinkxwaves.uk'
FULLCHAIN     = os.path.join(CERT_DIR, 'fullchain.pem')
PRIVKEY       = os.path.join(CERT_DIR, 'privkey.pem')
P12_FILENAME  = 'teralinkxwaves.p12'
# The cert name RouterOS assigns after import (filename without extension + _0)
CERT_NAME     = 'teralinkxwaves.p12_0'
# Hotspot profile that uses the cert
HOTSPOT_PROFILE = 'teralinkx'


def generate_p12(fullchain_path: str, privkey_path: str) -> bytes:
    """
    Generate a PKCS12 (.p12) bundle from PEM cert + key.
    No password — MikroTik import requires passphrase="" for passwordless .p12.
    """
    from cryptography.hazmat.primitives.serialization import pkcs12
    from cryptography.hazmat.primitives.serialization import (
        Encoding, PrivateFormat, NoEncryption
    )
    from cryptography.hazmat.primitives import serialization
    from cryptography import x509

    with open(privkey_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    with open(fullchain_path, 'rb') as f:
        pem_data = f.read()

    # Parse all certs in the chain
    certs = []
    for cert_pem in pem_data.split(b'-----END CERTIFICATE-----'):
        cert_pem = cert_pem.strip()
        if cert_pem:
            cert_pem += b'\n-----END CERTIFICATE-----\n'
            try:
                certs.append(x509.load_pem_x509_certificate(cert_pem))
            except Exception:
                pass

    if not certs:
        raise ValueError("No certificates found in fullchain.pem")

    leaf_cert = certs[0]
    ca_certs   = certs[1:] if len(certs) > 1 else []

    p12_data = pkcs12.serialize_key_and_certificates(
        name=b'teralinkxwaves',
        key=private_key,
        cert=leaf_cert,
        cas=ca_certs,
        encryption_algorithm=NoEncryption()  # no password
    )
    logger.info(f"Generated .p12 bundle ({len(p12_data)} bytes)")
    return p12_data


def push_cert_to_mikrotik() -> dict:
    """
    Full cert push flow:
      1. Generate .p12 from Let's Encrypt certs
      2. SCP .p12 to router
      3. SSH: import cert
      4. SSH: bind to hotspot profile + www-ssl + api-ssl
      5. SSH: remove old certs
    Returns dict with success status and details.
    """
    import paramiko
    from finance.authentications import RouterConfig

    config = RouterConfig.get_config()
    host     = config['host']
    username = config['username']
    password = config['password']
    ssh_port = 22

    result = {
        'success': False,
        'steps': [],
        'error': None
    }

    # Step 1: Generate .p12
    try:
        p12_data = generate_p12(FULLCHAIN, PRIVKEY)
        result['steps'].append('p12_generated')
    except Exception as e:
        result['error'] = f"p12 generation failed: {e}"
        logger.error(result['error'])
        return result

    # Step 2: SCP to router
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, port=ssh_port, username=username, password=password, timeout=10)

        # SCP via SFTP
        sftp = ssh.open_sftp()
        with sftp.open(P12_FILENAME, 'wb') as remote_file:
            remote_file.write(p12_data)
        sftp.close()
        result['steps'].append('scp_uploaded')
        logger.info(f"Uploaded {P12_FILENAME} to {host}")

        # Step 3: Import certificate
        stdin, stdout, stderr = ssh.exec_command(
            f'/certificate import file-name={P12_FILENAME} passphrase=""'
        )
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        logger.info(f"cert import output: {out} {err}")
        result['steps'].append('cert_imported')

        # Step 4a: Bind to hotspot profile
        stdin, stdout, stderr = ssh.exec_command(
            f'/ip hotspot profile set {HOTSPOT_PROFILE} ssl-certificate={CERT_NAME}'
        )
        stdout.read()
        result['steps'].append('hotspot_profile_updated')
        logger.info(f"Bound {CERT_NAME} to hotspot profile {HOTSPOT_PROFILE}")

        # Step 4b: Bind to www-ssl
        stdin, stdout, stderr = ssh.exec_command(
            f'/ip service set www-ssl certificate={CERT_NAME} disabled=no'
        )
        stdout.read()
        result['steps'].append('www_ssl_updated')

        # Step 4c: Bind to api-ssl
        stdin, stdout, stderr = ssh.exec_command(
            f'/ip service set api-ssl certificate={CERT_NAME}'
        )
        stdout.read()
        result['steps'].append('api_ssl_updated')

        # Step 5: Remove old certs - keep only the one we just imported
        # Re-query certs after import to get the new cert's .id
        from finance.authentications import RouterManager as _RM, RouterConfig as _RC
        with _RM(_RC.get_config()) as _router:
            all_certs = _router.execute_command('/certificate', 'print')
            # Find the newest cert with our name (highest .id number)
            # Leaf cert has common-name matching our domain
            # CA/intermediate certs have short names like 'E7', 'E8', 'R3'
            leaf_certs = [
                c for c in all_certs
                if 'teralinkxwaves' in c.get('common-name', '').lower()
            ]
            old_certs = [
                c for c in all_certs
                if 'teralinkxwaves' in c.get('name', '').lower()
                and 'teralinkxwaves' not in c.get('common-name', '').lower()
            ]
            our_certs = leaf_certs  # for removal loop below
            if leaf_certs:
                keep_id = leaf_certs[-1].get('.id')
                keep_name = leaf_certs[-1].get('name')
                logger.info(f'Keeping cert: {keep_name} id={keep_id}')
                # Bind services to the kept cert
                _router.execute_command('/ip/hotspot/profile', 'set',
                    **{'numbers': HOTSPOT_PROFILE, 'ssl-certificate': keep_name})
                _router.execute_command('/ip/service', 'set',
                    **{'numbers': 'www-ssl', 'certificate': keep_name, 'disabled': 'no'})
                _router.execute_command('/ip/service', 'set',
                    **{'numbers': 'api-ssl', 'certificate': keep_name})
                # Remove all others
                for _c in list(leaf_certs[:-1]) + list(old_certs):
                    try:
                        _router.execute_command('/certificate', 'remove',
                            **{'numbers': _c.get('.id')})
                        logger.info(f'Removed old cert: {_c.get("name")} id={_c.get(".id")}')
                    except Exception as _e:
                        logger.warning(f'Could not remove cert: {_e}')

        result['steps'].append('old_certs_removed')
        result['success'] = True
        logger.info("Certificate push to MikroTik completed successfully")

    except Exception as e:
        result['error'] = f"SSH/SCP error: {e}"
        logger.error(result['error'], exc_info=True)
    finally:
        ssh.close()

    return result


def check_cert_expiry() -> dict:
    """Check days until current cert expires."""
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from django.utils import timezone
    import datetime

    try:
        with open(FULLCHAIN, 'rb') as f:
            cert = x509.load_pem_x509_certificate(f.read(), default_backend())
        expires_at = cert.not_valid_after_utc
        days_left  = (expires_at - timezone.now()).days
        return {
            'expires_at': expires_at.isoformat(),
            'days_left':  days_left,
            'needs_renewal': days_left < 30
        }
    except Exception as e:
        return {'error': str(e)}

"""
Environment & Infrastructure Verification Script
Checks environment variables, PostgreSQL, Qdrant, and native host Ollama connectivity.
"""
import os
import sys
import socket
import json
import urllib.request
from pathlib import Path

# Add project root and backend to sys.path so backend.app.core.config can be imported
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))


def print_header(title: str):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def check_tcp_port(host: str, port: int, timeout: float = 3.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def verify_settings():
    print_header("1. ENVIRONMENT SETTINGS VERIFICATION")
    try:
        from app.core.config import get_settings
        settings = get_settings()
        print(f"[PASS] Settings loaded successfully from .env")
        print(f"  - Project: {settings.PROJECT_NAME}")
        print(f"  - Environment: {settings.ENVIRONMENT}")
        print(f"  - PostgreSQL Target: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB} (User: {settings.POSTGRES_USER})")
        print(f"  - Qdrant Target: {settings.QDRANT_HOST}:{settings.QDRANT_PORT} (Collection: {settings.QDRANT_COLLECTION})")
        print(f"  - Ollama Target: {settings.OLLAMA_BASE_URL} (Model: {settings.OLLAMA_MODEL})")
        print(f"  - Embedding Pipeline: {settings.EMBEDDING_MODEL_NAME} ({settings.EMBEDDING_DIMENSION}-dim)")
        return settings, True
    except Exception as e:
        print(f"[FAIL] Error loading settings: {e}")
        return None, False


def verify_postgres(settings):
    print_header("2. POSTGRESQL CONNECTIVITY")
    host = settings.POSTGRES_HOST
    port = settings.POSTGRES_PORT
    is_port_open = check_tcp_port(host, port)
    
    if not is_port_open:
        print(f"[WARN] PostgreSQL port {host}:{port} is not reachable.")
        print(f"       If running via Docker, start containers using: docker compose -f docker/docker-compose.yml up -d")
        return False

    print(f"[PASS] PostgreSQL port {host}:{port} is open and accepting TCP connections.")
    
    # Attempt SQL handshake if psycopg is available
    try:
        import psycopg
        conn = psycopg.connect(
            host=host,
            port=port,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            dbname=settings.POSTGRES_DB,
            connect_timeout=3
        )
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print(f"[PASS] PostgreSQL authenticated query succeeded:")
            print(f"       Version: {version}")
        conn.close()
        return True
    except ImportError:
        print(f"[INFO] psycopg not installed in current Python env; TCP port check passed.")
        return True
    except Exception as e:
        print(f"[FAIL] PostgreSQL connection handshake failed: {e}")
        return False


def verify_qdrant(settings):
    print_header("3. QDRANT VECTOR DATABASE CONNECTIVITY")
    host = settings.QDRANT_HOST
    port = settings.QDRANT_PORT
    is_port_open = check_tcp_port(host, port)
    
    if not is_port_open:
        print(f"[WARN] Qdrant port {host}:{port} is not reachable.")
        print(f"       If running via Docker, start containers using: docker compose -f docker/docker-compose.yml up -d")
        return False

    print(f"[PASS] Qdrant port {host}:{port} is open.")
    
    # Query Qdrant HTTP health endpoint
    try:
        url = f"http://{host}:{port}/readyz"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            status = resp.status
            if status == 200:
                print(f"[PASS] Qdrant /readyz healthcheck returned HTTP 200 (Engine Ready)")
                return True
            else:
                print(f"[WARN] Qdrant /readyz returned unexpected status code: {status}")
                return False
    except Exception as e:
        # Fallback to /collections
        try:
            url = f"http://{host}:{port}/collections"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                print(f"[PASS] Qdrant /collections endpoint reachable (HTTP {resp.status})")
                return True
        except Exception as e2:
            print(f"[WARN] Could not perform HTTP healthcheck on Qdrant: {e2}")
            return False


def verify_ollama(settings):
    print_header("4. LOCAL HOST OLLAMA CONNECTIVITY")
    base_url = settings.OLLAMA_BASE_URL.rstrip("/")
    tags_url = f"{base_url}/api/tags"
    
    try:
        req = urllib.request.Request(tags_url, method="GET")
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name") for m in data.get("models", [])]
                print(f"[PASS] Ollama server is active and reachable at {base_url}")
                print(f"       Installed Models: {', '.join(models) if models else 'None'}")
                
                target_model = settings.OLLAMA_MODEL
                matching = [m for m in models if target_model in m]
                if matching:
                    print(f"[PASS] Target model '{target_model}' is available ({matching[0]}).")
                    return True
                else:
                    print(f"[WARN] Target model '{target_model}' was not found in installed models.")
                    print(f"       Install it using: ollama pull {target_model}")
                    return False
            else:
                print(f"[FAIL] Ollama returned status {resp.status}")
                return False
    except Exception as e:
        print(f"[FAIL] Ollama is not reachable at {base_url}: {e}")
        print(f"       Ensure Ollama service is running on the host machine.")
        return False


def main():
    print("=" * 70)
    print(" ENTERPRISE RAG SECURITY: MILESTONE 1 ENVIRONMENT VERIFICATION")
    print("=" * 70)
    
    settings, settings_ok = verify_settings()
    if not settings_ok:
        print("\n[SUMMARY] Environment verification failed due to missing or invalid settings.")
        sys.exit(1)
        
    pg_ok = verify_postgres(settings)
    qd_ok = verify_qdrant(settings)
    ollama_ok = verify_ollama(settings)
    
    print_header("VERIFICATION SUMMARY")
    print(f"  Configuration Loader:   {'[ PASS ]' if settings_ok else '[ FAIL ]'}")
    print(f"  PostgreSQL Reachability:{'[ PASS ]' if pg_ok else '[ WARN/FAIL ]'}")
    print(f"  Qdrant Reachability:    {'[ PASS ]' if qd_ok else '[ WARN/FAIL ]'}")
    print(f"  Host Ollama & Qwen3:4B: {'[ PASS ]' if ollama_ok else '[ WARN/FAIL ]'}")
    print("=" * 70)
    
    if settings_ok and ollama_ok:
        print("\nEnvironment foundations are properly configured.")
        if not (pg_ok and qd_ok):
            print("Note: Start the container infrastructure using: docker compose -f docker/docker-compose.yml up -d")
    print()


if __name__ == "__main__":
    main()

"""Run Milestone 4 deterministic and mocked end-to-end tests."""
import subprocess, sys

if __name__ == "__main__":
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", "-q", "tests"]))


import json
import sys
from pathlib import Path


report_path = Path("trivy-image-report.json")

if not report_path.is_file():
    print("ERROR: Trivy report was not generated.")
    sys.exit(2)

try:
    with report_path.open(encoding="utf-8") as file:
        report = json.load(file)
except (OSError, json.JSONDecodeError) as error:
    print(f"ERROR: Cannot read Trivy report: {error}")
    sys.exit(2)


critical = []

for result in report.get("Results") or []:
    for vulnerability in result.get("Vulnerabilities") or []:
        if vulnerability.get("Severity") == "CRITICAL":
            critical.append({
                "id": vulnerability.get("VulnerabilityID"),
                "package": vulnerability.get("PkgName"),
                "installed": vulnerability.get("InstalledVersion"),
                "fixed": vulnerability.get("FixedVersion"),
            })


print(f"Critical vulnerabilities found: {len(critical)}")

for item in critical:
    print(
        f"{item['id']} | {item['package']} | "
        f"installed={item['installed']} | fixed={item['fixed']}"
    )

if critical:
    print("CRITICAL vulnerability gate failed.")
    sys.exit(1)

print("CRITICAL vulnerability gate passed.")

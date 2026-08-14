"""Deploy one src/fabric/<function> folder to its matching Fabric workspace via fabric-cicd.

Used by .github/workflows/deploy-acceptance.yml and deploy-production.yml. Authenticates with
whatever Azure identity `azure/login` (OIDC, no stored secrets) leaves active in the runner's CLI
session — no client secret ever touches this script or the pipeline definition.

Usage:
    python scripts/deploy_fabric_items.py \
        --environment acc \
        --workspace-name lakehouse-acc \
        --repository-directory src/fabric/lakehouse
"""

import argparse

import requests
from azure.identity import AzureCliCredential
from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items

FABRIC_RESOURCE = "https://api.fabric.microsoft.com"
FABRIC_API_ROOT = f"{FABRIC_RESOURCE}/v1"


def resolve_workspace_id(workspace_name: str, credential: AzureCliCredential) -> str:
    token = credential.get_token(f"{FABRIC_RESOURCE}/.default")
    response = requests.get(
        f"{FABRIC_API_ROOT}/workspaces",
        headers={"Authorization": f"Bearer {token.token}"},
        timeout=30,
    )
    response.raise_for_status()
    for workspace in response.json()["value"]:
        if workspace["displayName"] == workspace_name:
            return workspace["id"]
    raise ValueError(f"Workspace '{workspace_name}' not found or not accessible to this identity.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", required=True, choices=["acc", "prod"])
    parser.add_argument("--workspace-name", required=True)
    parser.add_argument("--repository-directory", required=True)
    parser.add_argument(
        "--items-in-scope",
        default="Notebook,DataPipeline,Lakehouse,Environment",
        help="Comma-separated Fabric item types to deploy.",
    )
    parser.add_argument("--parameter-file", default="config/parameter.yml")
    args = parser.parse_args()

    credential = AzureCliCredential()
    workspace_id = resolve_workspace_id(args.workspace_name, credential)

    workspace = FabricWorkspace(
        workspace_id=workspace_id,
        environment=args.environment,
        repository_directory=args.repository_directory,
        item_type_in_scope=args.items_in_scope.split(","),
        token_credential=credential,
        parameter_file_path=args.parameter_file,
    )

    publish_all_items(workspace)
    unpublish_all_orphan_items(workspace)


if __name__ == "__main__":
    main()

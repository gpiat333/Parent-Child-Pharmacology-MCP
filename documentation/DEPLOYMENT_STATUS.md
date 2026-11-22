# What is running, what was tested, and what deployment means

**A GitHub push updates files. An application deployment changes the service users connect to.** Those are separate actions in this project. The current work updates source, tests, documentation and submission materials; it does not replace the running Databricks App.

| Component | Current state | What changes when released |
|---|---|---|
| Private GitHub repository | Holds the revised source and submission artifacts; Windows/Linux CI tests the committed package | A push changes repository contents, not the live MCP service |
| Local MCP service | Started on loopback for fresh evaluation, then stopped | A local test process is not a shared hosted service |
| Databricks test notebook | Runs the revised application tests in an isolated job environment | Uploading a test bundle and running a notebook does not install it into the App |
| Databricks model gateway | Supplies model calls for evaluations using the existing model configuration | This work does not create or redeploy a model endpoint |
| Databricks MLflow | Stores runs, scores, traces and reviewed artifacts | Logging an experiment does not serve the MCP or change its App deployment |
| Existing Databricks App `mcp-mc` | Still the historical **.9** deployment, ID `01f1e5f7f6fc162fb8c3cc875e7f8546` | A deliberate App deployment is needed to run the revised package there |
| Companion chat client | Revised local client scripts and output contracts | Any hosted client must be updated too; the server cannot force an arbitrary client to enforce its safety/display contracts |

## What a future hosted release would involve

1. Choose the evaluated source commit and package its dependencies, policy, bundled MPRINT snapshots and required configuration together. Confirm the intended transport and compute/runtime support.
2. Configure the host's access and network controls. The revised server defaults to local stdio; remote HTTP requires the documented operator-managed RS256 issuer, public key, audience and tool scopes. Existing Databricks gateway access alone is not proof that the new server's bearer-token contract is configured. Confirm how the gateway/client obtains and supplies the appropriate server token without broadening access.
3. Configure secrets through the hosting environment, permitted outbound source access, logging/trace retention and the intended user audience. Do not put credentials into source, demo traces or the submission package.
4. Deploy the selected package to the hosted App and update the intended companion/client configuration. Keep the old release available for rollback.
5. Run hosted protocol, authentication/authorization, source-connectivity, fixed-stop, display-contract and fresh chat checks against that exact deployment. Local tests, Databricks notebook tests and CI do not replace hosted integration checks.

No new model training, new model endpoint, new database, or public GitHub release is inherently required for these code changes. Spanish chat also does not become supported merely by deploying the package: its review prerequisites remain separate in [Language support](LANGUAGE_SUPPORT.md).

The existing App is not a live demonstration of the newest evaluation results. This work makes no production-readiness, penetration-test or clinical-certification claim. [Security requirements](../SECURITY.md) and the [latest evaluation index](../evaluation/README.md) record remaining boundaries.

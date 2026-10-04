{ pkgs, lib, wakapiSdk, ... }:
with pkgs.python3Packages;

# MCP 2026-07-28 needs fastmcp 4.x on the mcp 2.x SDK. No available nixpkgs
# carries it: the pinned nixpkgs (2025-09-19) resolves fastmcp 2.11.3 / mcp
# 1.14.0, and current nixos-unstable only reaches fastmcp 3.4.7 / mcp 1.29.0.
# The build therefore fails pythonRuntimeDepsCheck against pyproject.toml
# until nixpkgs ships fastmcp 4. Until then, use `uv sync` from pyproject.toml.
buildPythonPackage {
  pname = "mcp-wakapi";
  version = "0.2.0";

  src = ./.;

  pyproject = true;

  dependencies = [
    fastmcp
    mcp
    toml
    # Serves the Streamable HTTP app in `--transport http`. The mcp SDK
    # requires uvicorn too, but that transitive dependency is not a contract.
    uvicorn

    wakapiSdk
  ];

  build-system = [ hatchling ];

  postPatch = ''
    substituteInPlace pyproject.toml \
      --replace "{root:uri}/wakapi_sdk_project" "$PWD/wakapi_sdk_project"
  '';

  meta = with lib; {
    description = "MCP server for collecting logs from Wakapi";
    homepage = "https://github.com/impure0xntk/mcp-wakapi";
    license = licenses.asl20;
    maintainers = with maintainers; [ impure0xntk ];
    mainProgram = "wakapi-mcp";
  };
}
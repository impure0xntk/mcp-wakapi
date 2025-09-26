{ pkgs, lib, wakapiSdk, ... }:
with pkgs.python3Packages;
buildPythonPackage {
  pname = "mcp-wakapi";
  version = "0.1.0";

  src = ./.;

  pyproject = true;

  dependencies = [
    fastmcp
    toml

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
{ pkgs, lib, ... }:
with pkgs.python3Packages;
buildPythonPackage {
  pname = "wakapi_sdk";
  version = "0.1.0";

  src = ./.;

  pyproject = true;

  build-system = [ hatchling ];
  dependencies = [ httpx pydantic structlog ];
  devDependencies = [ pytest pytest-asyncio ];

  meta = with lib; {
    description = "SDK for interacting with Wakapi API";
    homepage = "https://github.com/impure0xntk/mcp-wakapi";
    license = licenses.asl20;
    maintainers = with maintainers; [ impure0xntk ];
  };
}

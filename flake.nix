{
  description = "MCP server for collecting logs from Wakapi";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";

    wakapi-sdk = {
      url = "./wakapi_sdk_project";
      inputs = {
        nixpkgs.follows = "nixpkgs";
        flake-utils.follows = "flake-utils";
      };
    };
  };
  outputs = { self, nixpkgs, flake-utils, wakapi-sdk }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        lib = nixpkgs.lib;
        wakapiSdk = wakapi-sdk.packages.${system}.default;

        packages = {
          default = self.packages.${system}.mcp-wakapi;
          mcp-wakapi = pkgs.callPackage ./default.nix { inherit wakapiSdk; };
        };
      in {
        inherit packages;

        devShells.default = pkgs.mkShell {
          buildInputs = [
            pkgs.uv
          ];

          shellHook = ''
            # Python environment setup
            export PYTHONPATH="${pkgs.python3}/lib/python${lib.versions.majorMinor pkgs.python3.version}/site-packages:$PWD/src:$PYTHONPATH"

            # Manage dependencies with uv
            uv venv --python ${pkgs.python3}/bin/python
            uv sync --dev

            # Activate virtual environment
            source .venv/bin/activate

            echo "Development environment started"
            echo "Python version: $(python --version)"
            echo "uv version: $(uv --version)"
          '';
        };
      });
}

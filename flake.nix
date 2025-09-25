{
  description = "MCP server for collecting logs from Wakapi";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python312Packages = pkgs.python312Packages;
        python-with-packages = pkgs.python312.withPackages (ps: with ps; [
          httpx
          fastmcp
          pydantic
          python-dotenv
          toml
          structlog
          pip
          pytest
          python312Packages.pytest-asyncio
        ]);
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pkgs.uv
            python-with-packages
          ];

          shellHook = ''
            # Python environment setup
            export PYTHONPATH="${pkgs.python312}/lib/python3.12/site-packages:$PWD/src:$PYTHONPATH"

            # Manage dependencies with uv
            uv venv --python ${pkgs.python312}/bin/python
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

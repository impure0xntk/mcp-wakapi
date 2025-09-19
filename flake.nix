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
        python-with-packages = pkgs.python3.withPackages (ps: with ps; [
          httpx
          fastmcp
          pydantic
          python-dotenv
        ]);
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pkgs.uv
            python-with-packages
          ];
          
          shellHook = ''
            # Python環境の設定
            export PYTHONPATH="$PWD/src:$PYTHONPATH"
            
            # uvで依存関係を管理
            if [ ! -d .venv ]; then
              uv venv
            fi
            
            # 仮想環境をアクティベート
            source .venv/bin/activate
            
            echo "開発環境が起動しました"
            echo "Pythonバージョン: $(python --version)"
            echo "uvバージョン: $(uv --version)"
          '';
        };
      });
}
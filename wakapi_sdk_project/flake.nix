{
  description = "Nix flake for wakapi_sdk";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        packages = {
          default = self.packages.${system}.wakapi-sdk;
          wakapi-sdk = pkgs.python3Packages.callPackage ./default.nix {};
        };
      }
    );
}
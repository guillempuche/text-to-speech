{
  description = "Xiroi Voice Cloning environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        lint = pkgs.writeShellScriptBin "lint" ''
          echo "Checking formatting..."
          echo ""
          echo "-> Markdown, JSON, TOML (dprint)"
          ${pkgs.dprint}/bin/dprint check
          echo ""
          echo "-> Python (ruff)"
          ${pkgs.ruff}/bin/ruff check .
          ${pkgs.ruff}/bin/ruff format --check .
        '';
        format = pkgs.writeShellScriptBin "format" ''
          echo "Formatting files..."
          echo ""
          echo "-> Markdown, JSON, TOML (dprint)"
          ${pkgs.dprint}/bin/dprint fmt
          echo ""
          echo "-> Python (ruff)"
          ${pkgs.ruff}/bin/ruff check --fix .
          ${pkgs.ruff}/bin/ruff format .
        '';
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            lint
            format
            pkgs.python3
            pkgs.dprint
            pkgs.ruff
            pkgs.lefthook
          ];

          shellHook = ''
            lefthook install
            echo ""
            echo "Xiroi Voice Cloning Environment"
            echo "  python: $(python3 --version)"
            echo "  dprint: $(dprint --version)"
            echo "  ruff: $(ruff --version)"
            echo "  lefthook: $(lefthook version)"
            echo ""
            echo "Commands:"
            echo "  lint      - Check formatting (no changes)"
            echo "  format    - Format all files (auto-fix)"
          '';
        };
      });
}

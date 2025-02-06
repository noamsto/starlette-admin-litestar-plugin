{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    systems.url = "github:nix-systems/default";
    devenv.url = "github:cachix/devenv";
    nixpkgs-python = {
      url = "github:cachix/nixpkgs-python";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

  outputs = {
    self,
    nixpkgs,
    devenv,
    systems,
    ...
  } @ inputs: let
    forEachSystem = nixpkgs.lib.genAttrs (import systems);
  in {
    packages = forEachSystem (system: {
      devenv-up = self.devShells.${system}.default.config.procfileScript;
      devenv-test = self.devShells.${system}.default.config.test;
    });

    devShells =
      forEachSystem
      (system: let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        py310 = devenv.lib.mkShell {
          inherit inputs pkgs;
          modules = [
            ({config, ...}: {
              # This is your devenv configuration
              packages = with pkgs; [just pre-commit python3Packages.pre-commit-hooks];
              languages.python = {
                version = "3.10";
                enable = true;
                uv = {
                  enable = true;
                  sync.enable = true;
                };
              };

              env = {
                LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [pkgs.stdenv.cc.cc pkgs.zlib]; # NOTE: see https://github.com/cachix/devenv/issues/1264
                UV_PYTHON_PREFERENCE = "only-system";
                UV_LINK_MODE = "copy";
                UV_PYTHON = "${config.languages.python.package}";
              };
              enterShell = ''
                echo path to dll $NIX_LD
                export VIRTUAL_ENV=$UV_PROJECT_ENVIRONMENT
                source $VIRTUAL_ENV/bin/activate
              '';
            })
          ];
        };
      });
  };
}

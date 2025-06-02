{
  inputs = {
    devenv-root = {
      url = "file+file:///dev/null";
      flake = false;
    };
    flake-parts.url = "github:hercules-ci/flake-parts";
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    devenv.url = "github:cachix/devenv";
    nix2container.url = "github:nlewo/nix2container";
    nix2container.inputs.nixpkgs.follows = "nixpkgs";
    mk-shell-bin.url = "github:rrbutani/nix-mk-shell-bin";
    nixpkgs-python = {
      url = "github:cachix/nixpkgs-python";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

  outputs = inputs @ {
    flake-parts,
    devenv-root,
    ...
  }:
    flake-parts.lib.mkFlake {
      inherit inputs;
    } {
      systems = ["x86_64-linux" "i686-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin"];
      imports = [
        inputs.devenv.flakeModule
      ];
      perSystem = {
        config,
        self',
        inputs',
        pkgs,
        system,
        ...
      }: {
        devenv.shells.default = {
          packages = with pkgs; [just pre-commit python3Packages.pre-commit-hooks];
          languages.python = {
            version = "3.10";
            enable = true;
            venv.enable = true;
            uv = {
              enable = true;
              sync = {
                enable = true;
                allExtras = true;
              };
            };
          };

          env = {
            LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [pkgs.stdenv.cc.cc pkgs.zlib]; # NOTE: see https://github.com/cachix/devenv/issues/1264
            UV_LINK_MODE = "copy";
            UV_PYTHON = "${config.devenv.shells.default.languages.python.package}";
          };

          enterShell = ''
            echo -e "\033[1;36m✨ \033[1;33mFactify DAL\033[1;36m ✨\033[0m"
            echo -e "\033[0;32m→ Python \033[1;32m$(python --version | cut -d' ' -f2)\033[0m"
            echo -e "\033[0;32m→ Run \033[1;32mjust\033[0m \033[0;32mfor available commands\033[0m"
          '';
        };
      };
    };
}

# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }:
{
  # Which nixpkgs channel to use.
  channel = "unstable";

  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.python311
  ];

  # Sets environment variables in the workspace
  env = {};

  idx = {
    extensions = [
      "google.gemini-cli-vscode-ide-companion"
      "ms-python.python"
    ];

    workspace = {
      # Runs when a workspace is created
      onCreate = {
        default.openFiles = [ "README.md" ];
      };
      # Runs when a workspace is started
      onStart = {
      };
    };

    # Enable previews and customize configuration
    previews = {
      enable = true;
    };
  };
}

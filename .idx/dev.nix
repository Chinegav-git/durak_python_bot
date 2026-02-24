# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }:
{
  # Which nixpkgs channel to use.
  channel = "unstable";

  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.postgresql
    pkgs.pkg-config

    # Декларативно определяем окружение Python со всеми зависимостями.
    (pkgs.python311.withPackages (ps:
      let
        tortoise-orm = ps.buildPythonPackage rec {
          pname = "tortoise-orm";
          version = "0.21.3";
          src = ps.fetchPypi {
            inherit pname version;
            # ЭТО ЗАГЛУШКА. Следующая сборка выдаст правильный хеш.
            # THIS IS A PLACEHOLDER. The next build will output the correct hash.
            sha256 = "0000000000000000000000000000000000000000000000000000";
          };
          pyproject = true;
          build-system = [ ps.setuptools ];
          propagatedBuildInputs = [ ps.asyncpg ps.pypika ps.aiofiles ];
          doCheck = false;
        };

        aerich = ps.buildPythonPackage rec {
          pname = "aerich";
          version = "0.7.2";
          src = ps.fetchPypi {
            inherit pname version;
            sha256 = "sha256-MdZ957lhhGNrid6ZBi4Fnl5iBLYlHSTDPrIfyc+YLgk=";
          };
          pyproject = true;
          build-system = [ ps.setuptools ];
          propagatedBuildInputs = [ tortoise-orm ps.click ps.toml ];
          doCheck = false;
        };

        environs = ps.buildPythonPackage rec {
          pname = "environs";
          version = "11.0.0";
          src = ps.fetchPypi {
            inherit pname version;
            # ИСПРАВЛЕНО: Обновлен хеш для environs согласно логу ошибки.
            # FIXED: Updated the hash for environs according to the error log.
            sha256 = "sha256-BpcnqPc9i6jQM9PNlcDaIx1E848dp3O/B2zvFo0xLug=";
          };
          pyproject = true;
          build-system = [ ps.setuptools ];
          propagatedBuildInputs = [ ps.python-dotenv ];
          doCheck = false;
        };

      in [
        # Core bot framework
        ps.aiogram
        ps.magic-filter

        # Database
        tortoise-orm
        aerich
        ps.asyncpg

        # State management
        ps.redis

        # Configuration
        environs
      ]))
  ];

  # Sets environment variables in the workspace
  env = {};

  idx = {
    extensions = [
      "google.gemini-cli-vscode-ide-companion"
      "ms-python.python"
    ];

    previews = {
      enable = true;
    };

    workspace = {
      onCreate = {
        default.openFiles = [ "README.md" "bot.py" "DEPLOY.md" ];
      };
      onStart = {};
    };
  };
}

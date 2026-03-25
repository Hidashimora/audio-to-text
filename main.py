from transcriber.config import load_config
from transcriber.ui import TranscriberApp


def main() -> None:
    config, settings = load_config()
    app = TranscriberApp(config, settings)
    app.run()


if __name__ == "__main__":
    main()

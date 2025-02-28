import argparse

from modules.add_background_music import add_background_music
from modules.concatenate_asset_with_image import concatenate_asset_with_image
from modules.concatenate_multiple_assets import concatenate_multiple_assets
from modules.concatenate_pieces import concatenate_pieces


def main():
    parser = argparse.ArgumentParser(description="Video Processing Script")
    parser.add_argument(
        "--opt",
        type=str,
        required=True,
        choices=["full", "pieces", "asset_image", "multiple_assets", "bg_music"],
        help="Operation to perform: full, pieces, asset_image, multiple_assets, bg_music",
    )
    parser.add_argument("--assets", type=str, help="Comma-separated list of asset IDs")
    parser.add_argument(
        "--article", type=int, help="Article ID for multiple assets concatenation"
    )
    parser.add_argument("--bg", type=int, help="Background music ID")

    args = parser.parse_args()

    if args.opt == "full":
        # Perform all operations
        concatenate_pieces(args.assets)
        concatenate_asset_with_image(args.assets)
        concatenate_multiple_assets(args.assets, args.article)
        add_background_music(args.article, args.bg)
    elif args.opt == "pieces":
        concatenate_pieces(args.assets)
    elif args.opt == "asset_image":
        concatenate_asset_with_image(args.assets)
    elif args.opt == "multiple_assets":
        concatenate_multiple_assets(args.assets, args.article)
    elif args.opt == "bg_music":
        add_background_music(args.article, args.bg)


if __name__ == "__main__":
    main()

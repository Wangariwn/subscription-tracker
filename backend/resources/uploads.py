from flask import current_app

try:
    import cloudinary
    import cloudinary.uploader as cloudinary_uploader
except ImportError:  # pragma: no cover
    cloudinary = None
    cloudinary_uploader = None


def cloudinary_configured():
    cfg = current_app.config
    return bool(
        cloudinary
        and cfg.get("CLOUDINARY_CLOUD_NAME")
        and cfg.get("CLOUDINARY_API_KEY")
        and cfg.get("CLOUDINARY_API_SECRET")
    )


def configure_cloudinary():
    cloudinary.config(
        cloud_name=current_app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=current_app.config["CLOUDINARY_API_KEY"],
        api_secret=current_app.config["CLOUDINARY_API_SECRET"],
        secure=True,
    )


def upload_avatar(file_storage, public_id=None):
    """Upload an image file to Cloudinary and return the secure URL."""
    if cloudinary is None or cloudinary_uploader is None:
        raise RuntimeError(
            "cloudinary package is not installed. pip install cloudinary"
        )
    if not cloudinary_configured():
        raise RuntimeError(
            "Cloudinary is not configured. Set CLOUDINARY_CLOUD_NAME, "
            "CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET."
        )

    configure_cloudinary()
    result = cloudinary_uploader.upload(
        file_storage,
        folder="subscription-tracker/avatars",
        public_id=public_id,
        overwrite=True,
        resource_type="image",
        transformation=[{"width": 400, "height": 400, "crop": "fill"}],
    )
    return result["secure_url"]

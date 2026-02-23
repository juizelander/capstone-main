# Media Handling Instructions

## Overview
The application stores program and application images using Django's `ImageField`. Images are saved under the `media/` directory (e.g., `media/program_images/`).

## Development
- `DEBUG = True` – Django automatically serves files from `MEDIA_URL` (`/media/`).
- Run the server as usual: `python manage.py runserver`.
- Uploaded images can be accessed directly via URLs like `/media/program_images/<filename>.jpg`.

## Production (Render)
1. **Environment Variable**
   - If you want to use Cloudinary, set `CLOUDINARY_URL` in Render's environment variables. The app will then store images on Cloudinary and serve them via the CDN.
   - If `CLOUDINARY_URL` is **not** set, the app falls back to local storage.
2. **Serving Media Files**
   - The project now includes an unconditional media URL pattern in `capstone/urls.py`:
     ```python
     from django.conf import settings
     from django.conf.urls.static import static

     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
     ```
   - This ensures that `/media/` URLs are served correctly on Render as well.
3. **Deploy Steps**
   - Push your changes to the repository.
   - Render will rebuild the container and the new URL pattern will take effect.
   - Verify that image URLs (e.g., `/media/program_images/edukalinga.jpg`) return **200 OK**.

## Testing
A Django test (`home/tests/test_media.py`) verifies that the API endpoint `/home/programs/` returns a valid `program_image` URL that ends with the uploaded filename and starts with `/media/` or `http`.

## Troubleshooting
- **404 on image URLs**: Ensure the `media/` folder is present on the server and contains the uploaded files. Verify that the `MEDIA_ROOT` path is correct.
- **Cloudinary not working**: Double‑check the `CLOUDINARY_URL` value and that the `cloudinary_storage` app is installed.
- **Static files not loading**: `whitenoise` handles static files; media files are handled by the pattern above.

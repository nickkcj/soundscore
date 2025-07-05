import os
import uuid
from supabase import create_client, Client
from django.conf import settings
from PIL import Image
import io

class SupabaseStorageService:
    def __init__(self):
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket_name = settings.SUPABASE_BUCKET_NAME

    def upload_profile_picture(self, file, user_id):
        """
        Upload a profile picture to Supabase storage.
        Returns the public URL of the uploaded image.
        """
        try:
            # Generate unique filename
            file_extension = file.name.split('.')[-1].lower()
            unique_filename = f"{user_id}_{uuid.uuid4().hex}.{file_extension}"
            file_path = f"users/{unique_filename}"

            # Resize and optimize image
            optimized_file = self._optimize_image(file)

            # Upload to Supabase
            response = self.supabase.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=optimized_file,
                file_options={"content-type": f"image/{file_extension}"}
            )

            if response:
                # Get public URL
                public_url = self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)
                return {
                    "success": True,
                    "url": public_url,
                    "path": file_path
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to upload to Supabase"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_default_profile_picture_url(self):
        """
        Get the URL for the default profile picture.
        Upload default image if it doesn't exist.
        """
        default_path = "defaults/default-profile.jpg"
        
        try:
            # Check if default image exists
            public_url = self.supabase.storage.from_(self.bucket_name).get_public_url(default_path)
            return public_url
        except:
            # Upload default image if it doesn't exist
            return self._upload_default_image()

    
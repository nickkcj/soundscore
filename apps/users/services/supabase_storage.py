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

    def delete_profile_picture(self, file_path_or_url):
        """
        Delete a profile picture from Supabase storage.
        """
        try:
            # Don't delete the default image
            if "2301-default-2.png" in file_path_or_url:
                return {"success": True}
            
            # Extract path from URL if needed
            if file_path_or_url.startswith('http'):
                file_path = self._extract_path_from_url(file_path_or_url)
            else:
                file_path = file_path_or_url
            
            response = self.supabase.storage.from_(self.bucket_name).remove([file_path])
            return {"success": True}
        except Exception as e:
            print(f"Error deleting file: {e}")
            return {"success": False, "error": str(e)}

    def _optimize_image(self, file):
        """
        Resize and optimize image before upload.
        """
        try:
            # Open image
            image = Image.open(file)
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Resize to max 400x400 while maintaining aspect ratio
            image.thumbnail((400, 400), Image.Resampling.LANCZOS)
            
            # Save to BytesIO
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            return output.getvalue()
            
        except Exception as e:
            # If optimization fails, return original file
            file.seek(0)
            return file.read()

    def _extract_path_from_url(self, url):
        """
        Extract file path from Supabase public URL.
        """
        try:
            # Example URL: https://xxx.supabase.co/storage/v1/object/public/profilepictures/users/filename.jpg
            parts = url.split(f'/{self.bucket_name}/')
            if len(parts) > 1:
                return parts[1]
            return url
        except:
            return url


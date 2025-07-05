import uuid
from supabase import create_client
from django.conf import settings

class SupabaseCoverStorage:
    def __init__(self):
        self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket = settings.SUPABASE_COVER_BUCKET

    def upload_cover(self, file, group_id):
        ext = file.name.split('.')[-1].lower()
        filename = f"{group_id}_{uuid.uuid4().hex}.{ext}"
        path = f"covers/{filename}"
        file.seek(0)
        res = self.supabase.storage.from_(self.bucket).upload(path, file.read(), {"content-type": f"image/{ext}"})
        if res:
            url = self.supabase.storage.from_(self.bucket).get_public_url(path)
            return url
        return None
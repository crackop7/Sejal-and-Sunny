"""
=====================================================================
WedSnap - Bulk Photo Import CLI Script
Import wedding photos directly from any local folder into WedSnap!
=====================================================================

Usage:
  python import_photos.py "C:\\path\\to\\photos"
  python import_photos.py "C:\\path\\to\\photos" --event haldi
  python import_photos.py "C:\\path\\to\\photos" --event mehendi
  python import_photos.py "C:\\path\\to\\photos" --event wedding
  python import_photos.py "C:\\path\\to\\photos" --event reception
"""

import sys
import os
import argparse
import uuid
import json
import shutil
from pathlib import Path
from PIL import Image

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.config import settings
from backend.database import get_sync_db, init_db
from backend.face_engine import get_face_engine

def import_photos_from_folder(folder_path: str, event_slug: str = None, gallery_id: str = "sejal-aarav-2026"):
    src_dir = Path(folder_path)
    if not src_dir.exists() or not src_dir.is_dir():
        print(f"Error: Folder '{folder_path}' does not exist or is not a directory.")
        return

    init_db()
    conn = get_sync_db()
    cursor = conn.cursor()

    # Find event ID if specified
    event_id = None
    if event_slug:
        cursor.execute("SELECT id, name FROM events WHERE gallery_id = ? AND slug LIKE ?", (gallery_id, f"%{event_slug}%"))
        row = cursor.fetchone()
        if row:
            event_id = row["id"]
            print(f"Assigning photos to event: {row['name']} ({event_id})")
        else:
            print(f"Warning: No event matching '{event_slug}' found. Photos will be unassigned.")

    # Target folders
    orig_dir = settings.ORIGINALS_DIR / gallery_id
    thumb_dir = settings.THUMBNAILS_DIR / gallery_id
    orig_dir.mkdir(parents=True, exist_ok=True)
    thumb_dir.mkdir(parents=True, exist_ok=True)

    # Scan image files
    valid_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    image_files = [f for f in src_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_extensions]

    if not image_files:
        print(f"No image files found in '{folder_path}' (supported: .jpg, .jpeg, .png, .webp).")
        return

    print(f"\nFound {len(image_files)} photos in '{folder_path}'. Initializing AI face recognition engine...")
    face_engine = get_face_engine()

    imported_count = 0
    total_faces_count = 0

    for idx, img_file in enumerate(image_files, 1):
        photo_id = str(uuid.uuid4())
        ext = img_file.suffix.lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            ext = ".jpg"

        dest_orig = orig_dir / f"{photo_id}{ext}"
        dest_thumb = thumb_dir / f"{photo_id}.jpg"

        # Copy original
        shutil.copy2(img_file, dest_orig)

        # Create thumbnail
        try:
            with Image.open(dest_orig) as im:
                im = im.convert("RGB")
                w, h = im.size
                im.thumbnail((640, 640), Image.Resampling.LANCZOS)
                im.save(dest_thumb, "JPEG", quality=85, optimize=True)
        except Exception as e:
            print(f"[{idx}/{len(image_files)}] Failed to process thumbnail for {img_file.name}: {e}")
            continue

        file_size = dest_orig.stat().st_size
        orig_url = f"/uploads/originals/{gallery_id}/{photo_id}{ext}"
        thumb_url = f"/uploads/thumbnails/{gallery_id}/{photo_id}.jpg"

        # Run AI Face Detection and Embedding Extraction
        with open(dest_orig, "rb") as f:
            img_bytes = f.read()

        try:
            img_w, img_h, detected_faces = face_engine.process_image_bytes(img_bytes)
        except Exception as e:
            print(f"[{idx}/{len(image_files)}] AI face extraction warning for {img_file.name}: {e}")
            detected_faces = []
            img_w, img_h = w, h

        # Insert photo record
        cursor.execute("""
            INSERT INTO photos (
                id, gallery_id, event_id, filename, original_url, thumbnail_url,
                width, height, file_size, faces_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            photo_id, gallery_id, event_id, img_file.name,
            orig_url, thumb_url, img_w, img_h, file_size, len(detected_faces)
        ))

        # Insert face embeddings
        for face in detected_faces:
            emb_id = str(uuid.uuid4())
            bbox = face["bbox"]
            emb_bytes = face["embedding"].tobytes()
            cursor.execute("""
                INSERT INTO face_embeddings (
                    id, photo_id, gallery_id, bbox_x, bbox_y, bbox_w, bbox_h,
                    landmarks_json, confidence, embedding
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                emb_id, photo_id, gallery_id,
                bbox["x"], bbox["y"], bbox["w"], bbox["h"],
                json.dumps(face.get("landmarks", [])),
                face["confidence"],
                emb_bytes
            ))

        imported_count += 1
        total_faces_count += len(detected_faces)
        print(f"[{idx}/{len(image_files)}] Imported: {img_file.name} -> {len(detected_faces)} face(s) indexed.")

    conn.commit()
    conn.close()

    print(f"\n==================================================")
    print(f"Import Complete!")
    print(f"  • Successfully imported: {imported_count} photos")
    print(f"  • Total faces indexed: {total_faces_count} faces")
    print(f"  • Open http://localhost:8000 to view your gallery!")
    print(f"==================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bulk import wedding photos into WedSnap")
    parser.add_argument("folder", help="Path to folder containing photos")
    parser.add_argument("--event", help="Event category (haldi, mehendi, wedding, reception)", default=None)
    parser.add_argument("--gallery", help="Target gallery ID", default="sejal-aarav-2026")
    args = parser.parse_args()

    import_photos_from_folder(args.folder, event_slug=args.event, gallery_id=args.gallery)

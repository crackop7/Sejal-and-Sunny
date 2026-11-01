# WedSnap 💍 — AI-Powered Wedding Photo Sharing Website

**WedSnap** is a production-ready wedding photo-sharing platform designed for **Sejal & Sunny's Wedding**. Wedding guests can scan a table QR code with their mobile phone, take a quick selfie (or upload a photo), and instantly discover every wedding photograph they appear in using **deep neural network facial recognition**.

---

## 🌟 Key Features

### 1. 🎨 Luxury Wedding Design
- **Color Palette:** Warm Ivory (`#FAF8F5`), Champagne Gold (`#C5A059`, `#D4AF37`), Soft Beige (`#F4EFEA`), and Deep Charcoal (`#242220`).
- **Typography:** Elegant serif typography (*Cormorant Garamond*) paired with modern sans-serif (*Plus Jakarta Sans*).
- **Mobile-First Experience:** Tailored for guests scanning QR codes at wedding reception tables from iPhones and Android devices.

### 2. 🧠 Real AI Face Recognition (No Mockups or Fakes)
- **Face Detector:** OpenCV **YuNet** deep learning ONNX detector (fast multi-face localization with bounding boxes and 5 facial landmarks).
- **Face Recognizer:** **SFace** (SphereFace/CosFace deep neural network) extracting 128-dimensional L2-normalized facial embeddings.
- **Vector Similarity Search:** Real-time cosine similarity search across all ceremony photographs with adjustable sensitivity threshold.
- **Crowd Multi-Face Support:** Detects and indexes every guest in group photos (Haldi, Mehendi, Mandap crowd, Reception dance floor).

### 3. 📸 Wedding Album Organization
- Organized by events:
  - 💛 **Haldi Ceremony**
  - 🌿 **Mehendi Ceremony**
  - 💍 **Wedding Ceremony**
  - 🥂 **Grand Reception**
- Responsive masonry grid with lazy loading.
- Fullscreen Lightbox viewer with zoom, event badges, face count indicators, and download links.

### 4. 📦 Download & Sharing
- Download individual original full-resolution photos.
- **Batch ZIP Download:** Select specific photos or download all matched photos in one click.
- Web Share API and one-tap clipboard share links.

### 5. 📱 QR Code & Printable Table Cards
- **Mobile Direct Access:** Unique QR code opening the wedding gallery on any smartphone camera.
- **Print-Ready Table Tent Card:** Auto-generates high-resolution 800×1150 gold-ornamented signage cards ready to print for guest tables and entrance signage.

### 6. 🔒 Photographer / Admin Portal
- Protected with bcrypt password hashing and JWT token authentication.
- **Bulk Photo Uploader:** Drag and drop 50+ photos at once with real-time upload progress and background facial embedding extraction.
- **Photo Manager:** View all indexed photos, face counts, and delete options.
- **Gallery Settings:** Update couple names, wedding date, venue, location, and welcome message.

---

## 🚀 How to Add Photos

You have **two easy ways** to add wedding photos:

### Method 1: Directly via the Web Browser (Photographer Portal)
1. Open [http://localhost:8000](http://localhost:8000).
2. Click **"Upload Photos"** (or the lock icon 🔒) in the top navigation bar.
3. Sign in with the administrator credentials:
   - **Username:** `admin`
   - **Password:** `admin12345`
4. Select the target event album (e.g. *Haldi*, *Mehendi*, *Wedding Ceremony*, or *Grand Reception*).
5. Drag and drop your photos into the upload zone (or click to browse multiple files from your computer).
6. Click **"Upload & Run AI Face Indexing"**.
7. The system will automatically generate fast thumbnails, run deep neural facial detection on every photo, extract embeddings, and immediately make them searchable!

### Method 2: Bulk Import via Command Line (`import_photos.py`)
If you have a folder containing dozens or hundreds of wedding photos on your computer, import them in one command:

```powershell
# Import all photos in a folder to the wedding gallery
python import_photos.py "C:\path\to\your\wedding\photos"

# Import specifically to an event album:
python import_photos.py "C:\path\to\haldi_photos" --event haldi
python import_photos.py "C:\path\to\mehendi_photos" --event mehendi
python import_photos.py "C:\path\to\ceremony_photos" --event wedding
python import_photos.py "C:\path\to\reception_photos" --event reception
```

---

## 🛠️ Technology Stack

- **Backend:** Python 3.10+ / 3.14 with **FastAPI** & **Uvicorn**
- **AI Face Pipeline:** OpenCV **YuNet** (detection) + **SFace** (recognition) ONNX models
- **Database:** SQLite (local zero-config) + full **Supabase PostgreSQL (`pgvector`)** support
- **Image Processing:** OpenCV, Pillow, QRCode[pil]
- **Frontend:** Vanilla HTML5, CSS3, JavaScript (no complex build step; fast and lightweight)
- **Security:** PyJWT, BCrypt, CORS middleware

---

## 💻 Running Locally

### 1. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 2. Start the Server
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Open in Browser
Visit **[http://localhost:8000](http://localhost:8000)** on your computer or open it on your mobile phone connected to the same Wi-Fi using your local IP (e.g., `http://192.168.1.X:8000`).

---

## ⚡ Instant 1-Click AI Test

On the landing page, you can test the real face recognition engine without taking a selfie by clicking any of the **Quick Test** buttons:
- **Test Bride (Sejal):** Instantly matches Mehendi, Haldi, and Wedding Ceremony photos.
- **Test Groom (Sunny):** Matches groom portrait, wedding mandap, and reception dancing photos while correctly ignoring all-women ceremonies.
- **Test Bridesmaid (Priya):** Matches Mehendi celebration swing photo.
- **Take Live Selfie:** Click **"Find My Photos"** to use your real laptop or phone camera!

---

## ☁️ Supabase Cloud Deployment (Optional)

WedSnap is fully turnkey on SQLite by default. To deploy with Supabase PostgreSQL and Supabase Private Storage:

1. Create a Supabase project at [supabase.com](https://supabase.com).
2. Go to the **SQL Editor** in your Supabase dashboard and run the migration script:
   ```sql
   -- File: supabase/schema.sql
   ```
   This automatically enables the `pgvector` extension, creates all tables with foreign keys and cascade rules, and builds the HNSW cosine index `match_wedding_faces`.
3. In Supabase **Storage**, create a bucket named `wedding-photos`.
4. Configure your `.env` file:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-supabase-key
   SUPABASE_DB_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
   ```

---

## 🛡️ Privacy & Biometric Protection

- **No Permanent Biometric Retention:** Guest selfies submitted via "Find My Photos" are processed in-memory and discarded immediately after similarity calculation.
- **Guest Consent:** Explicit consent is validated prior to facial analysis.
- **Private Galleries:** Passcode protection option for private family galleries.
- **No Third-Party Sharing:** All face embeddings are processed on-premise/in-app without sending data to external APIs.

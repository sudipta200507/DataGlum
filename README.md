# DataGlum 🧹

**Automatically clean messy CSV datasets for ML training — in seconds.**

DataGlum is a free web tool that detects and fixes all common data quality problems in CSV files so your machine learning models train on perfect data, every time.

No code. No setup. Just upload your CSV and download a clean one.

---

## 🌐 Live Demo

> Coming soon — deploying on Vercel

---

## 🎯 What Problem Does It Solve?

Raw CSV datasets are always messy. Before you can train any ML model, you need to fix:

- Null / missing values
- Empty rows
- Duplicate rows
- Wrong data types (numbers stored as text)
- Extreme outliers
- Messy column names
- ERROR values in cells

Doing this manually with pandas takes hours — every single time, for every new dataset.

**DataGlum automates the entire process in seconds.**

---

## ✅ What It Fixes Automatically

| Problem | How DataGlum Fixes It |
|---|---|
| Empty rows | Removes all rows where every cell is empty |
| Duplicate rows | Detects and removes exact duplicate rows |
| Missing values | Fills with median (numbers) or most common value (text) |
| Columns mostly empty | Drops columns where more than 60% of values are missing |
| Wrong data types | Converts text numbers to actual numbers, detects dates |
| Extreme outliers | Caps outliers using the IQR method |
| Messy column names | Converts `Full Name` → `full_name` |
| Whitespace in cells | Strips all leading and trailing spaces |

---

## 🚀 How It Works

1. **Upload** — drag and drop your CSV file on the dashboard
2. **Clean** — DataGlum runs 8 automated cleaning passes on the cloud
3. **Download** — get your perfectly clean CSV, ready for ML training

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript (single file) |
| Backend / API | Python, pandas, FastAPI |
| Cloud Deployment | Modal.com |
| Hosting | Vercel |
| Authentication | Supabase (Google + GitHub login) |

---

## 📁 Project Structure

```
dataglum/
├── dataglum.html        # Complete frontend — all 3 pages (Landing, Auth, Dashboard)
├── csv_cleaner_api.py   # Python backend — CSV cleaning engine + Modal API
└── README.md            # You are here
```

---

## ⚙️ How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/dataglum.git
cd dataglum
```

### 2. Install Python dependencies

```bash
pip install modal pandas numpy
```

### 3. Set up Modal account

```bash
python -m modal token new
```

This opens your browser — log in to modal.com and click Approve.

### 4. Deploy the backend API

```bash
python -m modal deploy csv_cleaner_api.py
```

Modal will print your live API URL:
```
✓ Created web function clean_csv => https://YOUR-USERNAME--clean-csv.modal.run
```

### 5. Connect the frontend to your API

Open `dataglum.html` and find this line:

```javascript
const MODAL_API_URL = 'YOUR_MODAL_API_URL_HERE';
```

Replace `YOUR_MODAL_API_URL_HERE` with your Modal URL from Step 4.

### 6. Open the website

Double-click `dataglum.html` in your file explorer — it opens in your browser and is fully functional.

---

## 📊 Real World Test

Tested on a real 10,000 row cafe sales dataset:

| Metric | Before | After |
|---|---|---|
| Total rows | 10,000 | 10,000 |
| Null values | 6,826 | 0 ✅ |
| ERROR values | 1,622 | 0 ✅ |
| Total problems | **8,448** | **0** ✅ |
| Numeric columns | stored as text | proper float64 ✅ |
| Column names | `Transaction ID` | `transaction_id` ✅ |

---

## 💰 Cost

**Completely free.**

| Service | Free Tier |
|---|---|
| Modal.com | $30 free compute per month |
| Vercel | Free forever (hobby plan) |
| Supabase | Free up to 50,000 users |

Running this tool costs approximately **$0.001 per CSV file cleaned.**
You can clean thousands of files per month without paying anything.

---

## 🗺️ Roadmap

- [x] CSV cleaning engine (8 automated fixes)
- [x] Web dashboard with drag and drop upload
- [x] Cloud API on Modal.com
- [ ] Google + GitHub login via Supabase
- [ ] User history — save past cleaned files
- [ ] Deploy live on Vercel with custom domain
- [ ] Support for Excel (.xlsx) files
- [ ] Column-by-column cleaning report with charts

---

## 🤝 Contributing

Contributions are welcome! If you find a bug or want to suggest a new cleaning feature, feel free to open an issue or submit a pull request.

---

## 👨‍💻 Built By

**Sudipta** — built with Python, pandas, and a lot of coffee ☕

If this saved you time, give it a ⭐ on GitHub — it means a lot!

---

## 📄 License

MIT License — free to use, modify, and distribute.

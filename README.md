# Nepal Adel Ali - Portfolio App

An interactive portfolio built with Streamlit. It shows my data projects with their real cleaned data, so visitors can filter and explore the results instead of only reading about them.

---

## Pages

| Page | What it shows |
|---|---|
| Home | Profile with photo, key numbers, featured projects, skills, education and certificates |
| Smartphone Price Tracker | 1,829 cleaned Jumia Egypt phones with filters for brand, storage, price and renewed phones, charts and a product table |
| Beauty Products Pipeline | Rows before and after cleaning, top brands, average price by product type, common tags and a product table, read from the pipeline's SQLite database |
| Python Games | Screenshots (loaded from each game repository) and links for my four Turtle graphics games |
| Contact | My freelance and social profiles |

---

## Tech Stack

* **App:** Streamlit
* **Data:** Pandas, SQLite
* **Charts:** Plotly

---

## Data

* `data/jumia_clean_2026-10-24.csv`: output of the cleaning notebook in [egypt-smartphone-price-tracker](https://github.com/nepal-aly/egypt-smartphone-price-tracker)
* `data/beauty_products.db`: output of [beauty-products-pipeline](https://github.com/nepal-aly/beauty-products-pipeline)
* `data/nepal_photo.webp`: profile photo

---

## Installation

1. **Clone the repository:**
   `git clone https://github.com/nepal-aly/nepal-portfolio-app.git`

2. **Install the requirements:**
   `pip install -r requirements.txt`

3. **Run the app:**
   `streamlit run app.py`

# 🥗 Healthy Meal Recommender



### 🚀 Project Overview

This project aims to **promote healthy eating habits** by recommending nutritious recipes tailored to your preferences — based on ingredients, dietary needs, and nutrition data — using machine learning techniques.  

### 📁 Project Structure
```bash
healthy-meal-recommender/
├── crawl/ # Web scraping & data crawling scripts
├── demo/ # Demo web app & API backend
├── model/ # ML model training and inference code
├── pre_processing_and_eda/ # Data cleaning & exploratory data analysis
├── report/ # Project report files
├── slide/ # Presentation slides
├── .gitattributes # Git config
├── .gitignore # Git ignore rules
├── requirements.txt # Python dependencies
└── README.md # Project overview (this file)
```

### 📥 Data Collection

- **Sources**:  
  - Food.com (500k+ recipes, regularly updated)  
  - EatingWell (Award-winning nutrition site, millions of monthly visitors)  

- **Tool**: Selenium for precise and reliable scraping.

- **Dataset Summary**:  
  - Combined dataset contains **11,102 recipes**.  
  - Features: title, ingredients, cooking instructions, calories, fats, cholesterol, sodium, carbs, fiber, sugars, protein, and diet labels.

### 🧹 Data Preprocessing

- Clean, merge and standardize data from multiple sources.  
- Extract ingredient quantities and units with `ingredient_parser`.  
- Fill missing nutritional info where necessary.  
- Normalize nutritional data for modeling.  
- Evaluate data quality based on:  
  - ✅ Accuracy  
  - ✅ Completeness  
  - ✅ Consistency  
  - ✅ Timeliness  
  - ✅ Relevance  

### 🤖 Modeling

- Algorithm: **Nearest Neighbors** with brute-force search and **cosine similarity**.  
- Purpose: Find and recommend nutritionally similar and ingredient-relevant healthy recipes.  
- Pipeline:  
  - Load & clean data  
  - Scale nutritional features  
  - Vectorize text (ingredients, instructions) with TF-IDF  
  - Filter by nutritional thresholds  
  - Recommend top matching recipes  

### 🌐 Deployment & Demo

- Web app built with **Streamlit** for easy interaction.  
- Backend API powered by **FastAPI** for scalability.  
- **Ngrok** for exposing local server to public internet.
  
## 📸 Demo Preview
![Demo Screenshot](img/Screenshot%20%28237%29.png)
![Demo Screenshot](img/Screenshot%20%28238%29.png)


---

### 🛠 How to Run

1. Clone the repository.

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
   
3. Run the demo web app:
```
streamlit run demo/app.py
```

### 👥 Contributors
- Phạm Ngọc Trí (22521526)
- Lê Xuân Bình (22520131)

### Acknowledgments
- This project is part of the Preprocessing and Dataset Construction (DS108.O21) course at UIT.
- Thanks to the data sources: Food.com, EatingWell.
- Advisors: TS. Nguyễn Gia Tuấn Anh & Trần Quốc Khánh.

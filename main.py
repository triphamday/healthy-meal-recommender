from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import traceback

app = FastAPI()

# Load the dataset
dataset = pd.read_csv(r'D:\UIT\final_project_please\dataset.csv')

# Convert nutritional columns to numeric types
nutritional_columns = ['Calories', 'Total Fat (g)', 'Saturated Fat (g)', 'Cholesterol (mg)',
                       'Sodium (mg)', 'Total Carbohydrate (g)', 'Dietary Fiber (g)', 'Sugars (g)', 'Protein (g)']
dataset[nutritional_columns] = dataset[nutritional_columns].apply(pd.to_numeric, errors='coerce')

# Drop rows with missing or non-numeric values
dataset.dropna(subset=nutritional_columns, inplace=True)

columns = ['RecipeID', 'Title', 'Time (mins)', 'Calories',
           'Total Fat (g)', 'Saturated Fat (g)', 'Cholesterol (mg)',
           'Sodium (mg)', 'Total Carbohydrate (g)', 'Dietary Fiber (g)',
           'Sugars (g)', 'Protein (g)', 'Diet Label',
           'Ingredient', 'Ingredient_units', 'Direction']

dataset = dataset[columns]

# print(dataset.columns)


# Define maximum values for filtering
max_list = [2000, 78, 20, 300, 2300, 275, 28, 50, 50]

# Define functions
def scaling(dataframe):
    scaler = StandardScaler()
    prep_data = scaler.fit_transform(dataframe.iloc[:, 3:12])
    return prep_data, scaler

def tfidf_transform(ingredient_units):
    tfidf = TfidfVectorizer()
    ingredient_units_tfidf = tfidf.fit_transform(ingredient_units)
    return ingredient_units_tfidf, tfidf

def nn_predictor(prep_data):
    neigh = NearestNeighbors(metric='cosine', algorithm='brute')
    neigh.fit(prep_data)
    return neigh

def extract_data(dataframe, max_nutritional_values):
    extracted_data = dataframe.copy()
    for column, maximum in zip(extracted_data.columns[3:12], max_nutritional_values):
        extracted_data = extracted_data[extracted_data[column] < maximum]
    return extracted_data

def apply_pipeline(neigh, scaler, _input, extracted_data):
    input_scaled = scaler.transform(_input)
    prep_data = scaler.transform(extracted_data.iloc[:, 3:12])
    indices = neigh.kneighbors(input_scaled, n_neighbors=5)[1].flatten()
    recommendations = extracted_data.iloc[indices]
    recommendations_scaled = scaler.transform(recommendations.iloc[:, 3:12])
    similarities = cosine_similarity(input_scaled, recommendations_scaled)
    return recommendations, similarities

class InputData(BaseModel):
    calories: float
    total_fat: float
    saturated_fat: float
    cholesterol: float
    sodium: float
    carbohydrate: float
    fiber: float
    sugars: float
    protein: float
    ingredient_filter: str = None

@app.post("/predict/")
def predict(data: InputData):
    try:
        _input = np.array([[data.calories, data.total_fat, data.saturated_fat, data.cholesterol, data.sodium, data.carbohydrate, data.fiber, data.sugars, data.protein]])

        extracted_data = extract_data(dataset, max_list)
        prep_data, scaler = scaling(extracted_data)
        ingredient_units_tfidf, tfidf = tfidf_transform(extracted_data['Ingredient_units'])
        neigh = nn_predictor(prep_data)

        recommendations, similarities = apply_pipeline(neigh, scaler, _input, extracted_data)

        if data.ingredient_filter:
            filter_vector = tfidf.transform([' '.join([data.ingredient_filter])])
            recommendations_tfidf = tfidf.transform(recommendations['Ingredient_units'])
            text_similarities = cosine_similarity(recommendations_tfidf, filter_vector).flatten()
            recommendations = recommendations[text_similarities > 0.0]
            text_similarities = text_similarities[text_similarities > 0.0]
        else:
            text_similarities = None

        return {
            "recommended_recipes": recommendations.to_dict(orient='records'),
            "numeric_similarities": similarities.tolist(),
            "text_similarities": text_similarities.tolist() if text_similarities is not None else None
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

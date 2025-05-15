import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load the data
data = pd.read_csv('/content/drive/MyDrive/DS108/02.preprocess/dataset_final/dataset.csv')

# Drop duplicate rows
data = data.drop_duplicates()

# Insert 'Recipes ID' column
data.insert(0, 'Recipes ID', range(1, len(data) + 1))

# Select relevant columns
columns = ['Recipes ID', 'Time (mins)', 'Calories', 'Total Fat (g)', 'Saturated Fat (g)', 'Cholesterol (mg)',
           'Sodium (mg)', 'Total Carbohydrate (g)', 'Dietary Fiber (g)', 'Sugars (g)', 'Protein (g)',
           'Diet Label', 'Ingredient', 'Ingredient_units', 'Direction']
dataset = data[columns]

# Define maximum values for filtering 
max_Calories = 2000  # kcal
max_daily_fat = 78  # grams
max_daily_Saturatedfat = 20  # grams
max_daily_Cholesterol = 300  # mg
max_daily_Sodium = 2300  # mg
max_daily_Carbohydrate = 275  # grams
max_daily_Fiber = 28  # grams
max_daily_Sugar = 50  # grams (added sugars)
max_daily_Protein = 50  # grams

max_list = [max_Calories, max_daily_fat, max_daily_Saturatedfat, max_daily_Cholesterol, max_daily_Sodium, max_daily_Carbohydrate, max_daily_Fiber, max_daily_Sugar, max_daily_Protein]

# Define functions
def scaling(dataframe):
    scaler = StandardScaler()
    prep_data = scaler.fit_transform(dataframe.iloc[:, 3:11])
    return prep_data, scaler

def tfidf_transform(ingredient_units):
    tfidf = TfidfVectorizer()
    ingredient_units_tfidf = tfidf.fit_transform(ingredient_units)
    return ingredient_units_tfidf, tfidf

def nn_predictor(prep_data):
    neigh = NearestNeighbors(metric='cosine', algorithm='brute')
    neigh.fit(prep_data)
    return neigh

def build_pipeline(neigh, scaler, params):
    # Handle cases with fewer neighbors than requested
    n_neighbors = min(params['n_neighbors'], len(scaler.transform(dataset.iloc[:, 3:11])))
    transformer = FunctionTransformer(lambda X: neigh.kneighbors(X, n_neighbors=n_neighbors)[1],
                                      validate=False)
    pipeline = Pipeline([
        ('scaler', scaler),
        ('NN', transformer)
    ])
    return pipeline

def extract_data(dataframe, ingredient_filter, max_nutritional_values):
    extracted_data = dataframe.copy()
    for column, maximum in zip(extracted_data.columns[3:11], max_nutritional_values):
        extracted_data = extracted_data[extracted_data[column] < maximum]
    return extracted_data

def apply_pipeline(pipeline, _input, extracted_data, scaler):
    indices = pipeline.transform(_input)[0]
    indices = indices.flatten()
    recommendations = extracted_data.iloc[indices]
    
    input_scaled = scaler.transform(_input)
    recommendations_scaled = scaler.transform(recommendations.iloc[:, 3:11])
    similarities = cosine_similarity(input_scaled, recommendations_scaled)
    
    return recommendations, similarities

def recommand(dataframe, _input, max_nutritional_values, ingredient_filter=None, params={'n_neighbors': 5, 'return_distance': False}):
    extracted_data = extract_data(dataframe, ingredient_filter, max_nutritional_values)
    prep_data, scaler = scaling(extracted_data)
    ingredient_units_tfidf, tfidf = tfidf_transform(extracted_data['Ingredient_units'])
    neigh = nn_predictor(prep_data)
    pipeline = build_pipeline(neigh, scaler, params)
    
    _input_scaled = scaler.transform(_input)
    
    recommendations, similarities = apply_pipeline(pipeline, _input_scaled, extracted_data, scaler)
    
    if ingredient_filter is not None:
        filter_vector = tfidf.transform([' '.join(ingredient_filter)])
        recommendations_tfidf = tfidf.transform(recommendations['Ingredient_units'])
        text_similarities = cosine_similarity(recommendations_tfidf, filter_vector).flatten()
        
        # Ensure the length matches before filtering
        if len(recommendations) == len(text_similarities):
            recommendations = recommendations[text_similarities > 0.0]
            text_similarities = text_similarities[text_similarities > 0.0]
        else:
            print("Warning: Length mismatch between recommendations and text similarities")
            text_similarities = None
    else:
        text_similarities = None
    
    print("Recommended Recipes:")
    print(recommendations)
    print("\nCosine Similarities (Numeric Features):")
    print(similarities)
    if text_similarities is not None:
        print("\nCosine Similarities (Text Features):")
        print(text_similarities)
    
    return recommendations, similarities, text_similarities

# Run model
test_input = dataset.iloc[0:1, 3:11].to_numpy()
ingredient_filter = ['garlic']
recommand(dataset, test_input, max_list, ingredient_filter=ingredient_filter)
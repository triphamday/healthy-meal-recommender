import streamlit as st
import requests
import pandas as pd
import re
from streamlit_echarts import st_echarts
import streamlit.components.v1 as components

# Display class to handle the display of recommendations
class Display:
    def __init__(self):
        self.nutrition_values = ['Calories', 'Total Fat (g)', 'Saturated Fat (g)', 'Cholesterol (mg)', 'Sodium (mg)',
                                 'Total Carbohydrate (g)', 'Dietary Fiber (g)', 'Sugars (g)', 'Protein (g)']

    def display_recommendation(self, recommendations):
        st.subheader('Recommended Recipes:')
        if recommendations:
            rows = len(recommendations) // 2 + 1
            for column, row in zip(st.columns(2), range(2)):
                with column:
                    for idx in range(rows * row, min(rows * (row + 1), len(recommendations))):
                        recipe = recommendations[idx]
                        recipe_name = recipe['Title']
                        expander = st.expander(recipe_name)
                        nutritions_df = pd.DataFrame({value: [recipe[value]] for value in self.nutrition_values})
                        expander.markdown(
                            f'<h5 style="text-align: center;font-family:sans-serif;">Nutritional Values (g):</h5>',
                            unsafe_allow_html=True)
                        expander.dataframe(nutritions_df)
                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Ingredients:</h5>',
                                          unsafe_allow_html=True)
                        for ingredient in recipe['Ingredient'].split(';'):
                            expander.markdown(f"- {ingredient}")
                        expander.markdown(
                            f'<h5 style="text-align: center;font-family:sans-serif;">Recipe Instructions:</h5>',
                            unsafe_allow_html=True)
                        for instruction in recipe['Direction'].split(';'):
                            expander.markdown(f"- {instruction}")
                        expander.markdown(
                            f'<h5 style="text-align: center;font-family:sans-serif;">Cooking and Preparation Time:</h5>',
                            unsafe_allow_html=True)
                        expander.markdown(f"""
                            - Total Time      : {recipe['Time (mins)']} min
                        """)

                        if st.button(f"View Recipe", key=f"button_{recipe['RecipeID']}"):
                            st.session_state.page = 'Recipe Detail'
                            st.experimental_set_query_params(recipe_id=recipe['RecipeID'])
                            st.experimental_rerun()
        else:
            st.info("Couldn't find any recipes with the specified ingredients", icon="🙁")

    def display_overview(self, recommendations):
        if recommendations:
            st.subheader('Overview:')
            col1, col2, col3 = st.columns(3)
            with col2:
                selected_recipe_name = st.selectbox('Select a recipe', [r['Title'] for r in recommendations])
            st.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Nutritional Values:</h5>',
                        unsafe_allow_html=True)
            selected_recipe = next(r for r in recommendations if r['Title'] == selected_recipe_name)


            options = {
                "title": {"text": "Nutrition values", "subtext": f"{selected_recipe_name}", "left": "center"},
                "tooltip": {"trigger": "item"},
                "legend": {"orient": "vertical", "left": "left"},
                "series": [
                    {
                        "name": "Nutrition values",
                        "type": "pie",
                        "radius": "50%",
                        "data": [
                            {"value": selected_recipe[nutrition_value] / 1000 if nutrition_value in ['Cholesterol (mg)','Sodium (mg)'] else selected_recipe[nutrition_value],
                             "name": nutrition_value.replace('(mg)', '(g)')}
                            # Thay đổi tên hiển thị từ '(mg)' sang '(g)'
                            for nutrition_value in self.nutrition_values if nutrition_value not in ['Calories']
                        ],
                        "emphasis": {
                            "itemStyle": {
                                "shadowBlur": 10,
                                "shadowOffsetX": 0,
                                "shadowColor": "rgba(0, 0, 0, 0.5)"
                            }
                        }
                    }
                ]
            }
            st_echarts(options=options, height="600px")
            st.caption('You can select/deselect an item (nutrition value) from the legend.')


# Function to get user input
def user_input_features():
    st.sidebar.header('Your infomations')
    calories = st.sidebar.slider('Calories', min_value=0, max_value=2000, value=500)
    total_fat = st.sidebar.slider('Total Fat (g)', min_value=0, max_value=100, value=20)
    saturated_fat = st.sidebar.slider('Saturated Fat (g)', min_value=0, max_value=50, value=10)
    cholesterol = st.sidebar.slider('Cholesterol (mg)', min_value=0, max_value=300, value=2300)
    sodium = st.sidebar.slider('Sodium (mg)', min_value=0, max_value=2300, value=500)
    carbohydrate = st.sidebar.slider('Total Carbohydrate (g)', min_value=0, max_value=300, value=100)
    fiber = st.sidebar.slider('Dietary Fiber (g)', min_value=0, max_value=100, value=10)
    sugars = st.sidebar.slider('Sugars (g)', min_value=0, max_value=100, value=20)
    protein = st.sidebar.slider('Protein (g)', min_value=0, max_value=100, value=20)
    ingredient_filter = st.sidebar.text_input('Ingredient Filter (optional)')

    data = {
        'calories': calories,
        'total_fat': total_fat,
        'saturated_fat': saturated_fat,
        'cholesterol': cholesterol,
        'sodium': sodium,
        'carbohydrate': carbohydrate,
        'fiber': fiber,
        'sugars': sugars,
        'protein': protein,
        'ingredient_filter': ingredient_filter
    }
    return data


# Function to get recommendations
def get_recommendations(input_data):
    response = requests.post('http://127.0.0.1:8080/predict/', json=input_data)
    if response.status_code == 200:
        return response.json()['recommended_recipes']
    else:
        st.write("Error:", response.status_code, response.text)
        return None


# Main function to control page navigation
def main():
    if 'page' not in st.session_state:
        st.session_state.page = 'Introduction'

    if st.session_state.page == 'Introduction':
        show_introduction()
    elif st.session_state.page == 'Recommendation':
        show_recommendation()
    elif st.session_state.page == 'Recipe Detail':
        show_recipe_detail()


# Function to display introduction page
def show_introduction():
    background_color_style = """
            <style>
                body {
                    background: rgba(255,0,0,0.2) ; /* Set your desired background color code here */
                }
            </style>
        """
    st.markdown(background_color_style, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; margin-bottom: 70px;'>Welcome to my world</h1>",
                unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; margin-bottom: 70px;'><i>Food, in the end, in our own tradition, is something holy. It's not about nutrients and calories. It's about sharing. It's about honesty. It's about identity.</i></p>",
        unsafe_allow_html=True
    )
    # CSS style for the button
    button_style = """
           <style>
               .stButton>button {
                   background-color: #2a481d; /* Set your desired color code here */
                   color: #fff5ec;
                   border-radius: 5px;
                   padding: 10px 20px;
               }
           </style>
       """
    st.markdown(button_style, unsafe_allow_html=True)
    if st.columns(3)[1].button("Explore culinary dreams", use_container_width=True):
        st.session_state.page = 'Recommendation'
        st.experimental_rerun()

# Function to display recommendation page
def show_recommendation():
    display = Display()
    title = "<h1 style='text-align: center;'>Custom Food Recommendation</h1>"
    st.markdown(title, unsafe_allow_html=True)

    input_data = user_input_features()
    button_style = """
                   <style>
                       .stButton>button {
                           background-color: #2a481d; /* Set your desired color code here */
                           color: #fff5ec;
                           border-radius: 5px;
                           padding: 10px 20px;
                       }
                   </style>
               """
    st.markdown(button_style, unsafe_allow_html=True)
    if st.columns(3)[0].button('Predict'):
        recommendations = get_recommendations(input_data)
        if recommendations:
            st.session_state.recommendations = recommendations
            st.session_state.generated = True
            st.experimental_rerun()

    if st.session_state.get('generated', False):
        with st.container():
            display.display_recommendation(st.session_state.recommendations)
        with st.container():
            display.display_overview(st.session_state.recommendations)

    if st.button("Back to Introduction", use_container_width=True):
        st.session_state.page = 'Introduction'
        st.experimental_rerun()

def clean_direction(direction):
    unwanted_chars = "':., "
    cleaned_direction = ''.join(char for char in direction if char not in unwanted_chars)
    return cleaned_direction

# Function to display recipe detail page
def show_recipe_detail():
    query_params = st.experimental_get_query_params()
    recipe_id = query_params.get('recipe_id', [None])[0]

    if recipe_id and 'recommendations' in st.session_state:
        recommendations = st.session_state.recommendations
        recipe = next(r for r in recommendations if r['RecipeID'] == int(recipe_id))

        st.markdown(f"## {recipe['Title']}")
        st.markdown(f"**Time to prepare:** {recipe['Time (mins)']} min")

        st.markdown("### Ingredients")
        # Loại bỏ dấu '[' và ']' ra khỏi danh sách thành phần
        ingredient_list = recipe['Ingredient'].strip("[]")

        # Loại bỏ dấu "'" và khoảng trắng dư thừa từ mỗi thành phần trong danh sách
        ingredient_list = [ingredient.strip("' ") for ingredient in ingredient_list.split(',')]
        # Hiển thị danh sách thành phần đã được xử lý
        for ingredient in ingredient_list:
            st.markdown(f"- {ingredient.strip()}")
        # Loại bỏ khoảng trắng dư thừa từ các thành phần

        st.markdown("### Directions")
        # Loại bỏ các dấu thừa từ các hướng dẫn bằng cách sử dụng hàm clean_direction
        directions = recipe['Direction']
        # Sử dụng re.findall để tìm tất cả các mẫu văn bản giữa dấu chấm
        direction_list = re.findall(r'[^.]+', directions)
        # Gộp các hướng dẫn thành một đoạn văn bản duy nhất
        full_directions = ". ".join(direction.strip() for direction in direction_list)
        full_directions = re.sub(r'\[\'|\', \'|\']', '', full_directions)
        full_directions = re.sub(r':', '', full_directions)
        full_directions = re.sub(r',\s*,', ',', full_directions)  # Loại bỏ các dấu phẩy liên tiếp
        st.markdown(full_directions)
    else:
        st.error("No recipe selected!")

    if st.button("Back to Recommendations"):
        st.session_state.page = 'Recommendation'
        st.experimental_rerun()

if __name__ == "__main__":
    main()

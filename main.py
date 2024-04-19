import streamlit as st
from PIL import Image, ImageDraw

from streamlit_image_coordinates import streamlit_image_coordinates

st.set_page_config(
    page_title="BlotQuant",
    page_icon="🔬",
    layout="centered",
)

def get_ellipse_coords(point: tuple[int, int]) -> tuple[int, int, int, int]:
    center = point
    radius = 3
    return (
        center[0] - radius,
        center[1] - radius,
        center[0] + radius,
        center[1] + radius,
    )

if "pixels" not in st.session_state:
    st.session_state["pixels"] = {"lower": None, "upper": None, "value": None}
if "intensity" not in st.session_state:
    st.session_state["intensity"] = None
if "coords" not in st.session_state:
    st.session_state["coords"] = None

def calculate_intensity(lower: int, upper: int, value: int, conc: float) -> float:
    st.session_state["intensity"] = ((255-upper) / ((255-value) - (255-lower))) * conc                                   # idfk fix this

# Upload image
uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_image is not None:
    # Open the image
    image = Image.open(uploaded_image)

    # Display the image
    draw = ImageDraw.Draw(image)
    pixel_values = list(image.getdata())

    concentration = st.number_input("Concentration Value", value=None, placeholder="Enter concentration")
    selected_point_type = st.selectbox("Select Point Type", ["lower_bound", "upper_bound", "chosen_value"])

    # Draw an ellipse at each coordinate in points
    for key, value in st.session_state["pixels"].items():
        label = f'{key}: '
        if value is not None:
            coords = get_ellipse_coords(value)
            draw.ellipse(coords, fill="white", outline="black")
            # label += f"{value} = {pixel_values[value[0] + value[1] * image.width][0]}"
            label += f"{pixel_values[value[0] + value[1] * image.width][0]}"
        else:
            label += str(value)
        st.write(label)
    
    st.session_state["coords"] = streamlit_image_coordinates(image, key="pil")

    if st.session_state["pixels"]["lower"] is None or st.session_state["pixels"]["upper"] is None \
            or st.session_state["pixels"]["value"] is None or concentration is None:
        st.write("Please select all points and enter concentration")
    else:
        st.button('Calculate Intensity', type='primary', on_click=calculate_intensity, args=[
            pixel_values[st.session_state["pixels"]["lower"][0] + st.session_state["pixels"]["lower"][1] * image.width][0], 
            pixel_values[st.session_state["pixels"]["upper"][0] + st.session_state["pixels"]["upper"][1] * image.width][0],
            pixel_values[st.session_state["pixels"]["value"][0] + st.session_state["pixels"]["value"][1] * image.width][0],
            concentration
        ])
        st.write(f'Intensity: {str(st.session_state["intensity"])}')

    # Update the page to show the pixel and value
    if st.session_state["coords"] is not None:
        point = st.session_state["coords"]["x"], st.session_state["coords"]["y"]
        pixel_value = pixel_values[point[0] + point[1] * image.width][0]
        # st.write(f"Clicked at {point} = {pixel_value}")
        if selected_point_type == "lower_bound":
            st.session_state["pixels"]["lower"] = point
            st.session_state["coords"] = None
            # st.rerun()
        elif selected_point_type == "upper_bound":
            st.session_state["pixels"]["upper"] = point
            st.session_state["coords"] = None
            # st.rerun()
        elif selected_point_type == "chosen_value":
            st.session_state["pixels"]["value"] = point
            st.session_state["coords"] = None
            # st.rerun()
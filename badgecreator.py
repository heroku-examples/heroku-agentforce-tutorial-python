"""
Badge Creator Module

This module provides functionality for generating custom badges with a logo,
rotated text box, and text. It uses the Python Imaging Library (Pillow) to
create the badge and encodes it as a Base64 string for easy embedding in HTML
or other formats.

Functionality:
- Dynamically generates a badge with customizable text lines.
- Includes a logo at the top of the badge.
- Adds a rotated text box with a shadow effect and text inside.
- Outputs the badge as a Base64-encoded PNG string.

Dependencies:
- Pillow (PIL): For image creation and manipulation.
- base64: For encoding the badge image.
- io: For in-memory image handling.
- math: For geometric calculations.
- os: For file path operations.

Functions:
    create_badge(line1: str, line2: str) -> str:
        Creates a badge with the specified text lines and returns it as a
        Base64-encoded PNG string.

Example Usage:
    from badgecreator import create_badge

    # Generate a badge with custom text
    badge_base64 = create_badge("Heroku Agent Action", "Deployed by Neo")

    # Embed the badge in an HTML fragment
    html_fragment = f'<img src="data:image/png;base64,{badge_base64}">'

Directory Structure:
    The module expects the following directory and file setup:
    - A `resources` directory containing a logo image (`heroku_logo.png`).
    - A font file (`arial.ttf`) for rendering text.

Error Handling:
- Raises `FileNotFoundError` if the logo file is not found in the expected path.
- Falls back to the default font if the specified font file is unavailable.

This module is designed to be integrated into other applications where badge
generation and dynamic content embedding are required.
"""
import base64
import io
import math
import os

from PIL import Image, ImageDraw, ImageFont


def create_badge(line1: str, line2: str) -> str:
    """
        Generates a badge with a logo, rotated text box, and text.

        The badge includes a logo image at the top, a rotated text box with a
        shadow, and two lines of text. The output is a Base64-encoded PNG image
        suitable for embedding in HTML.

        Args:
            line1 (str): The first line of text to include in the badge.
            line2 (str): The second line of text to include in the badge.

        Returns:
            str: A Base64-encoded PNG image of the generated badge.

        Raises:
            FileNotFoundError: If the logo image is not found in the expected path.

        Example:
            badge_base64 = create_badge("Heroku Agent Action", "Deployed by Neo")
            html_fragment = f'<img src="data:image/png;base64,{badge_base64}">'
        """
    # Paths and colors
    logo_path = os.path.join("resources", "heroku_logo.png")
    font_path = "arial.ttf"  # Use the initial font (Arial Regular)
    background_color = "white"
    text_color = "black"
    shadow_color = (0, 0, 0, 128)  # Semi-transparent black for the shadow

    # Load the logo
    try:
        logo = Image.open(logo_path).convert("RGBA")
    except FileNotFoundError:
        raise FileNotFoundError(f"Logo not found at {logo_path}")

    # Resize the logo
    logo_width = 200
    aspect_ratio = logo.height / logo.width
    logo_height = int(logo_width * aspect_ratio)
    logo = logo.resize((logo_width, logo_height))

    # Font settings
    font_size = 20
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()  # Fallback to default font
        print("Warning: Arial font not found, using default font.")

    # Calculate text dimensions using textbbox
    temp_image = Image.new("RGBA", (1, 1))
    temp_draw = ImageDraw.Draw(temp_image)
    line1_bbox = temp_draw.textbbox((0, 0), line1, font=font)
    line2_bbox = temp_draw.textbbox((0, 0), line2, font=font)
    text_width = max(line1_bbox[2], line2_bbox[2])  # Use the width from bbox
    text_height = (line1_bbox[3] - line1_bbox[1]) + (line2_bbox[3] - line2_bbox[1])  # Height of both lines

    # Badge dimensions
    padding = 15
    box_padding_top_bottom = 5  # Reduced padding at the top and bottom
    box_padding_sides = 10  # Keep the same padding on the sides
    box_width = text_width + 2 * box_padding_sides
    box_height = text_height + 2 * box_padding_top_bottom
    badge_width = max(box_width + 2 * padding, logo_width + 2 * padding)
    dynamic_badge_height = logo_height + box_height + 2 * padding

    # Create badge canvas
    badge = Image.new("RGBA", (int(badge_width), int(dynamic_badge_height)), background_color)

    # Place logo at the top
    logo_x = (badge_width - logo_width) // 2
    logo_y = padding
    badge.paste(logo, (int(logo_x), int(logo_y)), logo)

    # Calculate rotated box position (adjusted below the logo with minimal overlap)
    box_x = (badge_width - box_width) // 2
    box_y = logo_y + logo_height - 10  # Adjusted positioning for minimal overlap
    rotation_angle = -10  # Tilt counter-clockwise like in the Java version

    # Expand the image to accommodate the rotated box
    diagonal = int(math.sqrt(box_width**2 + box_height**2))
    expanded_box_image = Image.new("RGBA", (diagonal, diagonal), (0, 0, 0, 0))
    expanded_box_draw = ImageDraw.Draw(expanded_box_image)

    # Center the box in the expanded image
    box_center_x = diagonal // 2
    box_center_y = diagonal // 2
    box_origin = (
        box_center_x - box_width // 2,
        box_center_y - box_height // 2,
    )

    # Draw shadow
    shadow_offset = 5
    expanded_box_draw.rectangle(
        [
            (box_origin[0] + shadow_offset, box_origin[1] + shadow_offset),
            (box_origin[0] + box_width + shadow_offset, box_origin[1] + box_height + shadow_offset),
        ],
        fill=shadow_color,
    )

    # Draw white box with border
    expanded_box_draw.rectangle(
        [box_origin, (box_origin[0] + box_width, box_origin[1] + box_height)],
        fill="white",
        outline="black",
        width=2,
    )

    # Draw text inside the box before rotation
    text_x1 = box_origin[0] + (box_width - line1_bbox[2]) // 2  # Center line 1
    text_x2 = box_origin[0] + (box_width - line2_bbox[2]) // 2  # Center line 2
    text_y_start = box_origin[1] + box_padding_top_bottom  # Adjusted for reduced padding
    expanded_box_draw.text((text_x1, text_y_start), line1, fill=text_color, font=font)
    expanded_box_draw.text(
        (text_x2, text_y_start + (line1_bbox[3] - line1_bbox[1])), line2, fill=text_color, font=font
    )

    # Rotate the expanded box
    rotated_box = expanded_box_image.rotate(
        rotation_angle, resample=Image.BICUBIC, center=(box_center_x, box_center_y)
    )

    # Paste the rotated box onto the badge
    rotated_box_position = (
        int(box_x - (box_center_x - box_width // 2)),
        int(box_y - (box_center_y - box_height // 2)),
    )
    badge.paste(rotated_box, rotated_box_position, rotated_box)

    # Save badge as Base64-encoded string
    with io.BytesIO() as output:
        badge.save(output, format="PNG")
        base64_image = base64.b64encode(output.getvalue()).decode("utf-8")

    return base64_image

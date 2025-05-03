import random
import string
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from utils.logger_utility import logger


class CaptchaGenerator:
    def __init__(self, width: int = 280, height: int = 90):
        """
        Initialize captcha generator with custom dimensions
        
        Args:
            width: Width of the captcha image
            height: Height of the captcha image
        """
        self.width = width
        self.height = height
        # Increased default font size
        self.font_size = 200
        
    def _create_image_with_text(self, text: str) -> Image.Image:
        """Create a PIL Image with the given text"""
        # Create image with white background
        image = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(image)
        
        try:
            # Try to load a system font
            font = ImageFont.load_default()
            # Scale up the default font
            image = image.resize((int(self.width * 0.6), int(self.height * 0.6)), Image.Resampling.LANCZOS)
            draw = ImageDraw.Draw(image)
        except Exception as e:
            logger.warning(f"Could not load default font: {str(e)}")
            # If default font fails, create a simple font
            font = ImageFont.truetype("arial.ttf", self.font_size)
        
        # Calculate text position to center it
        # For default font, we'll use a simpler approach with larger spacing
        text_width = len(text) * 20  # Increased spacing between characters
        text_height = 32  # Increased height for larger font
        x = (image.width - text_width) // 2
        y = (image.height - text_height) // 2
        
        # Add text with larger size
        for i, char in enumerate(text):
            # Add each character with slight random vertical offset
            char_x = x + i * 20  # Fixed horizontal spacing
            char_y = y + random.randint(-5, 5)  # Random vertical offset
            draw.text((char_x, char_y), char, fill='black', font=font)
        
        # Add some noise
        self._add_noise(image)
        
        # If we scaled up the image, scale it back down
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)
        
        return image
        
    def _add_noise(self, image: Image.Image):
        """Add random noise to the image"""
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # Add random points
        for _ in range(width * height // 30):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            draw.point((x, y), fill='black')
            
        # Add random lines with increased thickness
        for _ in range(5):
            x1 = random.randint(0, width - 1)
            y1 = random.randint(0, height - 1)
            x2 = random.randint(0, width - 1)
            y2 = random.randint(0, height - 1)
            draw.line([(x1, y1), (x2, y2)], fill='gray', width=2)  # Increased line width
        
    def generate_captcha(self, length: int = 6) -> tuple[str, str]:
        """
        Generate a captcha image and return the text and base64 encoded image
        
        Args:
            length: Length of the captcha text
            
        Returns:
            tuple[str, str]: (captcha_text, base64_encoded_image)
        """
        try:
            # Generate random text
            captcha_text = ''.join(random.choices(
                string.ascii_uppercase + string.digits, 
                k=length
            ))
            
            # Generate image
            image = self._create_image_with_text(captcha_text)
            
            # Convert to base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return captcha_text, f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Error generating captcha: {str(e)}")
            raise 
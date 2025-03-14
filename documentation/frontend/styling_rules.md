# Styling Rules
Styling for VikeEats is mainly pre-setup for developers using custom Tailwind CSS tags in **tailwind.config.js**.

## Fonts
VikeEats uses the Figtree font from Google Fonts. Unless stated below, the font weight should be 400. The following Tailwind styling rules are followed:
- **Header:** font-header-regular font-extrabold text-xl
- **Body Copy:** font-header-regular text-base
- **Highlighted Words:** font-header-regular font-bold text-base

## Hover
For hover elements whose background colour does not change on hover, the font colour should be 75% opacity normally, and full opacity on hover. 
For hover elements whose background colour does changes from white to primary-light on hover, switch the background to primary-light and the text to white.
Use a 300 ms ease-in-out transition for opacity on hover.

## Decoration
Buttons and cards should have rounded edges with rounded-md/rounded-full and an outer glow with shadow-lg. 

## Colours
The core colour palette is based on UVic's website colour palette. Detailed information can be found at https://www.uvic.ca/brand/brand-guidelines/colours-fonts/index.php. 
The primary colors are white, primary-light, and primary-dark.
The secondary color is secondary, which is currently the same as primary-light.
Accent colours are accent-blue, accent-light-blue, and accent-yellow.

### Using the Colours
- Try to balance the colours at 60% primary, 30% secondary and 10% accent
- primary-dark works well as a background or text colour, and should be the body text of most pages
- accent-blue works well as a background colour and for pin colours
- accent yellow is used sparingly and only for shapes and icons
- Use accent-yellow for components mid-way or further down the page

Last Updated: January 31st, 2025 by Sophie R.
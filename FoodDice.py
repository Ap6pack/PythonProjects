"""Seasonal Meal Idea Generator - Phase 3: UX Improvements"""

from tkinter import Tk, Label, Button, Frame, NORMAL, DISABLED, Canvas, Scrollbar, RIGHT, LEFT, BOTH, Y, VERTICAL, TOP
from tkinter import ttk
from datetime import date
import random
import urllib.request
import json
from io import BytesIO
from PIL import Image, ImageTk


# Meal component lists
COOKING_METHODS = ['grill', 'roast/bake', 'broil', 'saute', 'pan fry', 'braise']
PROTEINS = [
    'beef or tempeh',
    'chicken or tofu',
    'turkey or seitan',
    'fish or cheese',
    'pork or eggs',
    'lamb or beans'
]
GRAINS_CARBS = ['rice', 'quinoa', 'pasta', 'polenta', 'potato', 'millet']
HERBS = ['rosemary', 'basil', 'oregano', 'cilantro', 'thyme', 'dill']
BONUS_INGREDIENTS = ['mushrooms', 'bacon', 'nuts', 'onions', 'lemon', 'garlic']

# Seasonal vegetables
SEASONAL_VEGGIES = {
    'Spring': ['dandelion greens', 'peas', 'asparagus', 'artichokes', 'spinach', 'radishes'],
    'Summer': ['bell peppers', 'zucchini', 'eggplant', 'tomatoes', 'corn', 'green beans'],
    'Fall': ['mustard greens', 'brussels sprouts', 'squash', 'chard', 'broccoli', 'arugula'],
    'Winter': ['carrots', 'parsnips', 'cabbage', 'fennel', 'endives', 'kale']
}

# API mapping for proteins
PROTEIN_API_MAP = {
    'beef or tempeh': 'beef',
    'chicken or tofu': 'chicken',
    'turkey or seitan': 'turkey',
    'fish or cheese': 'salmon',
    'pork or eggs': 'pork',
    'lamb or beans': 'lamb'
}

# Modern color palette
COLORS = {
    'primary': '#2C3E50',
    'secondary': '#34495E',
    'accent': '#3498DB',
    'success': '#27AE60',
    'background': '#ECF0F1',
    'white': '#FFFFFF',
    'text': '#2C3E50',
    'text_light': '#7F8C8D',
    'shadow': '#BDC3C7',
    'warning': '#F39C12',
    
    # Component colors
    'method': '#E74C3C',
    'protein': '#E67E22',
    'grain': '#F39C12',
    'herb': '#27AE60',
    'bonus': '#9B59B6',
    'veggie': '#16A085'
}


class ComponentCard(Frame):
    """A modern card widget for displaying meal components with lock feature."""
    
    def __init__(self, parent, title, icon, color, on_lock_callback=None, **kwargs):
        super().__init__(parent, bg=COLORS['white'], relief='flat', bd=0, **kwargs)
        
        self.locked = False
        self.on_lock_callback = on_lock_callback
        self.color = color
        
        # Add shadow effect
        self.config(highlightbackground=COLORS['shadow'], highlightthickness=1)
        
        # Icon and title with lock button
        header_frame = Frame(self, bg=color, height=40)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        icon_label = Label(
            header_frame,
            text=icon,
            font=('Arial', 16),
            bg=color,
            fg=COLORS['white']
        )
        icon_label.pack(side=LEFT, padx=10, pady=8)
        
        title_label = Label(
            header_frame,
            text=title,
            font=('Arial', 10, 'bold'),
            bg=color,
            fg=COLORS['white']
        )
        title_label.pack(side=LEFT, pady=8)
        
        # Lock button
        self.lock_btn = Label(
            header_frame,
            text='🔓',
            font=('Arial', 14),
            bg=color,
            fg=COLORS['white'],
            cursor='hand2'
        )
        self.lock_btn.pack(side=RIGHT, padx=10, pady=8)
        self.lock_btn.bind('<Button-1>', lambda e: self.toggle_lock())
        
        # Value
        self.value_label = Label(
            self,
            text='...',
            font=('Arial', 14),
            bg=COLORS['white'],
            fg=COLORS['text'],
            wraplength=180,
            justify='center',
            height=2
        )
        self.value_label.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Hover effect
        self.bind('<Enter>', lambda e: self.config(highlightbackground=color, highlightthickness=2))
        self.bind('<Leave>', lambda e: self.config(highlightbackground=COLORS['shadow'], highlightthickness=1))
    
    def set_value(self, value):
        """Update the card value."""
        self.value_label.config(text=value.title())
    
    def toggle_lock(self):
        """Toggle the lock state."""
        self.locked = not self.locked
        self.lock_btn.config(text='🔒' if self.locked else '🔓')
        
        if self.on_lock_callback:
            self.on_lock_callback()
    
    def is_locked(self):
        """Check if card is locked."""
        return self.locked
    
    def get_value(self):
        """Get the current value."""
        return self.value_label.cget('text')


class RecipeCard(Frame):
    """A card widget for displaying recipe information with image."""
    
    def __init__(self, parent, recipe_number=1, **kwargs):
        super().__init__(parent, bg=COLORS['white'], relief='flat', bd=0, **kwargs)
        self.config(highlightbackground=COLORS['shadow'], highlightthickness=2)
        
        self.expanded = False
        
        # Recipe number badge
        badge = Label(
            self,
            text=f'#{recipe_number}',
            font=('Arial', 10, 'bold'),
            bg=COLORS['accent'],
            fg=COLORS['white'],
            padx=8,
            pady=4
        )
        badge.place(x=10, y=10)
        
        # Container for image and content
        self.content_frame = Frame(self, bg=COLORS['white'])
        self.content_frame.pack(fill='both', expand=True)
        
        # Image label (left side)
        self.image_label = Label(
            self.content_frame,
            bg=COLORS['background'],
            width=200,
            height=150
        )
        self.image_label.pack(side=LEFT, padx=0, pady=0)
        
        # Text content (right side)
        self.text_frame = Frame(self.content_frame, bg=COLORS['white'])
        self.text_frame.pack(side=LEFT, fill='both', expand=True, padx=20, pady=15)
        
        # Recipe name (clickable to expand)
        self.name_button = Button(
            self.text_frame,
            text='Recipe Name',
            font=('Arial', 14, 'bold'),
            bg=COLORS['white'],
            fg=COLORS['text'],
            relief='flat',
            anchor='w',
            cursor='hand2',
            command=self.toggle_expand
        )
        self.name_button.pack(fill='x', pady=(0, 10))
        
        # Quick info (always visible)
        self.quick_info = Label(
            self.text_frame,
            text='Click to view full recipe →',
            font=('Arial', 9, 'italic'),
            bg=COLORS['white'],
            fg=COLORS['text_light'],
            anchor='w'
        )
        self.quick_info.pack(fill='x', pady=(0, 5))
        
        # Expandable sections frame
        self.sections_frame = Frame(self.text_frame, bg=COLORS['white'])
        
        # Ingredients section
        self.ingredients_header = Label(
            self.sections_frame,
            text='INGREDIENTS',
            font=('Arial', 9, 'bold'),
            bg=COLORS['background'],
            fg=COLORS['text'],
            relief='flat',
            anchor='w',
            padx=10,
            pady=5
        )
        
        self.ingredients_text = Label(
            self.sections_frame,
            text='',
            font=('Arial', 9),
            bg=COLORS['white'],
            fg=COLORS['text'],
            justify='left',
            anchor='nw',
            wraplength=500
        )
        
        # Instructions section
        self.instructions_header = Label(
            self.sections_frame,
            text='INSTRUCTIONS',
            font=('Arial', 9, 'bold'),
            bg=COLORS['background'],
            fg=COLORS['text'],
            relief='flat',
            anchor='w',
            padx=10,
            pady=5
        )
        
        self.instructions_text = Label(
            self.sections_frame,
            text='',
            font=('Arial', 9),
            bg=COLORS['white'],
            fg=COLORS['text'],
            justify='left',
            anchor='nw',
            wraplength=500
        )
        
        # Hover effect
        self.bind('<Enter>', lambda e: self.config(highlightbackground=COLORS['accent'], highlightthickness=2))
        self.bind('<Leave>', lambda e: self.config(highlightbackground=COLORS['shadow'], highlightthickness=2))
    
    def toggle_expand(self):
        """Toggle recipe details visibility."""
        if self.expanded:
            # Collapse
            self.sections_frame.pack_forget()
            self.quick_info.config(text='Click to view full recipe →')
            self.expanded = False
        else:
            # Expand
            self.sections_frame.pack(fill='both', expand=True)
            self.ingredients_header.pack(fill='x', pady=(5, 2))
            self.ingredients_text.pack(fill='x', padx=10, pady=(0, 10))
            self.instructions_header.pack(fill='x', pady=(5, 2))
            self.instructions_text.pack(fill='x', padx=10, pady=(0, 10))
            self.quick_info.config(text='Click to collapse ▲')
            self.expanded = True
    
    def set_recipe(self, name, ingredients, instructions, image_url=None):
        """Update the recipe card with data."""
        self.name_button.config(text=name)
        self.ingredients_text.config(text=ingredients)
        self.instructions_text.config(text=instructions)
        
        # Load image
        if image_url:
            try:
                with urllib.request.urlopen(image_url) as url:
                    image_data = url.read()
                
                image = Image.open(BytesIO(image_data))
                image = image.resize((200, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                self.image_label.config(image=photo)
                self.image_label.image = photo
            except:
                self.image_label.config(
                    text='🍽️',
                    font=('Arial', 48),
                    bg=COLORS['background'],
                    fg=COLORS['text_light']
                )
        else:
            self.image_label.config(
                text='🍽️',
                font=('Arial', 48),
                bg=COLORS['background'],
                fg=COLORS['text_light']
            )


class LoadingSpinner(Frame):
    """Animated loading spinner."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS['background'], **kwargs)
        
        self.canvas = Canvas(self, width=60, height=60, bg=COLORS['background'], highlightthickness=0)
        self.canvas.pack()
        
        self.angle = 0
        self.animation_id = None
        
    def start(self):
        """Start the spinning animation."""
        self.animate()
    
    def stop(self):
        """Stop the spinning animation."""
        if self.animation_id:
            self.after_cancel(self.animation_id)
    
    def animate(self):
        """Animate the spinner."""
        self.canvas.delete('all')
        
        x, y, r = 30, 30, 20
        self.canvas.create_arc(
            x - r, y - r, x + r, y + r,
            start=self.angle,
            extent=280,
            outline=COLORS['accent'],
            width=4,
            style='arc'
        )
        
        self.angle = (self.angle + 10) % 360
        self.animation_id = self.after(50, self.animate)


class MealGeneratorApp:
    """Main application class for the Seasonal Meal Idea Generator."""
    
    def __init__(self, root):
        self.root = root
        self.root.title('Seasonal Meal Generator')
        self.root.configure(bg=COLORS['background'])
        
        self.root.geometry('1100x700')
        
        self.current_protein = None
        self.current_components = {}
        self.recipe_cards = []
        self.locked_components = {}
        
        self._setup_widgets()
        self._setup_layout()
    
    def _setup_widgets(self):
        """Create and configure all widgets."""
        
        # Header
        self.header_frame = Frame(self.root, bg=COLORS['primary'], height=80)
        
        self.title_label = Label(
            self.header_frame,
            text='🍽️  Seasonal Meal Generator',
            font=('Arial', 20, 'bold'),
            bg=COLORS['primary'],
            fg=COLORS['white']
        )
        
        season = self.get_current_season()
        self.season_label = Label(
            self.header_frame,
            text=f'Current Season: {season}',
            font=('Arial', 12),
            bg=COLORS['primary'],
            fg=COLORS['white']
        )
        
        # Main container with two columns
        self.main_container = Frame(self.root, bg=COLORS['background'])
        
        # LEFT COLUMN - Meal Components
        self.left_column = Frame(self.main_container, bg=COLORS['background'], width=450)
        
        left_header_frame = Frame(self.left_column, bg=COLORS['background'])
        
        left_header = Label(
            left_header_frame,
            text='Your Meal Components',
            font=('Arial', 16, 'bold'),
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        left_header.pack(side=LEFT)
        
        # Lock info tooltip
        lock_info = Label(
            left_header_frame,
            text='🔒 Lock to keep',
            font=('Arial', 9),
            bg=COLORS['background'],
            fg=COLORS['text_light']
        )
        lock_info.pack(side=LEFT, padx=10)
        
        left_header_frame.pack(pady=(20, 15))
        
        # Component cards container
        self.cards_container = Frame(self.left_column, bg=COLORS['background'])
        
        # Create component cards with lock feature
        self.method_card = ComponentCard(
            self.cards_container,
            'Cooking Method',
            '🔥',
            COLORS['method'],
            on_lock_callback=self.on_component_locked,
            width=200,
            height=120
        )
        
        self.protein_card = ComponentCard(
            self.cards_container,
            'Protein',
            '🥩',
            COLORS['protein'],
            on_lock_callback=self.on_component_locked,
            width=200,
            height=120
        )
        
        self.grain_card = ComponentCard(
            self.cards_container,
            'Grains/Carbs',
            '🌾',
            COLORS['grain'],
            on_lock_callback=self.on_component_locked,
            width=200,
            height=120
        )
        
        self.herb_card = ComponentCard(
            self.cards_container,
            'Herb',
            '🌿',
            COLORS['herb'],
            on_lock_callback=self.on_component_locked,
            width=200,
            height=120
        )
        
        self.bonus_card = ComponentCard(
            self.cards_container,
            'Bonus',
            '✨',
            COLORS['bonus'],
            on_lock_callback=self.on_component_locked,
            width=200,
            height=120
        )
        
        self.veggie_card = ComponentCard(
            self.cards_container,
            f'Seasonal Veggie',
            '🥬',
            COLORS['veggie'],
            on_lock_callback=self.on_component_locked,
            width=200,
            height=120
        )
        
        self.all_cards = [
            self.method_card,
            self.protein_card,
            self.grain_card,
            self.herb_card,
            self.bonus_card,
            self.veggie_card
        ]
        
        # Buttons for left column
        self.left_buttons = Frame(self.left_column, bg=COLORS['background'])
        
        self.generate_btn = Button(
            self.left_buttons,
            text='🎲 Generate Meal',
            command=self.generate_meal,
            font=('Arial', 12, 'bold'),
            bg=COLORS['success'],
            fg=COLORS['white'],
            relief='flat',
            padx=30,
            pady=12,
            cursor='hand2',
            activebackground='#229954'
        )
        
        self.generate_btn.bind('<Enter>', lambda e: self.generate_btn.config(bg='#229954'))
        self.generate_btn.bind('<Leave>', lambda e: self.generate_btn.config(bg=COLORS['success']) if self.generate_btn['state'] == NORMAL else None)
        
        # Auto-find recipes after generation (combined button)
        
        # RIGHT COLUMN - Recipes
        self.right_column = Frame(self.main_container, bg=COLORS['background'])
        
        right_header_frame = Frame(self.right_column, bg=COLORS['background'])
        
        right_header = Label(
            right_header_frame,
            text='Recipe Suggestions',
            font=('Arial', 16, 'bold'),
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        right_header.pack(side=LEFT)
        
        # Recipe count badge
        self.recipe_count_label = Label(
            right_header_frame,
            text='',
            font=('Arial', 10),
            bg=COLORS['background'],
            fg=COLORS['text_light']
        )
        self.recipe_count_label.pack(side=LEFT, padx=10)
        
        right_header_frame.pack(pady=(20, 15))
        
        # Scrollable recipe area
        self.recipe_canvas = Canvas(
            self.right_column,
            bg=COLORS['background'],
            highlightthickness=0
        )
        
        self.recipe_scrollbar = Scrollbar(
            self.right_column,
            orient=VERTICAL,
            command=self.recipe_canvas.yview
        )
        
        self.recipe_canvas.configure(yscrollcommand=self.recipe_scrollbar.set)
        
        self.recipe_frame = Frame(self.recipe_canvas, bg=COLORS['background'])
        self.recipe_canvas_window = self.recipe_canvas.create_window(
            (0, 0),
            window=self.recipe_frame,
            anchor='nw'
        )
        
        # Placeholder message
        self.placeholder_label = Label(
            self.recipe_frame,
            text='👈 Click "Generate Meal"\nto get started!',
            font=('Arial', 14),
            bg=COLORS['background'],
            fg=COLORS['text_light'],
            justify='center'
        )
        self.placeholder_label.pack(pady=100)
        
        # Bind canvas resize
        self.recipe_frame.bind('<Configure>', self._on_recipe_frame_configure)
        self.recipe_canvas.bind('<Configure>', self._on_canvas_configure)
    
    def _setup_layout(self):
        """Arrange widgets using grid and pack layout."""
        
        # Header
        self.header_frame.pack(fill='x')
        self.header_frame.pack_propagate(False)
        self.title_label.pack(pady=(20, 5))
        self.season_label.pack()
        
        # Main container
        self.main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left column
        self.left_column.pack(side=LEFT, fill='both', padx=(0, 10))
        self.left_column.pack_propagate(False)
        
        self.cards_container.pack(pady=10)
        
        # Arrange cards in 2x3 grid
        self.method_card.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.protein_card.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        self.grain_card.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        self.herb_card.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')
        self.bonus_card.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')
        self.veggie_card.grid(row=2, column=1, padx=10, pady=10, sticky='nsew')
        
        # Buttons
        self.left_buttons.pack(pady=20)
        self.generate_btn.pack(pady=5)
        
        # Right column
        self.right_column.pack(side=LEFT, fill='both', expand=True)
        
        self.recipe_canvas.pack(side=LEFT, fill='both', expand=True)
        self.recipe_scrollbar.pack(side=RIGHT, fill=Y)
    
    def _on_recipe_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame."""
        self.recipe_canvas.configure(scrollregion=self.recipe_canvas.bbox('all'))
    
    def _on_canvas_configure(self, event):
        """Resize the inner frame to match the canvas width."""
        canvas_width = event.width
        self.recipe_canvas.itemconfig(self.recipe_canvas_window, width=canvas_width)
    
    def get_current_season(self):
        """Determine the current season based on today's date."""
        today = date.today()
        month = today.month
        day = today.day
        
        if (month == 3 and day >= 20) or (month in [4, 5]) or (month == 6 and day <= 20):
            return 'Spring'
        elif (month == 6 and day >= 21) or (month in [7, 8]) or (month == 9 and day <= 22):
            return 'Summer'
        elif (month == 9 and day >= 23) or (month in [10, 11]) or (month == 12 and day <= 21):
            return 'Fall'
        else:
            return 'Winter'
    
    def on_component_locked(self):
        """Callback when a component is locked/unlocked."""
        locked_count = sum(1 for card in self.all_cards if card.is_locked())
        if locked_count > 0:
            self.generate_btn.config(text=f'🎲 Regenerate ({6-locked_count} new)')
        else:
            self.generate_btn.config(text='🎲 Generate Meal')
    
    def generate_meal(self):
        """Generate a random meal idea based on current season."""
        season = self.get_current_season()
        
        # Generate only unlocked components
        if not self.method_card.is_locked():
            cooking_method = random.choice(COOKING_METHODS)
            self.method_card.set_value(cooking_method)
        else:
            cooking_method = self.method_card.get_value()
        
        if not self.protein_card.is_locked():
            protein = random.choice(PROTEINS)
            self.protein_card.set_value(protein)
        else:
            protein = self.protein_card.get_value()
        
        if not self.grain_card.is_locked():
            grain_carb = random.choice(GRAINS_CARBS)
            self.grain_card.set_value(grain_carb)
        else:
            grain_carb = self.grain_card.get_value()
        
        if not self.herb_card.is_locked():
            herb = random.choice(HERBS)
            self.herb_card.set_value(herb)
        else:
            herb = self.herb_card.get_value()
        
        if not self.bonus_card.is_locked():
            bonus = random.choice(BONUS_INGREDIENTS)
            self.bonus_card.set_value(bonus)
        else:
            bonus = self.bonus_card.get_value()
        
        if not self.veggie_card.is_locked():
            veggie = random.choice(SEASONAL_VEGGIES[season])
            self.veggie_card.set_value(veggie)
        else:
            veggie = self.veggie_card.get_value()
        
        # Store current selection
        self.current_protein = protein
        self.current_components = {
            'method': cooking_method,
            'protein': protein,
            'grain': grain_carb,
            'herb': herb,
            'bonus': bonus,
            'veggie': veggie,
            'season': season
        }
        
        # Auto-find recipes after generation
        self.root.after(100, self.find_recipes)
    
    def find_recipes(self):
        """Search TheMealDB API for recipes based on generated protein."""
        if not self.current_protein:
            return
        
        # Clear previous recipes
        for widget in self.recipe_frame.winfo_children():
            widget.destroy()
        
        self.recipe_count_label.config(text='')
        
        # Show loading spinner
        loading_frame = Frame(self.recipe_frame, bg=COLORS['background'])
        loading_frame.pack(pady=50)
        
        spinner = LoadingSpinner(loading_frame)
        spinner.pack()
        spinner.start()
        
        loading_text = Label(
            loading_frame,
            text='Finding delicious recipes...',
            font=('Arial', 12),
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        loading_text.pack(pady=10)
        
        self.recipe_frame.update()
        
        # Get the API search term for the protein
        search_term = PROTEIN_API_MAP.get(self.current_protein, self.current_protein.split()[0])
        
        try:
            # Call TheMealDB API
            url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={search_term}"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
            
            meals = data.get('meals', [])
            
            spinner.stop()
            loading_frame.destroy()
            
            if meals:
                # Update recipe count
                self.recipe_count_label.config(text=f'({len(meals[:3])} recipes found)')
                
                # Get detailed info for first 3 recipes
                for i, meal in enumerate(meals[:3], 1):
                    meal_id = meal['idMeal']
                    meal_name = meal['strMeal']
                    meal_thumb = meal.get('strMealThumb')
                    
                    # Get full recipe details
                    detail_url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
                    with urllib.request.urlopen(detail_url) as detail_response:
                        detail_data = json.loads(detail_response.read().decode())
                    
                    meal_detail = detail_data['meals'][0]
                    
                    # Extract ingredients
                    ingredients = []
                    for j in range(1, 21):
                        ingredient = meal_detail.get(f'strIngredient{j}', '')
                        measure = meal_detail.get(f'strMeasure{j}', '')
                        if ingredient and ingredient.strip():
                            ingredients.append(f"• {measure.strip()} {ingredient.strip()}")
                    
                    ingredients_text = '\n'.join(ingredients)
                    instructions = meal_detail.get('strInstructions', 'No instructions available.')
                    
                    # Create recipe card with image
                    recipe_card = RecipeCard(self.recipe_frame, recipe_number=i)
                    recipe_card.set_recipe(meal_name, ingredients_text, instructions, meal_thumb)
                    recipe_card.pack(fill='x', padx=10, pady=10)
                    
            else:
                no_results = Label(
                    self.recipe_frame,
                    text=f'❌ No recipes found for {search_term}\nTry generating another meal!',
                    font=('Arial', 12),
                    bg=COLORS['background'],
                    fg=COLORS['text_light'],
                    justify='center'
                )
                no_results.pack(pady=100)
        
        except Exception as e:
            spinner.stop()
            loading_frame.destroy()
            error_label = Label(
                self.recipe_frame,
                text=f'❌ Error fetching recipes:\n{str(e)}',
                font=('Arial', 12),
                bg=COLORS['background'],
                fg=COLORS['text_light'],
                justify='center'
            )
            error_label.pack(pady=100)


def main():
    """Main entry point for the application."""
    root = Tk()
    app = MealGeneratorApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
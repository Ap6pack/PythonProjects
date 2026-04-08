"""Multi-Lottery Number Picker - Supports Powerball and Mega Millions."""

from tkinter import Tk, Label, Button, DISABLED, NORMAL, StringVar, OptionMenu, Frame
from random import sample, randint
from pathlib import Path

# Lottery configurations
LOTTERY_TYPES = {
    'Powerball': {
        'white_balls': 5,
        'white_range': (1, 69),
        'bonus_balls': 1,
        'bonus_range': (1, 26),
        'bonus_name': 'Powerball',
        'bonus_color': '#E63946'  # Red
    },
    'Mega Millions': {
        'white_balls': 5,
        'white_range': (1, 70),
        'bonus_balls': 1,
        'bonus_range': (1, 25),
        'bonus_name': 'Mega Ball',
        'bonus_color': '#FFD700'  # Gold
    }
}

DEFAULT_TEXT = '...'


class LottoPickerApp:
    """Main application class for the Multi-Lottery Number Picker."""
    
    def __init__(self, root):
        self.root = root
        self.root.title('Multi-Lottery Number Picker')
        self.root.resizable(0, 0)
        
        self.current_lottery = StringVar(value='Powerball')
        self.white_labels = []
        self.bonus_label = None
        
        self._setup_widgets()
        self._setup_layout()
    
    def _setup_widgets(self):
        """Create and configure all widgets."""
        # Lottery type selector frame
        self.lottery_frame = Frame(self.root)
        self.lottery_label = Label(
            self.lottery_frame,
            text="Select Lottery:",
            font=('Arial', 10, 'bold')
        )
        self.lottery_menu = OptionMenu(
            self.lottery_frame,
            self.current_lottery,
            *LOTTERY_TYPES.keys(),
            command=self.on_lottery_change
        )
        self.lottery_menu.config(width=15)
        
        # Create 5 white ball labels
        for _ in range(5):
            label = Label(
                self.root,
                relief='groove',
                width=4,
                height=2,
                text=DEFAULT_TEXT,
                font=('Arial', 14, 'bold'),
                bg='white'
            )
            self.white_labels.append(label)
        
        # Create bonus ball label (highlighted)
        self.bonus_label = Label(
            self.root,
            relief='groove',
            width=4,
            height=2,
            text=DEFAULT_TEXT,
            font=('Arial', 14, 'bold'),
            bg=LOTTERY_TYPES['Powerball']['bonus_color'],
            fg='white'
        )
        
        # Create bonus ball name label
        self.bonus_name_label = Label(
            self.root,
            text=LOTTERY_TYPES['Powerball']['bonus_name'],
            font=('Arial', 9)
        )
        
        # Create buttons
        self.get_btn = Button(
            self.root,
            text='Get My Lucky Numbers',
            command=self.pick_numbers,
            font=('Arial', 10),
            padx=10,
            pady=5
        )
        self.reset_btn = Button(
            self.root,
            text='Reset',
            command=self.reset,
            state=DISABLED,
            font=('Arial', 10),
            padx=10,
            pady=5
        )
    
    def _setup_layout(self):
        """Arrange widgets using grid layout."""
        # Lottery selector at top
        self.lottery_frame.grid(row=0, column=0, columnspan=6, pady=(10, 15))
        self.lottery_label.pack(side='left', padx=(0, 10))
        self.lottery_menu.pack(side='left')
        
        # White ball labels
        for i, label in enumerate(self.white_labels):
            label.grid(row=1, column=i, padx=5, pady=5)
        
        # Bonus ball label (highlighted)
        self.bonus_label.grid(row=1, column=5, padx=(15, 5), pady=5)
        
        # Bonus ball name
        self.bonus_name_label.grid(row=2, column=5, pady=(0, 10))
        
        # Buttons
        self.get_btn.grid(row=3, column=0, columnspan=4, pady=10, padx=5, sticky='ew')
        self.reset_btn.grid(row=3, column=4, columnspan=2, pady=10, padx=5, sticky='ew')
    
    def on_lottery_change(self, selection):
        """Handle lottery type change."""
        config = LOTTERY_TYPES[selection]
        
        # Update bonus ball color and name
        self.bonus_label.configure(bg=config['bonus_color'])
        self.bonus_name_label.configure(text=config['bonus_name'])
        
        # Reset the display
        self.reset()
    
    def pick_numbers(self):
        """Generate and display random lottery numbers."""
        config = LOTTERY_TYPES[self.current_lottery.get()]
        
        # Generate white balls (sorted)
        white_min, white_max = config['white_range']
        white_nums = sorted(sample(range(white_min, white_max + 1), config['white_balls']))
        
        # Display white balls
        for label, num in zip(self.white_labels, white_nums):
            label.configure(text=str(num))
        
        # Generate and display bonus ball
        bonus_min, bonus_max = config['bonus_range']
        bonus_num = randint(bonus_min, bonus_max)
        self.bonus_label.configure(text=str(bonus_num))
        
        # Update button states
        self.get_btn.configure(state=DISABLED)
        self.reset_btn.configure(state=NORMAL)
    
    def reset(self):
        """Reset all labels to default state."""
        for label in self.white_labels:
            label.configure(text=DEFAULT_TEXT)
        
        self.bonus_label.configure(text=DEFAULT_TEXT)
        
        self.get_btn.configure(state=NORMAL)
        self.reset_btn.configure(state=DISABLED)


def main():
    """Main entry point for the application."""
    root = Tk()
    app = LottoPickerApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
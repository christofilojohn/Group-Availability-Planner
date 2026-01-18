#!/usr/bin/env python3
"""
Group Scheduler - A simple scheduling tool with GUI
Features:
- Calendar-style schedule creation (9 AM - 7 PM)
- Drag to create multi-hour slots
- Export schedules to TSV
- Import multiple schedules and find overlaps
- Click participant names to view individual availability
- Clean statistics dashboard for finding best meeting times
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import os


class ScheduleCanvas(tk.Canvas):
    """Canvas widget for displaying and editing a weekly schedule."""

    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    START_HOUR = 9
    # Ends at 20, meaning the last slot is 19:00-20:00
    END_HOUR = 20

    def __init__(self, parent, editable=True, **kwargs):
        super().__init__(parent, **kwargs)
        self.editable = editable
        self.cell_width = 100
        self.cell_height = 40
        self.header_height = 30
        self.time_width = 60

        # Schedule data: {(day_index, hour): True/False}
        self.schedule = {}

        # Drag state
        self.drag_start = None
        self.drag_current = None
        self.drag_mode = None  # 'select' or 'deselect'

        # Colors
        self.colors = {
            'selected': '#4CAF50',
            'hover': '#81C784',
            'grid': '#BDBDBD',
            'header': '#2196F3',
            'header_text': 'white',
            'time_bg': '#E3F2FD',
            'time_text': '#1565C0',
        }

        self.configure(
            width=self.time_width + len(self.DAYS) * self.cell_width,
            height=self.header_height + (self.END_HOUR - self.START_HOUR) * self.cell_height
        )

        if editable:
            self.bind('<Button-1>', self.on_mouse_down)
            self.bind('<B1-Motion>', self.on_mouse_drag)
            self.bind('<ButtonRelease-1>', self.on_mouse_up)

        self.draw_grid()

    def draw_grid(self):
        """Draw the calendar grid."""
        self.delete('all')

        # Draw header background
        self.create_rectangle(
            self.time_width, 0,
            self.time_width + len(self.DAYS) * self.cell_width, self.header_height,
            fill=self.colors['header'], outline=''
        )

        # Draw day headers
        for i, day in enumerate(self.DAYS):
            x = self.time_width + i * self.cell_width + self.cell_width // 2
            self.create_text(x, self.header_height // 2, text=day[:3],
                             fill=self.colors['header_text'], font=('Arial', 10, 'bold'))

        # Draw time column background
        self.create_rectangle(
            0, self.header_height,
            self.time_width, self.header_height + (self.END_HOUR - self.START_HOUR) * self.cell_height,
            fill=self.colors['time_bg'], outline=''
        )

        # Draw time labels and grid
        for hour in range(self.START_HOUR, self.END_HOUR):
            y = self.header_height + (hour - self.START_HOUR) * self.cell_height

            # Time label
            time_str = f"{hour:02d}:00"
            self.create_text(self.time_width // 2, y + self.cell_height // 2,
                             text=time_str, font=('Arial', 10, 'bold'),
                             fill=self.colors['time_text'])

            # Grid lines
            for day in range(len(self.DAYS)):
                x = self.time_width + day * self.cell_width

                # Cell background
                if self.schedule.get((day, hour)):
                    self.create_rectangle(
                        x, y, x + self.cell_width, y + self.cell_height,
                        fill=self.colors['selected'], outline=self.colors['grid'],
                        tags=f'cell_{day}_{hour}'
                    )
                else:
                    self.create_rectangle(
                        x, y, x + self.cell_width, y + self.cell_height,
                        fill='white', outline=self.colors['grid'],
                        tags=f'cell_{day}_{hour}'
                    )

        # Draw drag selection preview
        if self.drag_start and self.drag_current:
            self.draw_drag_preview()

    def draw_drag_preview(self):
        """Draw preview of drag selection."""
        if not self.drag_start or not self.drag_current:
            return

        day1, hour1 = self.drag_start
        day2, hour2 = self.drag_current

        # Only allow vertical dragging (same day)
        if day1 != day2:
            return

        start_hour = min(hour1, hour2)
        end_hour = max(hour1, hour2)

        x = self.time_width + day1 * self.cell_width
        y1 = self.header_height + (start_hour - self.START_HOUR) * self.cell_height
        y2 = self.header_height + (end_hour - self.START_HOUR + 1) * self.cell_height

        color = self.colors['selected'] if self.drag_mode == 'select' else 'white'
        self.create_rectangle(x + 2, y1 + 2, x + self.cell_width - 2, y2 - 2,
                              fill=color, outline=self.colors['hover'], width=2,
                              tags='preview')

    def get_cell_at(self, x, y):
        """Get the (day, hour) at the given pixel coordinates."""
        if x < self.time_width or y < self.header_height:
            return None

        day = (x - self.time_width) // self.cell_width
        hour = (y - self.header_height) // self.cell_height + self.START_HOUR

        if 0 <= day < len(self.DAYS) and self.START_HOUR <= hour < self.END_HOUR:
            return (day, hour)
        return None

    def on_mouse_down(self, event):
        """Handle mouse down - start drag selection."""
        if not self.editable: return
        cell = self.get_cell_at(event.x, event.y)
        if cell:
            self.drag_start = cell
            self.drag_current = cell
            # If cell is selected, we're deselecting; otherwise selecting
            self.drag_mode = 'deselect' if self.schedule.get(cell) else 'select'
            self.draw_grid()

    def on_mouse_drag(self, event):
        """Handle mouse drag - extend selection."""
        if not self.editable or not self.drag_start:
            return

        cell = self.get_cell_at(event.x, event.y)
        if cell and cell[0] == self.drag_start[0]:  # Same day only
            self.drag_current = cell
            self.draw_grid()

    def on_mouse_up(self, event):
        """Handle mouse up - apply selection."""
        if not self.editable or not self.drag_start:
            return

        if self.drag_current:
            day = self.drag_start[0]
            start_hour = min(self.drag_start[1], self.drag_current[1])
            end_hour = max(self.drag_start[1], self.drag_current[1])

            for hour in range(start_hour, end_hour + 1):
                if self.drag_mode == 'select':
                    self.schedule[(day, hour)] = True
                else:
                    self.schedule.pop((day, hour), None)

        self.drag_start = None
        self.drag_current = None
        self.drag_mode = None
        self.draw_grid()

    def clear_schedule(self):
        """Clear all selections."""
        self.schedule.clear()
        self.draw_grid()

    def get_schedule_data(self):
        """Get schedule as a list of (day, hour) tuples."""
        return sorted(self.schedule.keys())

    def set_schedule_data(self, data):
        """Set schedule from a list of (day, hour) tuples."""
        self.schedule = {cell: True for cell in data}
        self.draw_grid()


class OverlapCanvas(tk.Canvas):
    """Canvas for displaying schedule overlaps."""

    DAYS = ScheduleCanvas.DAYS
    START_HOUR = ScheduleCanvas.START_HOUR
    END_HOUR = ScheduleCanvas.END_HOUR

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.cell_width = 100
        self.cell_height = 40
        self.header_height = 30
        self.time_width = 60

        # Overlap data: {(day, hour): count}
        self.overlap_counts = {}
        self.total_participants = 0

        self.configure(
            width=self.time_width + len(self.DAYS) * self.cell_width,
            height=self.header_height + (self.END_HOUR - self.START_HOUR) * self.cell_height
        )

        self.draw_grid()

    def get_color_for_count(self, count):
        """Get color based on overlap count."""
        if count == 0:
            return 'white'
        if self.total_participants == 0:
            return 'white'

        ratio = count / self.total_participants
        if ratio == 1.0:
            return '#1B5E20'  # Dark green - everyone available
        elif ratio >= 0.75:
            return '#4CAF50'  # Green
        elif ratio >= 0.5:
            return '#8BC34A'  # Light green
        elif ratio >= 0.25:
            return '#FFEB3B'  # Yellow
        else:
            return '#FFCDD2'  # Light red

    def draw_grid(self):
        """Draw the overlap grid."""
        self.delete('all')

        # Draw header
        self.create_rectangle(
            self.time_width, 0,
            self.time_width + len(self.DAYS) * self.cell_width, self.header_height,
            fill='#9C27B0', outline=''
        )

        for i, day in enumerate(self.DAYS):
            x = self.time_width + i * self.cell_width + self.cell_width // 2
            self.create_text(x, self.header_height // 2, text=day[:3],
                             fill='white', font=('Arial', 10, 'bold'))

        # Time column
        self.create_rectangle(
            0, self.header_height,
            self.time_width, self.header_height + (self.END_HOUR - self.START_HOUR) * self.cell_height,
            fill='#E3F2FD', outline=''
        )

        # Draw cells
        for hour in range(self.START_HOUR, self.END_HOUR):
            y = self.header_height + (hour - self.START_HOUR) * self.cell_height

            time_str = f"{hour:02d}:00"
            self.create_text(self.time_width // 2, y + self.cell_height // 2,
                             text=time_str, font=('Arial', 10, 'bold'),
                             fill='#1565C0')

            for day in range(len(self.DAYS)):
                x = self.time_width + day * self.cell_width
                count = self.overlap_counts.get((day, hour), 0)
                color = self.get_color_for_count(count)

                self.create_rectangle(
                    x, y, x + self.cell_width, y + self.cell_height,
                    fill=color, outline='#E0E0E0'
                )

                if count > 0:
                    self.create_text(
                        x + self.cell_width // 2, y + self.cell_height // 2,
                        text=str(count), font=('Arial', 10, 'bold'),
                        fill='white' if count / max(self.total_participants, 1) >= 0.5 else 'black'
                    )

    def set_overlaps(self, overlap_counts, total_participants):
        """Set overlap data and redraw."""
        self.overlap_counts = overlap_counts
        self.total_participants = total_participants
        self.draw_grid()


class GroupSchedulerApp:
    """Main application window."""

    def __init__(self, root):
        self.root = root
        self.root.title("Group Scheduler")
        self.root.geometry("1000x800")  # Slightly wider for the new stats view

        self.username = ""
        self.loaded_schedules = {}  # {username: [(day, hour), ...]}

        self.create_ui()

    def create_ui(self):
        """Create the main UI."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Create Schedule
        self.create_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.create_tab, text="📅 Create Schedule")
        self.create_schedule_tab()

        # Tab 2: View Overlaps
        self.overlap_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.overlap_tab, text="👥 View Overlaps")
        self.create_overlap_tab()

    def create_schedule_tab(self):
        """Create the schedule creation tab."""
        # Top frame - username and buttons
        top_frame = ttk.Frame(self.create_tab)
        top_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(top_frame, text="Your Name:").pack(side='left', padx=(0, 5))
        self.name_entry = ttk.Entry(top_frame, width=20)
        self.name_entry.pack(side='left', padx=(0, 20))
        self.name_entry.insert(0, "John")

        ttk.Button(top_frame, text="Clear All", command=self.clear_schedule).pack(side='left', padx=5)
        ttk.Button(top_frame, text="💾 Export Schedule", command=self.export_schedule).pack(side='left', padx=5)

        # Instructions
        instructions = ttk.Label(
            self.create_tab,
            text="Click and drag vertically to select time slots. Click on selected slots to deselect.",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        )
        instructions.pack(pady=(0, 10))

        # Schedule canvas in a frame with scrollbar
        canvas_frame = ttk.Frame(self.create_tab)
        canvas_frame.pack(fill='both', expand=True)

        self.schedule_canvas = ScheduleCanvas(canvas_frame, editable=True, bg='white')
        self.schedule_canvas.pack(pady=10)

        # Legend
        legend_frame = ttk.Frame(self.create_tab)
        legend_frame.pack(pady=10)

        ttk.Label(legend_frame, text="Legend:", font=('Arial', 9, 'bold')).pack(side='left', padx=(0, 10))

        # Available indicator
        avail_canvas = tk.Canvas(legend_frame, width=20, height=20)
        avail_canvas.create_rectangle(2, 2, 18, 18, fill='#4CAF50', outline='gray')
        avail_canvas.pack(side='left')
        ttk.Label(legend_frame, text="Available").pack(side='left', padx=(2, 15))

        # Unavailable indicator
        unavail_canvas = tk.Canvas(legend_frame, width=20, height=20)
        unavail_canvas.create_rectangle(2, 2, 18, 18, fill='white', outline='gray')
        unavail_canvas.pack(side='left')
        ttk.Label(legend_frame, text="Not Available").pack(side='left', padx=(2, 0))

    def create_overlap_tab(self):
        """Create the overlap viewing tab."""
        # Main Layout: Left side (Controls + List) / Right side (Canvas)
        paned = ttk.PanedWindow(self.overlap_tab, orient=tk.HORIZONTAL)
        paned.pack(fill='both', expand=True, padx=5, pady=5)

        left_frame = ttk.Frame(paned, width=300)
        right_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        paned.add(right_frame, weight=3)

        # --- LEFT PANEL ---

        # 1. Controls
        control_frame = ttk.LabelFrame(left_frame, text="Controls")
        control_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(control_frame, text="📁 Load Files", command=self.load_schedules).pack(fill='x', padx=5, pady=2)
        ttk.Button(control_frame, text="🗑️ Clear All", command=self.clear_loaded_schedules).pack(fill='x', padx=5,
                                                                                                 pady=2)
        ttk.Button(control_frame, text="📊 Export", command=self.export_analysis).pack(fill='x', padx=5, pady=2)

        # 2. Loaded Participants List
        list_frame = ttk.LabelFrame(left_frame, text="Participants (Click to view)")
        list_frame.pack(fill='x', padx=5, pady=5)

        self.loaded_listbox = tk.Listbox(list_frame, height=6)
        self.loaded_listbox.pack(fill='x', padx=5, pady=5)
        self.loaded_listbox.bind('<<ListboxSelect>>', self.on_participant_selected)

        # 3. Clean Statistics Dashboard
        stats_frame = ttk.LabelFrame(left_frame, text="Analysis Dashboard")
        stats_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Summary Counters
        summary_grid = ttk.Frame(stats_frame)
        summary_grid.pack(fill='x', padx=5, pady=5)

        ttk.Label(summary_grid, text="Participants:", font=('Arial', 9)).grid(row=0, column=0, sticky='w')
        self.lbl_part_count = ttk.Label(summary_grid, text="0", font=('Arial', 9, 'bold'))
        self.lbl_part_count.grid(row=0, column=1, sticky='e', padx=10)

        ttk.Label(summary_grid, text="Perfect Matches:", font=('Arial', 9)).grid(row=1, column=0, sticky='w')
        self.lbl_match_count = ttk.Label(summary_grid, text="0", font=('Arial', 9, 'bold'), foreground='#1B5E20')
        self.lbl_match_count.grid(row=1, column=1, sticky='e', padx=10)

        # Intersection List
        ttk.Separator(stats_frame, orient='horizontal').pack(fill='x', pady=5)
        ttk.Label(stats_frame, text="Perfect Overlap Times:", font=('Arial', 9, 'bold')).pack(anchor='w', padx=5)

        # Treeview for slots
        cols = ('day', 'time')
        self.tree = ttk.Treeview(stats_frame, columns=cols, show='headings', height=10)
        self.tree.heading('day', text='Day')
        self.tree.heading('time', text='Time')
        self.tree.column('day', width=80)
        self.tree.column('time', width=60)

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side='right', fill='y', pady=5, padx=(0, 5))

        # --- RIGHT PANEL (Canvas) ---

        canvas_container = ttk.Frame(right_frame)
        canvas_container.pack(fill='both', expand=True)

        self.overlap_canvas = OverlapCanvas(canvas_container, bg='white')
        self.overlap_canvas.pack(pady=10, padx=10)

        # Legend (Horizontal under canvas)
        legend_frame = ttk.Frame(right_frame)
        legend_frame.pack(pady=10)

        colors = [
            ('#1B5E20', 'All Available'),
            ('#4CAF50', '75%+'),
            ('#8BC34A', '50%+'),
            ('#FFEB3B', '25%+'),
            ('#FFCDD2', '<25%'),
        ]

        for color, label in colors:
            c = tk.Canvas(legend_frame, width=15, height=15)
            c.create_rectangle(0, 0, 15, 15, fill=color, outline='gray')
            c.pack(side='left', padx=(10, 2))
            ttk.Label(legend_frame, text=label, font=('Arial', 8)).pack(side='left')

    def on_participant_selected(self, event):
        """Handle selection of a participant from the listbox."""
        selection = self.loaded_listbox.curselection()
        if not selection:
            return

        item_text = self.loaded_listbox.get(selection[0])
        username = item_text.split(" (")[0]

        if username in self.loaded_schedules:
            self.show_participant_popup(username, self.loaded_schedules[username])

    def show_participant_popup(self, username, schedule_data):
        """Show a popup window with the participant's schedule."""
        popup = tk.Toplevel(self.root)
        popup.title(f"Schedule: {username}")
        popup.geometry("800x600")

        ttk.Label(popup, text=f"Availability for {username}", font=('Arial', 12, 'bold')).pack(pady=10)

        canvas_frame = ttk.Frame(popup)
        canvas_frame.pack(fill='both', expand=True, padx=10, pady=10)

        p_canvas = ScheduleCanvas(canvas_frame, editable=False, bg='white')
        p_canvas.pack(pady=5)
        p_canvas.set_schedule_data(schedule_data)

        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

    def clear_schedule(self):
        """Clear the current schedule."""
        self.schedule_canvas.clear_schedule()

    def export_schedule(self):
        """Export the current schedule to a TSV file."""
        username = self.name_entry.get().strip()
        if not username:
            messagebox.showwarning("Warning", "Please enter your name first.")
            return

        schedule_data = self.schedule_canvas.get_schedule_data()
        if not schedule_data:
            messagebox.showwarning("Warning", "Your schedule is empty.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".tsv",
            filetypes=[("TSV files", "*.tsv"), ("All files", "*.*")],
            initialfile=f"schedule_{username}.tsv"
        )

        if not filename:
            return

        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerow(['username', 'day', 'day_name', 'hour'])
                for day, hour in schedule_data:
                    writer.writerow([username, day, ScheduleCanvas.DAYS[day], hour])

            messagebox.showinfo("Success", f"Schedule exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")

    def load_schedules(self):
        """Load multiple schedule files."""
        filenames = filedialog.askopenfilenames(
            filetypes=[("TSV files", "*.tsv"), ("CSV files", "*.csv"), ("All files", "*.*")],
            title="Select Schedule Files"
        )

        if not filenames:
            return

        for filename in filenames:
            try:
                delimiter = '\t' if filename.endswith('.tsv') else ','
                with open(filename, 'r') as f:
                    reader = csv.DictReader(f, delimiter=delimiter)

                    username = None
                    schedule = []

                    for row in reader:
                        if username is None:
                            username = row.get('username', os.path.basename(filename))
                        day = int(row['day'])
                        hour = int(row['hour'])
                        schedule.append((day, hour))

                    if username and schedule:
                        base_username = username
                        counter = 1
                        while username in self.loaded_schedules:
                            username = f"{base_username}_{counter}"
                            counter += 1

                        self.loaded_schedules[username] = schedule
                        self.loaded_listbox.insert(tk.END, f"{username} ({len(schedule)} slots)")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load {filename}:\n{str(e)}")

        self.update_overlaps()

    def clear_loaded_schedules(self):
        """Clear all loaded schedules."""
        self.loaded_schedules.clear()
        self.loaded_listbox.delete(0, tk.END)
        self.overlap_canvas.set_overlaps({}, 0)

        # Reset Stats
        self.lbl_part_count.config(text="0")
        self.lbl_match_count.config(text="0")
        for item in self.tree.get_children():
            self.tree.delete(item)

    def update_overlaps(self):
        """Calculate and display overlaps."""
        if not self.loaded_schedules:
            return

        # 1. Count overlaps
        overlap_counts = {}
        for username, schedule in self.loaded_schedules.items():
            for cell in schedule:
                overlap_counts[cell] = overlap_counts.get(cell, 0) + 1

        total = len(self.loaded_schedules)
        self.overlap_canvas.set_overlaps(overlap_counts, total)

        # 2. Update Statistics Dashboard

        # Find perfect overlaps (Intersections)
        full_overlap_slots = [cell for cell, count in overlap_counts.items() if count == total]
        full_overlap_slots.sort()

        # Update labels
        self.lbl_part_count.config(text=str(total))
        self.lbl_match_count.config(text=str(len(full_overlap_slots)))

        # Update Treeview (Clear first)
        for item in self.tree.get_children():
            self.tree.delete(item)

        if full_overlap_slots:
            for day, hour in full_overlap_slots:
                day_name = ScheduleCanvas.DAYS[day]
                time_str = f"{hour:02d}:00"
                self.tree.insert('', 'end', values=(day_name, time_str))
        else:
            # Optional: If no perfect overlap, maybe show "None"
            pass

    def export_analysis(self):
        """Export the overlap analysis to a file."""
        if not self.loaded_schedules:
            messagebox.showwarning("Warning", "No schedules loaded.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".tsv",
            filetypes=[("TSV files", "*.tsv"), ("All files", "*.*")],
            initialfile="schedule_analysis.tsv"
        )

        if not filename:
            return

        try:
            overlap_counts = {}
            for username, schedule in self.loaded_schedules.items():
                for cell in schedule:
                    overlap_counts[cell] = overlap_counts.get(cell, 0) + 1

            total = len(self.loaded_schedules)

            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerow(['day', 'day_name', 'hour', 'available_count', 'total_participants', 'percentage'])

                for day in range(7):
                    for hour in range(ScheduleCanvas.START_HOUR, ScheduleCanvas.END_HOUR):
                        count = overlap_counts.get((day, hour), 0)
                        pct = (count / total * 100) if total > 0 else 0
                        writer.writerow([
                            day,
                            ScheduleCanvas.DAYS[day],
                            hour,
                            count,
                            total,
                            f"{pct:.1f}%"
                        ])

            messagebox.showinfo("Success", f"Analysis exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")


def main():
    root = tk.Tk()
    app = GroupSchedulerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
import sys
import copy
import random
from PyQt5 import QtWidgets, QtCore, QtGui

# ==============================================
# Common Sudoku Styling and Utilities
# ==============================================
class SudokuUICommon:
    @staticmethod
    def cell_style(row, col, is_readonly=False, has_conflict=False):
        style = []
        # Thicker borders for 3x3 subgrid separation
        if row % 3 == 0:
            style.append("border-top: 3px solid #000000;")
        else:
            style.append("border-top: 1px solid #dee2e6;")
        
        if (row + 1) % 3 == 0:
            style.append("border-bottom: 3px solid #000000;")
        else:
            style.append("border-bottom: 1px solid #dee2e6;")
        
        if col % 3 == 0:
            style.append("border-left: 3px solid #000000;")
        else:
            style.append("border-left: 1px solid #dee2e6;")
        
        if (col + 1) % 3 == 0:
            style.append("border-right: 3px solid #000000;")
        else:
            style.append("border-right: 1px solid #dee2e6;")
        
        bg_color = "#f8f9fa" if (row // 3 + col // 3) % 2 == 0 else "#ffffff"
        conflict_color = "#ffebee" if has_conflict else bg_color
        
        readonly_style = f"""
            background-color: {bg_color};
            color: #2c3e50;
            font-weight: bold;
        """
        editable_style = f"""
            background-color: {conflict_color};
            color: #2980b9;
        """
        return f"""
            QLineEdit {{
                {' '.join(style)}
                {readonly_style if is_readonly else editable_style}
                font-size: 24px;
                selection-background-color: #3498db;
                selection-color: white;
                padding: 0px;
                margin: 0px;
            }}
            QLineEdit:focus {{
                background-color: #e3f2fd;
                border: 2px solid #3498db;
            }}
        """


APP_STYLESHEET = """
QMainWindow {
    background-color: #f8f9fa;
}
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 14px;
    min-width: 80px;
}
QPushButton:hover {
    background-color: #2980b9;
}
QPushButton:pressed {
    background-color: #1a5980;
}
QComboBox {
    padding: 5px;
    border: 1px solid #ced4da;
    border-radius: 4px;
    min-width: 120px;
}
QLabel {
    color: #2c3e50;
    font-size: 14px;
}
QTabWidget::pane {
    border: none;
}
QTabBar::tab {
    background: #e9ecef;
    color: #495057;
    padding: 8px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #3498db;
    color: white;
}
QFrame#sudoku_frame {
    background: #ffffff;
    border-radius: 6px;
    border: 2px solid #dee2e6;
}
"""

# ==============================================
# Sudoku Engine (Generator + Solver)
# ==============================================
class SudokuGenerator:
    @staticmethod
    def create_puzzle(difficulty):
        base = [[0] * 9 for _ in range(9)]
        rows = [set(range(1, 10)) for _ in range(9)]
        cols = [set(range(1, 10)) for _ in range(9)]
        boxes = [set(range(1, 10)) for _ in range(9)]
        for i in range(9):
            for j in range(9):
                box_idx = (i // 3) * 3 + j // 3
                candidates = rows[i] & cols[j] & boxes[box_idx]
                if not candidates:
                    return None
                num = random.choice(list(candidates))
                base[i][j] = num
                rows[i].remove(num)
                cols[j].remove(num)
                boxes[box_idx].remove(num)
        puzzle = copy.deepcopy(base)
        dif_levels = {"easy": 35, "medium": 45, "hard": 55}
        empty_cells = dif_levels.get(difficulty.lower(), 35)
        count = 0
        while count < empty_cells:
            i, j = random.randint(0, 8), random.randint(0, 8)
            if puzzle[i][j] != 0:
                puzzle[i][j] = 0
                count += 1
        return puzzle


class SudokuSolver:
    @staticmethod
    def is_valid(grid, row, col, num):
        if num == 0:
            return False
        if num in grid[row]:
            return False
        if any(grid[i][col] == num for i in range(9)):
            return False
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if grid[start_row + i][start_col + j] == num:
                    return False
        return True

    @staticmethod
    def has_conflict(grid, row, col):
        value = grid[row][col]
        if value == 0:
            return False
        # Row check
        if grid[row].count(value) > 1:
            return True
        # Column check
        if [grid[i][col] for i in range(9)].count(value) > 1:
            return True
        # Box check
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        box = [grid[start_row + i][start_col + j] for i in range(3) for j in range(3)]
        return box.count(value) > 1

    @staticmethod
    def solve(grid):
        empty = next(((i, j) for i in range(9) for j in range(9) if grid[i][j] == 0), None)
        if not empty:
            return True
        row, col = empty
        for num in random.sample(range(1, 10), 9):
            if SudokuSolver.is_valid(grid, row, col, num):
                grid[row][col] = num
                if SudokuSolver.solve(grid):
                    return True
                grid[row][col] = 0
        return False

    @staticmethod
    def validate_puzzle(grid):
        try:
            for i in range(9):
                for j in range(9):
                    if grid[i][j] != 0 and SudokuSolver.has_conflict(grid, i, j):
                        return False
            return True
        except:
            return False


# ==============================================
# Game Interface Components
# ==============================================
class SudokuGame(QtWidgets.QWidget):
    def __init__(self, initial_grid=None):
        super().__init__()
        self.original_grid = initial_grid or [[0] * 9 for _ in range(9)]
        self.initial_grid = copy.deepcopy(self.original_grid)
        self.current_grid = copy.deepcopy(self.initial_grid)
        self.undo_stack = []
        self.redo_stack = []
        self.init_ui()
        self.update_grid()

    def init_ui(self):
        self.setContentsMargins(10, 10, 10, 10)
        layout = QtWidgets.QVBoxLayout()
        # Sudoku Grid
        grid_frame = QtWidgets.QFrame()
        grid_frame.setObjectName("sudoku_frame")
        grid_frame.setStyleSheet("background: #ffffff;")
        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.cells = []
        for i in range(9):
            row = []
            for j in range(9):
                cell = QtWidgets.QLineEdit()
                cell.setFixedSize(60, 60)
                cell.setAlignment(QtCore.Qt.AlignCenter)
                cell.setFont(QtGui.QFont("Arial", 20, QtGui.QFont.Bold))
                cell.setMaxLength(1)
                # Only allow numbers 1-9 as input
                validator = QtGui.QRegExpValidator(QtCore.QRegExp("[1-9]"), cell)
                cell.setValidator(validator)
                cell.textChanged.connect(lambda text, r=i, c=j: self.on_cell_change(r, c, text))
                row.append(cell)
                self.grid_layout.addWidget(cell, i, j)
            self.cells.append(row)
        grid_frame.setLayout(self.grid_layout)
        layout.addWidget(grid_frame, 0, QtCore.Qt.AlignCenter)
        self.setLayout(layout)

    def update_grid(self):
        for i in range(9):
            for j in range(9):
                cell = self.cells[i][j]
                value = self.initial_grid[i][j]
                if value != 0:
                    cell.setText(str(value))
                    cell.setReadOnly(True)
                    cell.setStyleSheet(SudokuUICommon.cell_style(i, j, True))
                else:
                    cell.setText("")
                    cell.setReadOnly(False)
                    cell.setStyleSheet(SudokuUICommon.cell_style(i, j, False))
        self.update_colors()

    def update_colors(self):
        for i in range(9):
            for j in range(9):
                if self.initial_grid[i][j] != 0:
                    continue
                value = self.current_grid[i][j]
                conflict = SudokuSolver.has_conflict(self.current_grid, i, j)
                style = SudokuUICommon.cell_style(i, j, False, conflict)
                self.cells[i][j].setStyleSheet(style)

    def on_cell_change(self, row, col, text):
        old_value = self.current_grid[row][col]
        try:
            new_value = int(text) if text else 0
        except:
            new_value = 0
        if new_value != old_value:
            self.undo_stack.append((row, col, old_value))
            self.redo_stack.clear()
            self.current_grid[row][col] = new_value
            self.update_colors()

    def undo(self):
        if self.undo_stack:
            row, col, value = self.undo_stack.pop()
            current = self.current_grid[row][col]
            self.redo_stack.append((row, col, current))
            self.current_grid[row][col] = value
            self.cells[row][col].setText(str(value) if value != 0 else "")
            self.update_colors()

    def redo(self):
        if self.redo_stack:
            row, col, value = self.redo_stack.pop()
            current = self.current_grid[row][col]
            self.undo_stack.append((row, col, current))
            self.current_grid[row][col] = value
            self.cells[row][col].setText(str(value) if value != 0 else "")
            self.update_colors()

    def clear(self):
        # Clear ALL cells (including preset values)
        for i in range(9):
            for j in range(9):
                self.initial_grid[i][j] = 0
                self.current_grid[i][j] = 0
                self.cells[i][j].setText("")
                self.cells[i][j].setReadOnly(False)
                self.cells[i][j].setStyleSheet(SudokuUICommon.cell_style(i, j, False))
        self.undo_stack.clear()
        self.redo_stack.clear()

    def reset(self):
        # Reset to original preset values
        self.initial_grid = copy.deepcopy(self.original_grid)
        self.current_grid = copy.deepcopy(self.original_grid)
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.update_grid()

    def solve(self):
        if not SudokuSolver.validate_puzzle(self.current_grid):
            QtWidgets.QMessageBox.warning(
                self,
                "Invalid Puzzle",
                "This puzzle contains conflicts and cannot be solved."
            )
            return
        grid_copy = copy.deepcopy(self.current_grid)
        if SudokuSolver.solve(grid_copy):
            self.current_grid = grid_copy
            for i in range(9):
                for j in range(9):
                    self.cells[i][j].setText(str(grid_copy[i][j]))
            self.update_colors()
        else:
            QtWidgets.QMessageBox.information(
                self,
                "No Solution",
                "This puzzle doesn't have a valid solution."
            )


# ==============================================
# Main Application Window
# ==============================================
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sudoku Master")
        self.setFixedSize(680, 800)
        self.setStyleSheet(APP_STYLESHEET)
        self.init_ui()

    def init_ui(self):
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self.create_new_puzzle_tab(), "New Game")
        tabs.addTab(self.create_preset_puzzle_tab(), "Preset Puzzles")
        self.setCentralWidget(tabs)

    def create_new_puzzle_tab(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Control panel
        control_frame = QtWidgets.QFrame()
        control_layout = QtWidgets.QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        
        # Difficulty selection
        diff_layout = QtWidgets.QHBoxLayout()
        diff_layout.addWidget(QtWidgets.QLabel("Difficulty:"))
        self.difficulty_combo = QtWidgets.QComboBox()
        self.difficulty_combo.addItems(["Easy", "Medium", "Hard"])
        diff_layout.addWidget(self.difficulty_combo)
        control_layout.addLayout(diff_layout)
        
        control_layout.addStretch()
        
        # Buttons
        self.new_game_btn = QtWidgets.QPushButton("New Game")
        self.undo_btn = QtWidgets.QPushButton("Undo")
        self.redo_btn = QtWidgets.QPushButton("Redo")
        self.clear_btn = QtWidgets.QPushButton("Clear")
        self.solve_btn = QtWidgets.QPushButton("Solve")
        
        control_layout.addWidget(self.new_game_btn)
        control_layout.addWidget(self.undo_btn)
        control_layout.addWidget(self.redo_btn)
        control_layout.addWidget(self.clear_btn)
        control_layout.addWidget(self.solve_btn)
        
        control_frame.setLayout(control_layout)
        layout.addWidget(control_frame)
        
        # Game board
        self.game = SudokuGame()
        layout.addWidget(self.game, 1)
        
        widget.setLayout(layout)
        
        # Connect signals
        self.new_game_btn.clicked.connect(self.new_game)
        self.undo_btn.clicked.connect(self.game.undo)
        self.redo_btn.clicked.connect(self.game.redo)
        self.clear_btn.clicked.connect(self.game.clear)
        self.solve_btn.clicked.connect(self.game.solve)
        
        return widget

    def create_preset_puzzle_tab(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Preset puzzle (classic example with solution)
        preset_puzzle = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ]
        
        # Control panel
        control_frame = QtWidgets.QFrame()
        control_layout = QtWidgets.QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        
        control_layout.addStretch()
        
        # Buttons
        self.undo_btn_preset = QtWidgets.QPushButton("Undo")
        self.redo_btn_preset = QtWidgets.QPushButton("Redo")
        self.clear_btn_preset = QtWidgets.QPushButton("Clear All")
        self.reset_btn_preset = QtWidgets.QPushButton("Reset")
        self.solve_preset_btn = QtWidgets.QPushButton("Solve")
        
        control_layout.addWidget(self.undo_btn_preset)
        control_layout.addWidget(self.redo_btn_preset)
        control_layout.addWidget(self.clear_btn_preset)
        control_layout.addWidget(self.reset_btn_preset)
        control_layout.addWidget(self.solve_preset_btn)
        
        control_frame.setLayout(control_layout)
        layout.addWidget(control_frame)
        
        # Game board
        self.preset_game = SudokuGame(preset_puzzle)
        layout.addWidget(self.preset_game, 1)
        
        widget.setLayout(layout)
        
        # Connect signals
        self.undo_btn_preset.clicked.connect(self.preset_game.undo)
        self.redo_btn_preset.clicked.connect(self.preset_game.redo)
        self.clear_btn_preset.clicked.connect(self.preset_game.clear)
        self.reset_btn_preset.clicked.connect(self.preset_game.reset)
        self.solve_preset_btn.clicked.connect(self.preset_game.solve)
        
        return widget

    def new_game(self):
        difficulty = self.difficulty_combo.currentText().lower()
        puzzle = None
        while not puzzle:
            puzzle = SudokuGenerator.create_puzzle(difficulty)
        self.game.initial_grid = copy.deepcopy(puzzle)
        self.game.current_grid = copy.deepcopy(puzzle)
        self.game.undo_stack.clear()
        self.game.redo_stack.clear()
        self.game.update_grid()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
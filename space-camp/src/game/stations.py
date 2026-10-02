class Station:
    def __init__(self, name, task_description, correct_input):
        self.name = name
        self.task_description = task_description
        self.correct_input = correct_input
        self.completed = False

    def validate_input(self, user_input):
        if user_input == self.correct_input:
            self.completed = True
            return True
        return False

    def get_task_info(self):
        return f"Task: {self.task_description} (Station: {self.name})"

def create_stations():
    stations = [
        Station("Launch Pad", "Press the button to launch the rocket!", "A"),
        Station("Orbit", "Press the button to enter orbit!", "B"),
        Station("Landing", "Press the button to land safely!", "C"),
    ]
    return stations
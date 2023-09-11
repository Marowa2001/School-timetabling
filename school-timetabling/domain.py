import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import optapy
from optapy import problem_fact, planning_id, planning_entity, planning_variable, \
    planning_solution, planning_entity_collection_property, \
    problem_fact_collection_property, \
    value_range_provider, planning_score
from optapy.types import HardSoftScore
from datetime import time


@problem_fact
class Room:
    id: int
    name: str

    def __init__(self, id, name):
        self.id = id
        self.name = name

    @planning_id
    def get_id(self):
        return self.id

    def __str__(self):
        return f"Room(id={self.id}, name={self.name})"


@problem_fact
class Timeslot:
    id: int
    day_of_week: str
    start_time: datetime.time
    end_time: datetime.time

    def __init__(self, id, day_of_week, start_time, end_time):
        self.id = id
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.lesson = None
    @planning_id
    def get_id(self):
        return self.id

    def __str__(self):
        return (
                f"Timeslot("
                f"id={self.id}, "
                f"day_of_week={self.day_of_week}, "
                f"start_time={self.start_time}, "
                f"end_time={self.end_time})"
        )


@planning_entity
class Lesson:
    id: int
    subject: str
    teacher: str
    StudentGroup: str
    timeslot: Timeslot
    room: Room
    credit_hour: int
    def __init__(self, id, subject, teacher, StudentGroup, credit_hour, timeslot=None, room=None):
        self.id = id
        self.subject = subject
        self.teacher = teacher
        self.StudentGroup = StudentGroup
        self.timeslot = timeslot
        self.room = room
        self.credit_hour = credit_hour
        
    @planning_id
    def get_id(self):
        return self.id

    @planning_variable(Timeslot, ["timeslotRange"])
    def get_timeslot(self):
        return self.timeslot

    def set_timeslot(self, new_timeslot):
        self.timeslot = new_timeslot

    @planning_variable(Room, ["roomRange"])
    def get_room(self):
        return self.room

    def set_room(self, new_room):
        self.room = new_room

    def __str__(self):
        return (
            f"Lesson("
            f"id={self.id}, "
            f"timeslot={self.timeslot}, "
            f"room={self.room}, "
            f"teacher={self.teacher}, "
            f"subject={self.subject}, "
            f"StudentGroup={self.StudentGroup},"
            f"credit_hour={self.credit_hour}"
            f")"
        )

@problem_fact
class StudentGroup:
    id: int
    name: str

    def __init__(self, id, name):
        self.id = id
        self.name = name

    @planning_id
    def get_id(self):
        return self.id

    def __str__(self):
        return f"StudentGroup(id={self.id}, name={self.name})"



def format_list(a_list):
    return ',\n'.join(map(str, a_list))


@planning_solution
class TimeTable:
    timeslot_list: list[Timeslot]
    room_list: list[Room]
    lesson_list: list[Lesson]
    student_group_list: list[StudentGroup]
    score: HardSoftScore

    def __init__(self, timeslot_list, room_list, lesson_list, student_group_list, score=None):
        self.timeslot_list = timeslot_list
        self.room_list = room_list
        self.lesson_list = lesson_list
        self.student_group_list = student_group_list
        self.score = score

    @problem_fact_collection_property(Timeslot)
    @value_range_provider("timeslotRange")
    def get_timeslot_list(self):
        return self.timeslot_list

    @problem_fact_collection_property(Room)
    @value_range_provider("roomRange")
    def get_room_list(self):
        return self.room_list

    @planning_entity_collection_property(Lesson)
    def get_lesson_list(self):
        return self.lesson_list
    
    @problem_fact_collection_property(StudentGroup)
    @value_range_provider("studentGroupRange")
    def get_student_group_list(self):
       return self.student_group_list

    @planning_score(HardSoftScore)
    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score
    
    def __str__(self):
        return (
            f"TimeTable("
            f"timeslot_list={format_list(self.timeslot_list)},\n"
            f"room_list={format_list(self.room_list)},\n"
            f"lesson_list={format_list(self.lesson_list)},\n"
            f"student_group_list={format_list(self.student_group_list)},\n"
            f"score={str(self.score)}" if self.score is not None else "None"
            f")"
        )

def generate_problem():
    root = tk.Tk()
    root.withdraw()

    # Prompt user for starting time of the first slot
    start_time = prompt_input("Enter starting time of the first slot (e.g. 08:20): ")

    # Prompt user for ending time of the last slot
    end_time = prompt_input("Enter ending time of the last slot (e.g. 13:20): ")

    # Prompt user for the total time of each slot
    slot_duration = prompt_input("Enter the duration of each slot in minutes (e.g. 50): ", data_type=int)

    # Prompt user for the days when classes will be conducted
    days_of_week = prompt_input("Enter the days of the week when classes will be conducted (comma-separated, e.g. MONDAY,TUESDAY): ", split=True)

    # Calculate the number of slots per day
    start_datetime = datetime.datetime.strptime(start_time, "%H:%M")
    end_datetime = datetime.datetime.strptime(end_time, "%H:%M")
    total_minutes = (end_datetime - start_datetime).seconds // 60
    num_slots = total_minutes // slot_duration

    timeslot_list = generate_timeslots(start_datetime, num_slots, slot_duration, days_of_week)

    num_rooms = prompt_input("Enter the number of rooms: ", data_type=int)
    room_list = generate_rooms(num_rooms)

    num_lessons = prompt_input("Enter the number of lessons: ", data_type=int)
    lesson_list, student_group_list = generate_lessons(num_lessons)

    return TimeTable(timeslot_list, room_list, lesson_list, student_group_list)

def prompt_input(message, data_type=str, split=False):
    
    value = None

    while value is None:
        user_input = simpledialog.askstring("Input", message)
        if user_input is not None:
            if split:
                value = user_input.split(',')
            else:
                try:
                    value = data_type(user_input)
                except ValueError:
                    messagebox.showerror("Error", "Invalid input. Please try again.")

    return value

def generate_timeslots(start_datetime, num_slots, slot_duration, days_of_week):
    timeslot_list = []

    for day_of_week in days_of_week:
        current_time = start_datetime
        for i in range(num_slots):
            start_slot = current_time.time()
            end_slot = (current_time + datetime.timedelta(minutes=slot_duration)).time()
            timeslot_list.append(Timeslot(len(timeslot_list) + 1, day_of_week, start_slot, end_slot))
            current_time += datetime.timedelta(minutes=slot_duration)

    return timeslot_list

def generate_rooms(num_rooms):
    room_list = []

    for i in range(1, num_rooms + 1):
        room_name = f"{i:03}"  # Generates room name with leading zeros
        room = Room(i, room_name)
        room_list.append(room)

    return room_list

def generate_lessons(num_lessons):
    lesson_list = []
    student_group_set = set()

    for i in range(1, num_lessons + 1):
        subject = prompt_input(f"Enter the subject for lesson {i}: ")
        teacher = prompt_input(f"Enter the teacher for lesson {i}: ")
        student_group = prompt_input(f"Enter the grade for lesson {i}: ")
        credit_hour = prompt_input(f"Enter the credit hour for lesson {i}: ", data_type=int)

        for _ in range(credit_hour):
            lesson = Lesson(len(lesson_list) + 1, subject, teacher, student_group, credit_hour)
            lesson_list.append(lesson)
            student_group_set.add(student_group)

    student_group_list = list(student_group_set)
    return lesson_list, student_group_list




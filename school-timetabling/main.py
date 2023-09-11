from functools import reduce
import tkinter as tk
from tkinter import messagebox
from optapy import solver_factory_create
from optapy.types import SolverConfig, Duration
from domain import TimeTable, Lesson, generate_problem
from constraints import define_constraints


def print_timetable(timetable: TimeTable):
    student_group_list = timetable.student_group_list
    lesson_list = timetable.lesson_list
    timeslot_student_group_lesson_triple_list = list(map(lambda the_lesson: (the_lesson.timeslot, the_lesson.StudentGroup, the_lesson),
                                                         filter(lambda the_lesson:
                                                                the_lesson.timeslot is not None and
                                                                the_lesson.StudentGroup is not None,
                                                                lesson_list)))
    lesson_map = dict()
    for timeslot, StudentGroup, lesson in timeslot_student_group_lesson_triple_list:
        if timeslot in lesson_map:
            if StudentGroup in lesson_map[timeslot]:
                lesson_map[timeslot][StudentGroup].append(lesson)
            else:
                lesson_map[timeslot][StudentGroup] = [lesson]
        else:
            lesson_map[timeslot] = {StudentGroup: [lesson]}

    print("|" + ("------------|" * (len(student_group_list) + 1)))
    print(reduce(lambda a, b: a + b + " | ",
                 map(lambda StudentGroup: "{:<10}".format(str(StudentGroup))[:10], student_group_list),
                 "|            | "))
    print("|" + ("------------|" * (len(student_group_list) + 1)))
    for timeslot in timetable.timeslot_list:
        cell_list = list(map(lambda the_StudentGroup: lesson_map.get(timeslot, {}).get(the_StudentGroup, []),
                             student_group_list))
        out = "| " + (timeslot.day_of_week[:3] + " " + str(timeslot.start_time))[:10] + " | "
        for cell in cell_list:
            if len(cell) == 0:
                out += "           | "
            else:
                out += "{:<10}".format(reduce(lambda a, b: a + "," + b,
                                              map(lambda assigned_lesson: assigned_lesson.subject,
                                                  cell)))[:10] + " | "
        print(out)
        out = "|            | "
        for cell in cell_list:
            if len(cell) == 0:
                out += "           | "
            else:
                out += "{:<10}".format(reduce(lambda a, b: a + "," + b,
                                              map(lambda assigned_lesson: assigned_lesson.teacher,
                                                  cell)))[0:10] + " | "
        print(out)
        out = "|            | "
        for cell in cell_list:
            if len(cell) == 0:
                out += "           | "
            else:
                out += "{:<10}".format(reduce(lambda a, b: a + "," + b,
                                              map(lambda assigned_lesson: assigned_lesson.room.name,
                                                  cell)))[:10] + " | "
        print(out)
        print("|" + ("------------|" * (len(student_group_list) + 1)))
    unassigned_lessons = list(
        filter(lambda unassigned_lesson: unassigned_lesson.timeslot is None or unassigned_lesson.room is None,
               lesson_list))

    if len(unassigned_lessons) > 0:
        print()

        print("Unassigned lessons")
        for lesson in unassigned_lessons:
            print(" " + lesson.subject + " - " + lesson.teacher + " - " + lesson.room.name)


solver_config = SolverConfig().withEntityClasses(Lesson) \
    .withSolutionClass(TimeTable) \
    .withConstraintProviderClass(define_constraints) \
    .withTerminationSpentLimit(Duration.ofSeconds(30))

solver = solver_factory_create(solver_config).buildSolver()

solution = solver.solve(generate_problem())

print_timetable(solution)


"""Student Grade Calculator

This program manages student records with three test scores,
loads and saves records to student_grades.txt, calculates averages and
letter grades, and displays classroom statistics.
"""

from __future__ import annotations
import os
import sys
import termios
import tty
from dataclasses import dataclass, field
from typing import Any

FILE_NAME = "student_grades.txt"


@dataclass
class Student:
    name: str
    student_id: str
    test1: float
    test2: float
    test3: float
    average: float = field(init=False)
    grade: str = field(init=False)

    def __post_init__(self) -> None:
        self.calculate_results()

    def calculate_results(self) -> None:
        self.average = round((self.test1 + self.test2 + self.test3) / 3, 2)
        self.grade = self.calculate_letter_grade(self.average)

    @staticmethod
    def calculate_letter_grade(average: float) -> str:
        if average >= 90:
            return "A"
        if average >= 80:
            return "B"
        if average >= 70:
            return "C"
        if average >= 60:
            return "D"
        return "F"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "id": self.student_id,
            "test1": f"{self.test1:.2f}",
            "test2": f"{self.test2:.2f}",
            "test3": f"{self.test3:.2f}",
            "average": f"{self.average:.2f}",
            "grade": self.grade,
        }

    @classmethod
    def from_dict(cls, row: dict[str, str]) -> Student | None:
        try:
            return cls(
                name=row.get("name", "").strip(),
                student_id=row.get("id", "").strip(),
                test1=float(row.get("test1", "0")),
                test2=float(row.get("test2", "0")),
                test3=float(row.get("test3", "0")),
            )
        except ValueError:
            return None


def get_float(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))
            if value < 0 or value > 100:
                raise ValueError("Score must be between 0 and 100.")
            return value
        except ValueError as exc:
            print(f"Invalid input: {exc}")


def read_student_records() -> list[Student]:
    records: list[Student] = []
    if not os.path.exists(FILE_NAME):
        return records

    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) != 7:
                    print(f"Skipping malformed record on line {line_number}.")
                    continue
                name, student_id, test1, test2, test3, _, _ = parts
                try:
                    student = Student(
                        name=name.strip(),
                        student_id=student_id.strip(),
                        test1=float(test1),
                        test2=float(test2),
                        test3=float(test3),
                    )
                    records.append(student)
                except ValueError:
                    print(f"Skipping invalid scores on line {line_number}.")
    except OSError as exc:
        print(f"Error reading {FILE_NAME}: {exc}")
    return records


def write_student_records(records: list[Student]) -> None:
    try:
        with open(FILE_NAME, "w", encoding="utf-8") as file:
            for record in records:
                file.write(
                    f"{record.name}|{record.student_id}|{record.test1:.2f}|{record.test2:.2f}|{record.test3:.2f}|{record.average:.2f}|{record.grade}\n"
                )
    except OSError as exc:
        print(f"Error writing {FILE_NAME}: {exc}")


def pause() -> None:
    input("\nPress Enter to continue...")


def add_student(records: list[Student]) -> None:
    print("\nAdd New Student")
    print("---------------")
    name = input("Student name: ").strip()
    student_id = input("Student ID: ").strip()
    test1 = get_float("Test 1 score (0-100): ")
    test2 = get_float("Test 2 score (0-100): ")
    test3 = get_float("Test 3 score (0-100): ")

    student = Student(name=name, student_id=student_id, test1=test1, test2=test2, test3=test3)
    records.append(student)
    print(f"\nAdded {student.name} with average {student.average:.2f} and grade {student.grade}.")
    write_student_records(records)
    pause()


def display_students(records: list[Student]) -> None:
    if not records:
        print("\nNo student records available.")
        pause()
        return

    print("\nStudent Records")
    print("---------------")
    header = f"{'Name':<20} {'ID':<10} {'Test1':>6} {'Test2':>6} {'Test3':>6} {'Avg':>6} {'Grade':>6}"
    print(header)
    print("-" * len(header))
    for record in records:
        print(
            f"{record.name:<20} {record.student_id:<10} "
            f"{record.test1:>6.2f} {record.test2:>6.2f} {record.test3:>6.2f} "
            f"{record.average:>6.2f} {record.grade:>6}"
        )
    pause()


def class_statistics(records: list[Student]) -> None:
    if not records:
        print("\nNo student records available for statistics.")
        pause()
        return

    averages = [record.average for record in records]
    highest = max(averages)
    lowest = min(averages)
    class_average = round(sum(averages) / len(averages), 2)
    highest_students = [r for r in records if r.average == highest]
    lowest_students = [r for r in records if r.average == lowest]

    print("\nClass Statistics")
    print("----------------")
    print(f"Highest average: {highest:.2f}")
    for student in highest_students:
        print(f"  - {student.name} ({student.student_id})")
    print(f"Lowest average:  {lowest:.2f}")
    for student in lowest_students:
        print(f"  - {student.name} ({student.student_id})")
    print(f"Class average:   {class_average:.2f}")
    pause()


def search_student(records: list[Student]) -> None:
    if not records:
        print("\nNo records available to search.")
        pause()
        return

    query = input("\nEnter the student name to search: ").strip().lower()
    matches = [r for r in records if query in r.name.lower()]

    if not matches:
        print(f"No students found matching '{query}'.")
        pause()
        return

    print("\nSearch Results")
    print("--------------")
    header = f"{'Name':<20} {'ID':<10} {'Average':>7} {'Grade':>6}"
    print(header)
    print("-" * len(header))
    for record in matches:
        print(
            f"{record.name:<20} {record.student_id:<10} "
            f"{record.average:>7.2f} {record.grade:>6}"
        )
    pause()


def get_single_key() -> str:
    if sys.platform.startswith("win"):
        try:
            import msvcrt

            key = msvcrt.getch()
            return key.decode("utf-8", errors="ignore")
        except Exception:
            return input().strip()

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key


def main_menu(records: list[Student]) -> None:
    while True:
        print("\nStudent Grade Calculator")
        print("------------------------")
        print("1. Add new student record")
        print("2. Display all students")
        print("3. Search for a student by name")
        print("4. Display class statistics")
        print("5. Save student records")
        print("Press ESC to exit")
        print("Choose an option: ", end="", flush=True)

        choice = get_single_key()
        print()  # Move to next line after selection

        if choice == "\x1b":
            print("Exiting and saving records...")
            write_student_records(records)
            break

        if choice == "1":
            add_student(records)
        elif choice == "2":
            display_students(records)
        elif choice == "3":
            search_student(records)
        elif choice == "4":
            class_statistics(records)
        elif choice == "5":
            write_student_records(records)
            print("Records saved.")
            pause()
        else:
            print("Invalid choice. Press ESC to exit or select 1-5.")


def main() -> None:
    records = read_student_records()
    if records:
        print(f"Loaded {len(records)} student record(s) from {FILE_NAME}.")
    else:
        print(f"No existing records found. Starting with an empty roster.")
    main_menu(records)


if __name__ == "__main__":
    main()

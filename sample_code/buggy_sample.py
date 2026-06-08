# ============================================================
# sample_code/buggy_sample.py
# ============================================================
# This file contains intentional bugs for testing CodePilot.
# Use it with any stage: python run.py will load this file.
#
# Bugs hidden in this file:
#   1. ZeroDivisionError  — calculate_average([])
#   2. IndexError         — get_first_element([])
#   3. TypeError          — process_score("abc")
#   4. Missing edge case  — no type validation anywhere
# ============================================================

def calculate_average(numbers):
    # BUG 1: no check for empty list → ZeroDivisionError
    total = 0
    for num in numbers:
        total = total + num
    average = total / len(numbers)   # crashes when numbers = []
    return average


def get_first_element(my_list):
    # BUG 2: no check for empty list → IndexError
    return my_list[0]   # crashes when my_list = []


def process_score(score):
    # BUG 3: no type check → TypeError if score is a string
    result = score * 2 + 10   # crashes when score = "abc"
    return result


def find_student(students, name):
    # BUG 4: returns None silently — caller won't know student not found
    for student in students:
        if student["name"] == name:
            return student
    # missing: should raise ValueError or return a clear signal


# ── Test calls that will trigger the bugs ────────────────────
if __name__ == "__main__":
    # This will work fine:
    print(calculate_average([85, 92, 78]))       # 85.0 — OK
    print(get_first_element([10, 20, 30]))        # 10 — OK
    print(process_score(90))                      # 190 — OK

    # These will crash — try them one at a time:
    # print(calculate_average([]))                # BUG 1
    # print(get_first_element([]))               # BUG 2
    # print(process_score("abc"))                # BUG 3

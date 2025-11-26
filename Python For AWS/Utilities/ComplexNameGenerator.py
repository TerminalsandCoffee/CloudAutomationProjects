import random
import string

def generate_unique_names():
    # List of departments that can use the name generator
    allowed_departments = ['Marketing', 'Accounting', 'FinOps']

    # Input name of department and validate if it's allowed to use the name generator
    dept_name = input("Enter the name of your department: ")
    if dept_name not in allowed_departments:
        print("Sorry, this department is not allowed to use this Name Generator.")
        return

    while True:
        try:
            num_of_instances = int(input("Hello, please enter the number of EC2 instances you want names for: "))
            break
        except ValueError:
            print("Sorry, the input must be a number. Please try again.")

    # Generate unique names for each instance
    for i in range(num_of_instances):
        #string of random numbers + letters
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

        #concatenate
        unique_name = dept_name + "-" + random_string
        print(unique_name)

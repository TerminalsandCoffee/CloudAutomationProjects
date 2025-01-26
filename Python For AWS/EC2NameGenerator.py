import random 
import string


#number of EC2 instances they want names for
while True:
    try:
        num_of_instances = int(input("Hello, please enter the number of EC2 instances you want names for: "))
        break
    except ValueError:
        print("Sorry, the input must be a number. Please try again.")

#input name of department
dept_name = input("Enter the name of your department: ")

for i in range(num_of_instances):
#string of random numbers + letters
  random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

#concatenate
  unique_name = dept_name + "-" + random_string
  print(unique_name)
  
  
"""
Week 12 fun
"""


#Create an empty list of services
services = []

#Populate the list using append
services.append('S3')
services.append('Lambda')
services.append('EC2')
services.append('DynamoDB')

#Using concataenation
#services = ['S3'] + ['Lambda'] + ['EC2'] + ['DynamoDB']

#Print the list and its length
print("List of services:", services)
print("Length of services list:", len(services), '\n')


#empty list of indexed services 
indexedServices = []

#Using index
indexedServices[0:0] = ['S3', 'Lambda', 'EC2', 'DynamoDB']

#Print the list and its length
print("List of services:", indexedServices)
print("Length of services list:", len(indexedServices),'\n')


#Remove two specific services from the list
services.remove('S3')

#pop is how we remove using an index.
services.pop(2)

# Print the new list and its length
print("New list of services:", services, '\n')
print("New length of services list:", len(services))
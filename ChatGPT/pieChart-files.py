import os
import matplotlib.pyplot as plt

# Get the current directory
dir_path = os.getcwd()

# Initialize a dictionary to store the file types and their sizes
file_sizes = {}

# Loop through all files in the directory
for file in os.listdir(dir_path):
    # Get the file extension
    file_ext = os.path.splitext(file)[1]
    # Get the file size in bytes
    file_size = os.path.getsize(os.path.join(dir_path, file))
    # Add the file size to the dictionary for the corresponding file type
    if file_ext in file_sizes:
        file_sizes[file_ext] += file_size
    else:
        file_sizes[file_ext] = file_size

# Create a pie chart of the file sizes
labels = file_sizes.keys()
sizes = file_sizes.values()
plt.pie(sizes, labels=labels, autopct='%1.1f%%')
plt.axis('equal')
plt.title('File Type Sizes in ' + dir_path)

# Show the pie chart
plt.show()

# Print the final result
print(file_sizes)
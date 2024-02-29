# Use an official Python runtime as a parent image
FROM python:3.11.7-slim-bullseye

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8501

# Run app.py when the container launches
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--client.showSidebarNavigation=False"]
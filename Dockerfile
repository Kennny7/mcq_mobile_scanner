FROM continuumio/miniconda3

# Copy environment definition
COPY environment.yml .

# Create the environment
# RUN conda env create -f environment.yml

COPY environment.yml .
RUN grep -v "win" environment.yml > environment.linux.yml \
 && conda env create -f environment.linux.yml

#COPY environment.linux.yml environment.yml
#RUN conda config --add channels conda-forge \
# && conda config --set channel_priority strict \
# && conda env create -f environment.yml

# Make sure the conda environment is used by default
SHELL ["conda", "run", "-n", "mcq_scanner", "/bin/bash", "-c"]

# Set working directory
WORKDIR /app
COPY . /app

# Expose port if your app serves something (optional)
# EXPOSE 8080

# Run your main app
CMD ["python", "main.py"]

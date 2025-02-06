# README.md

## Facial Similarity Survey Web Application

Welcome to the Facial Similarity Survey Web Application! This app allows users to evaluate facial similarity between pairs of individuals across a series of 60 comparisons. Each comparison represents a survey question designed to gather insightful data about facial recognition and subjective evaluations of similarity. After finishing the comparisons, users will provide feedback on their experience and receive a completion code to confirm their survey completion on Amazon Mechanical Turk (MTurk).

### Prerequisites

Before running the application, ensure you have the following:

- **Python 3.12.4**: Make sure you have Python installed. You can download it from the [official Python website](https://www.python.org/downloads/).

### Installation Instructions

Follow the instructions below to set up and run the application on your machine:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository
   ```

2. **Create a virtual environment**:
   Depending on your operating system, run the following command to create a virtual environment:

   - For **Windows**:

     ```bash
     python -m venv environment_name
     ```

   - For **macOS and Linux**:
     ```bash
     python3 -m venv environment_name
     ```

3. **Activate the virtual environment**:

   - For **Windows**:

     ```bash
     .\environment_name\Scripts\activate
     ```

   - For **macOS and Linux**:
     ```bash
     source environment_name/bin/activate
     ```

4. **Navigate to the source folder**:
   Change into the `src` directory where the application files are located:

   ```bash
   cd src
   ```

5. **Install the required packages**:
   Use pip to install the necessary dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. **Run the application**:
   To launch the app, use the following command:
   ```bash
   python app.py
   ```

### Usage

Once the application is running, you will be able to participate in the facial similarity survey. The interface will guide you through each comparison and feedback questions.

### Completion

After answering all survey questions and providing feedback, you will receive a completion code. Please ensure to save this code as it will confirm your survey completion on MTurk.

### Troubleshooting

If you encounter any issues during the installation or running the app, please check the following:

- Make sure Python and pip are correctly installed and added to your PATH.
- Ensure that you are in the correct directory when running commands.
- If you see any errors regarding missing packages, double-check that you have installed the requirements from `requirements.txt`.

### Support

For any further assistance, feel free to open an issue in the repository or contact the project maintainer.

---

Thank you for helping us evaluate facial similarity through your participation in this survey project!

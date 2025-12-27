
#  Analysis of Future Trends in Synchronized Hot and Dry Events

##  Project Overview
This notebook documents a computational analysis of climate change impacts, specifically focusing on the synchronization of **heatwaves** and **droughts** (compound events). Using multi-model climate data, we aim to quantify how the frequency and concurrence of these extreme events evolve under future emission scenarios (e.g., RCP 6.0) compared to a present baseline.


##  Scientific Leadership & Acknowledgments
**Principal Investigator & Data Acquisition: Dr. Cristina Deidda**

We explicitly designate the honors of this project to our coach **Dr. Cristina Deidda**. The scientific framework, rigorous data acquisition, and research methodology are the results of her extensive work in the field.

* **Role:** Dr. Deidda provided the pre-processed climate datasets, defined the physical parameters for extreme events, and established the scientific validity of the research questions.
* **Team Objective:** Our team was responsible for the **computational implementation**, translating Dr. Deidda’s research requirements into a functional Python workflow to visualize and quantify these trends.


##  Team Contributions & Workflow
This analysis is a collaborative effort, with specific computational tasks divided among team members:

* **Tasks 1 & 2 (Data Loading & Pre-processing):** Implemented by **Imdad Ullah**
    * *Setup of libraries and initial data ingestion.*

* **Tasks 3 & 4 (Individual Event Analysis):** Implemented by **Victor Carvajal**
    * *Analysis of isolated heatwave and drought metrics.*

* **Tasks 5 & 6 (Compound Event Definition & Mapping):** Implemented by **Siraj Ul Hasan Raja**
    * *Development of synchronization logic and spatial mapping of compound events.*

* **Tasks 7 & 8 (Statistical Analysis & Future Trends):** Implemented by **Imdad Ullah**
    * *Calculation of frequency ratios and visualization of future trends.*

* **Task 9 (Discussion & Interpretation):** Conducted by the **Whole Team**
    * *Synthesis of results and final conclusions.*

###  Graphical User Interface (GUI)
* **Development:** The interactive GUI was architected by **Siraj Ul Hasan Raja and Imdad Ullah** to enhance data exploration.
* **Implementation:** The code generation for the interface was executed with the assistance of **AI (Gemini)**, under strict instruction and design parameters.



##  How to Run This Project

### 1. Prerequisites
You need **Anaconda** or **Miniconda** installed on your system.


### 2. Environment Setup
To ensure compatibility and avoid version conflicts, please use the provided `environment_vis.yml` file included in this repository.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/sirajismail2001-sys/programing-project.git](https://github.com/sirajismail2001-sys/programing-project.git)
   cd programing-project

```

2. **Create the environment:**
```bash
conda env create -f environment_vis.yml

```


3. **Activate the environment:**
```bash
conda activate climate_project_env

```


*(Note: If the environment name differs, check the first line of the .yml file)*
4. **Launch the Notebook:**
```bash
jupyter notebook "programing_project_notebook-VIS (1).ipynb"

```



---

##  Technical Note

This project includes a custom **compatibility patch** in the first cell of the notebook. This automatically handles the deprecated `Int64Index` classes from older Pandas versions, allowing modern environments to read the legacy data files without errors.

```

```

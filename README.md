# Amanzi-ATS Transport Tutorial

This hands-on tutorial offers a hands-on experience in setting up and running transport simulations based on hydrology models in [Amanzi-ATS](https://github.com/amanzi/ats). This is part of the IDEAS-Watershed All-hands Meeting 2024 in Denver, CO.

**Facilitators:** Phong Le, Ethan Coon, Daniil Svyatsky

---

### 1. Learning Objectives
By the end of this workshop, participants will be able to:
* Understand core concepts of the [transport process kernel (PK)](https://github.com/amanzi/ats/tree/master/src/pk_transport) in Amanzi-ATS
* Develop workflows that integrate transport processes into [hydrology](https://amanzi.github.io/ats/stable/input_spec/process_kernels/physical/flow.html) models

---

### 2. Prerequisites
To get the most out of this tutorial, participants should have:
* Basic skills in Python and familiarity with [Jupyter Notebook](https://jupyter.org/). We will use [PyVista](https://pyvista.org/) for visualization.
* A fundamental understanding of watershed hydrology is encouraged.

---
### 3. Setup Instructions
1. **Pull the Docker Image:**
Make sure to pull the Docker container for this tutorial:
```bash
docker pull --platform linux/amd64 metsi/ideas-watersheds-all-hands-2024:v0
```

2. **Run the container:**
Start the container and open the Jupyter Notebook interface:
```bash
docker run --rm -it -p 8888:8888 metsi/ideas-watersheds-all-hands-2024:v0
```

3. **Access Jupyter Notebooks:**
Open the link displayed in your terminal to access Jupyter Notebook in your browser.

---

### 4. Workshop Outline
* **Introduction to ATS Hydrology and Transport:**  
Overview of fundamental equations in hydrology and transport in Amanzi-ATS

* **Hands-On Session: Building transport simulations:**
Step-by-step guidance on developing transport simulations in ATS based on the integrated hydrology model.

* **Discussion and Feedbacks** 
Open session for questions, insights, and feedback on the tutorial content.

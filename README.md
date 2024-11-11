# Amanzi-ATS Transport Tutorial

This tutorial offers a hands-on experience in setting up and running transport simulations based on hydrology models in [Amanzi-ATS](https://github.com/amanzi/ats). This is part of the [IDEAS-Watershed](https://ideas-watersheds.github.io/) all-hands meeting 2024 in Denver, CO.

**Instructors:** Phong Le, Ethan Coon, Daniil Svyatsky

---

### 1. Learning Objectives :dart:
By the end of this workshop, participants will be able to:
* Understand key concepts of the [transport process kernel (PK)](https://github.com/amanzi/ats/tree/master/src/pk_transport) in Amanzi-ATS;
* Develop workflows that couple transport PK with [hydrology PK](https://amanzi.github.io/ats/stable/input_spec/process_kernels/physical/flow.html).

---

### 2. Prerequisites :bulb:
To get the most out of this tutorial, participants should have:
* Basic skills in [python](https://www.python.org/) and [jupyter notebook](https://jupyter.org/). We will use [pyvista](https://pyvista.org/) and [ipywidgets](https://ipywidgets.readthedocs.io/) for interactive visualization.
* A fundamental understanding of watershed hydrology is encouraged.

---
### 3. Setup Instructions :wrench:
The slides for the tutorial can be found [here](./slides/slides.html).

The tutorial will be conducted in a `docker` container. The container includes the `terminal`, `text editor`, `ats`, `python`, `jupyter notebook`, and other dependencies. The `text editor` is customized to better work with the `ats` input files in `xml` format. Follow the steps below to set up the environment.
1. **Pull the `docker` image:**
Make sure to pull the Docker container for this tutorial:
```bash
docker pull --platform linux/amd64 metsi/ideas-watersheds-all-hands-2024:v0
```

2. **Run the container:**
Start the container and open the Jupyter Notebook interface:
```bash
docker run --rm -it -p 8888:8888 metsi/ideas-watersheds-all-hands-2024:v0
```

3. **Access Jupyter notebooks:**
Open the link displayed in your terminal to access `jupyter notebook` in your browser. 

4. **Clone the tutorial repository:**
Open a terminal in the Jupyter notebook interface and run:
```bash
git clone https://github.com/amanzi/ats-hands-on-transport.git
```

> [!IMPORTANT]
> If you're familiar with the `VSCode` editor, you can use the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension to connect to the container and edit XML files. You can also use the [jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) extension in `VSCode` to run notebooks directly within the Docker container.

---

### 4. Workshop Outline :memo:
* **Introduction to Hydrology and Transport PKs in ATS:**
   - Overview of governing equations
   
* **Hands-On Session: Building Transport Simulations:**
   - Step-by-step guidance on developing transport simulations in ATS based on the integrated hydrology model*

* **Discussion and Feedback:**
   - Open session for questions, insights, and feedback*

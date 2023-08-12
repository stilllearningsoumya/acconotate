# Acconotate
This is public code repository for the paper **Acconotate: Exploiting Acoustic Changes for Automatic Annotation of Inertial Data at the Source**, accepted in **IEEE DCOSS-IoT 2023**. The presentation slides and teaser for the project are available: [here](https://docs.google.com/presentation/d/1UUBJHT5jJccThNckkkOYgTZKo4d11a3WikLp2Y09kzk/edit?usp=sharing) and [here](https://youtu.be/XAEgkozGecA).

## Abstract

Smart infrastructures often intend to provide personalized context-aware services for their residents. These context-aware services, in turn, often rely on sophisticated machine learning algorithms which need vast volumes of costly annotated sensor data. State-of-the-art automated annotation frameworks try to solve this problem by generating annotated sensor data obtained from personal wearables. However, most of these approaches -- (a) either need visual data from the environment or (b) can only work for environments with a single resident. This paper discusses the design of a first-of-its-kind framework Acconotate which can automatically generate annotated data from dual resident smart environments without requiring any visual information. Acconotate achieves this by exploiting the typical transitions present in complex human activities first to solve the critical problem of the user-to-activity association and then use that to annotate the sensor stream available from both the users. Rigorous evaluation with two real-life datasets collected in two diverse scenarios shows that Acconotate can successfully generate annotated sensor data over the edge without human intervention.

## Software Requirements and Dependencies

To run and test Acconotate you would need MATLAB(R2017a) and `python` (3.9 or higher). The file `requirements.txt` provides the list of python dependencies required by this project. Additionally, Acconotate also utilizes a pre-trained audio-based activity recognition module for generating the annotations. This version of Acconotate currently uses the architecture and software pipeline defined in [Ubicoustics](https://github.com/FIGLAB/ubicoustics). Please refer to the original codebase of [Ubicoustics](https://github.com/FIGLAB/ubicoustics) for its license and software requirements.

## Running Acconotate

## Sample Dataset and Results

The purpose of this example is to explain the working principle of Acconotate, not exact reproduction of results. Exact details of the dataset used, virtual location of microphones, optimization settings, etc. may differ from the paper.

## Citations

If Acconotate and its setting are helpful in your research, please consider citing our paper:

```
@inproceedings{acconotate,
  author={Chatterjee, Soumyajit and Singh, Arun and Mitra, Bivas and Chakraborty, Sandip},
  booktitle={2023 19th International Conference on Distributed Computing in Smart Systems and the Internet of Things (DCOSS-IoT)}, 
  title={Acconotate: Exploiting Acoustic Changes for Automatic Annotation of Inertial Data}, 
  year={2023},,
  pages={25-33},
  doi={10.1109/DCOSS-IoT58021.2023.00013}}
```

## Correspondence
Please contact [Soumyajit Chatterjee](mailto:sjituit@gmail.com) for further questions or clarifications.
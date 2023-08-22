# ArtificialAMF
This repository accompanies the publication "On the Creation and Optical Microstructure Characterisation of Additively Manufactured Foam Structures (AMF)" and holds the source code for the artificial image generation pipeline for Additively Manufactured Foam Structures (AMF). It generates artificial images that correspond to microscope images of cutting planes through an AMF (2D images). You can adjust a lot of parameters for image generation and create a variety of AMF accordingly. 

A description of how the algorithm generates the images can be found in the publication (see Citation section).

## Citation
... To be done   

## Prerequesites
We recommend creating a virtual environment with your favourite tool, but you won't need a lot of special packages for this repo.
The basics with numpy, matplotlib and cv2 are sufficient. 

## Repo Organization
There are two folders in this repo:
- configs/ contains example config files that were generated while generating the images you'll find in the paper.
- src/ contains all source code as well as the examples folder where you'll find examples that show you how to generate images - from scratch and from a given config file. The examples folder has it's own ReadMe explaining the contained scripts and notebook.

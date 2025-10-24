# IACH_PROJECT
# Music Generation with RNN
### Authors:
- Alice Mangara
- Dinis Gonçalves
- Ivana Kuliš
  
This project uses a RNN model to generate new music sequences based on existing ones. It allows users to co-create music by adding or modifying generated bars.


* 1. Save this folder (we suggest to open it on Google Colab). Otherwise:

### Installation (Install them using pip)
* To run this project, you will need the following dependencies:
  - Python 3.7 or higher
  - TensorFlow 2.4.1 or higher
  - FluidSynth
  - PrettyMIDI
  - NumPy
  - Pandas
  - Collections
  - Glob
  - Pathlib

## Usage

This project is designed to generate new music sequences based on existing ones. It allows users to co-create music by adding or modifying generated bars.

### Prerequisites

Before you begin, ensure you have met the following requirements:

* You have installed Python 3.7 or higher.
* You have installed TensorFlow 2.4.1 or higher.
* You have installed FluidSynth.
* You have installed PrettyMIDI.
* You have installed NumPy, Pandas, Collections, Glob, and Pathlib.

### Running the Project

To run this project, follow these steps:

1. Clone the repository to your local machine.
2. Open the 'Final_script_HCAI' Jupyter notebook (!Google Colab):
     2a. Don't forget to change the directory from where you import the model in the Model Loading part.
4. You will be prompted to input parameters for the music generation. The output will be a new MIDI file that you can listen to and modify.

### Interacting with the Project

After running the project, you can interact with it in the following ways:

* You can choose to regenerate the last bar from scratch.
* You can choose to add a generated bar.
* You can choose to make changes to the generated bar.
* You can choose to finish the process.

Each of these options will prompt you to input parameters for the music generation. The output will be a new MIDI file that you can listen to and modify.

### Modifying the Generated Music

If you choose to make changes to the generated bar, you can download the generated MIDI file, make your changes, and upload the modified file. The project will then calculate the percentage of notes input by the user and the percentage of notes modified by the user.


** feel free to explore 'RNN_musicGenerator', the file we based on to create our approach ** : https://www.tensorflow.org/tutorials/audio/music_generation?hl=pt-br

* 3. Open the link in 'user_feedback.txt' file and provide some feedback.

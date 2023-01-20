# FuzzySystemCarla
## Tactical driving of vehicule using a fuzzy system to make decision

The project developed on the basis of fuzzy logic (Course SY10 at UTC) aims to test a fuzzy system in a simulated environment. The system will be in charge of making tactical decisions for driving a car with simplified manoeuvres such as: Accelerate, Decelerate, Change lane or Stay in lane.

The simulation environment used is CARLA, the fuzzy logic library used is Scikit-Fuzzy and the framework used for the generation of HMIs is Qt QML. 

The main architecture of the project is shown below:

![Schema](https://user-images.githubusercontent.com/49484735/213678372-ec6356c6-2e02-4659-bdd0-6cd7e7ecb927.png)

## Code explanation
The main program (main.py) is in charge of running the IHM application (MainApp.py). When the HMI is initialised, it in turn starts a parallel process which communicates with the Carla server (ThreadSimulation.py). This communication process is in charge of retrieving the data coming from the simulation environment, this data is evaluated by an object of the FuzzyCalculator class, this object gives as an output the manoeuvre, lateral or longitudinal, to be executed. 

In addition to this, there are 2 files (Fuzzy example) to understand how fuzzy systems are structured and what variables they take as input, it is sufficient to run them to obtain a graphical output of the system with predetermined inputs.

## UseCases

Different examples can be found in the next section:

Situation Without Traffic and High render quality

https://user-images.githubusercontent.com/49484735/212813746-c9806313-b49d-4e24-97d6-70d4bcbd709e.mp4

Situation With Traffic and Low render quality

https://user-images.githubusercontent.com/49484735/212821732-5e9881f6-693e-4ce0-8d39-d06caddb45da.mp4


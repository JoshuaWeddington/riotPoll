# Riot Poll - Data Collection/Machine Learning Project

Riot Poll is a way to collect data for a neural network that has been named "Hextech Augmented Network" to fit with the theme of what it does.

The idea was to delve into how RESTful APIs function to the end user, and set the groundwork for a free to use product that benefits from the data collected here.
Utilizing Python, data was collected from Riot Games' endpoints that provide data for the game League of Legends. 
This data is a collection of "game states" wherein each row of data is a particular minute from each match played.

While extracting the data from the JSON responses, it is organized in a way that is easy for a neural network to digest.
Due to rate limitations, it takes quite a long time to pull a significant amount of data.

Using SKLearn to create a dense neural network, the program is able to predict the winner of each game with around an 85% accuracy across all ranks of players.
One suggestion that I received was to train different models on each group of ranks for comparison of how each rank is able to be predicted accurately.
This portion of the network is currently in development, but the data polling is completely finished.

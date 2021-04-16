# audio-equalizer

**Introduction** : Sound equalizer is a basic tool in the music industry. It also serves in several biomedical applications like hearing aid industry.



**Description**: Based on your implementation of task 1, you need to develop the following:

Your application should be a multiple document one. Similar to MS Word or Excel, when you open a file, it opens in its own window or tab with all controlling UI showing up. If the user opens a second file, then the same interface (i.e. child window, or tab) should show up with its full UI controls.
Your old task window has the signal viewer and its spectrogram. Now, a new equalizer panel and a second signal viewer should be added to this window.
The two signal viewers should display the signal “before” and “after” the equalization actions. Note that the two viewers have to be exactly linked. i.e. they should always show the same exact part of the signal if the user scroll or zoom on any one of them.
The equalizer panel should contain 10 sliders, each control the gain of 1/10 of the bandwidth of the frequency domain. The default value of each slider is 1 (i.e. the corresponding BW of the signal remain as is) and can go up to 5 and drop down to 0.
Upon changing any equalizing slider, two things are expected to change:
The signal itself should change in the “After” viewer.
The spectrogram should also be updated to reflect the change.
To validate your work, each group should prepare a synthetic signal file. The signal is an artificial signal that you should prepare, and it is composed of a summation of several pure single frequencies. This should help in tracking what happens to each frequency when an equalizer action is taken. The decision of what are the frequencies to include and how many of them is left to the judgment and brainstorming of each group. Always remember that the main aim of this file is to validate if your equalizer is acting correctly or not.
To able to properly visualize the spectrogram, the user should be able to control:
Min and max values (i.e. the pixels intensity range) to plot through two sliders for the min value and one for the max. Each slider should goes from min and max values of the spectrogram.
The color palette that is used in the spectrogram through a combo-box/drop-menu that has 5 different palettes to use from.

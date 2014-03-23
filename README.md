OpenStat
========
###About
OpenStat is an exploratory statistical software meant as a replacement for Minitab. I wrote it for [Moody's Mega Math Challenge](http://m3challenge.siam.org), after they banned all non-free statistical software. There were a couple of free and open-source alternatives (e.g. SofaSTAT and PSPP), but they either didn't have all the functionality I needed or they were very buggy and hard to use.

###Features
* Basic statistical tests (e.g. t-tests and linear regression)
* Some very nice plots based on [Seaborn](http://stanford.edu/~mwaskom/software/seaborn/)

###To do list
* Add some real spreadsheet functionality (instead of just importing csv files)
* Expand IO to accomdate other file types
* Add some graph options so the user can add titles and labels
* Add more statistical tests, especially some nonparametric ones and logistic regression
* Add an IPython console for advanced users
* Allow custom Python functions to be optimized

###Dependencies
* [wxPython](http://wxpython.org/)
* [numpy](http://www.numpy.org/)
* [scipy](http://www.scipy.org/)
* [matplotlib](http://matplotlib.org/)
* [pandas](http://pandas.pydata.org/)
* [seaborn](http://stanford.edu/~mwaskom/software/seaborn/)
* [statsmodels](http://statsmodels.sourceforge.net/)

Forest colors

The reflectance spectra of the needles of young (less than 40 years old) individual
Scots pine and Norway spruce and the leaves of a birch. The data were collected in
Finland and Sweden. Spectroradiometric measurements were made in clear weather
during the growing season in June 1992. Each measurement represents the average
spectrum of thousands of leaves of a growing tree.

Measuring equipment: PR 713/702 AM spectroradiometer.

Wavelength interval: 390 nm - 850 nm.

Wavelength resolution: 5 nm.

File formats:  The available formats are ASCII and MATLAB(tm).

The file forest390_850_5.tar.gz includes three ASCII files which are named after
the forest type that the spectra are measured from. So there are files named
as spruce.dat, birch.dat and pine.dat. The spectra are measured from 390 to 850 nm
at 5 nm intervals so each spectrum can be considered as 93 dimensional vector at
which the first component corresponds the reflectance intensity at the wavelength
390 nm, the second at 395 nm and so on the last 93rd component corresponding the
reflectance intensity at the wavelength 850 nm. For example in the file spruce.dat
there are 349 spectra so there are 93*349 = 32457 values totally. The file birch.dat
has 337 spectra and the file pine.dat has 370 spectra stored in the same manner.

The file forest_matlab.tar.gz includes three MATLAB(tm) files which are named after
the forest type that the spectra are measured from. So there are files named
as spruce.mat, birch.mat and pine.mat. The file spruce.mat includes 93x349 matrix
where one column is 93 component spectrum. The file birch.mat includes 93x337
matrix and the file pine.mat 93x370 matrix in which the spectra are stored in the
same way.

Measurer: Ph.D. Raimo Silvennoinen, Vaisala Laboratory, University of Joensuu,
Finland.

Further information: haanpalo@lut.fi

References: 

   Jaaskelainen, T., Silvennoinen, R., Hiltunen, J. and Parkkinen, J. P. S.:
   ``Classification of the reflectance spectra of pine, spruce, and birch,'' Applied
   Optics, Vol. 33, No. 12, 20 April, 1994, pp. 2356-2362. 

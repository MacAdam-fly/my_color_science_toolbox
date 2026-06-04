Natural colors

The reflectance spectra of 218 coloured samples collected from the nature. Samples
include flowers and leaves and other colourful plants. Each spectrum consists of 61
elements that are raw data got from the output of the 12 bit A/D-converter of the
AOTF color measuring equipment. All the element values should be between 0 and 4096.
However there can exist some values which are larger than 4096. Those element values
should be corrected to the value 4096.

Measuring equipment: Acousto Optic Tunable Filter. (AOTF)

Wavelength interval: 400 nm - 700 nm.

Wavelength resolution: 5 nm.

File formats: The currently available format is ASCII.

The file natural400_700_5.asc.gz includes the natural spectra. Each spectrum consists
of two lines. The first line is the label of the spectrum and the second line is the
spectrum itself. The spectra are measured from 400 to 700 nm at 5 nm intervals so each
spectrum can be considered as 61 dimensional vector at which the first component
corresponds the reflectance intensity at the wavelength 400 nm, the second at 405 nm
and so on the last 61th component corresponding the reflectance intensity at the
wavelength 700 nm.

Measurer: Esa Koivisto, Department of Physics, University of Kuopio, Finland

Further information: haanpalo@lut.fi

References: 

   Parkkinen, J., Jaaskelainen, T. and Kuittinen, M.: ``Spectral representation of
   color images,'' IEEE 9th International Conference on Pattern Recognition,
   Rome, Italy, 14-17 November, 1988, Vol. 2, pp. 933-935. 

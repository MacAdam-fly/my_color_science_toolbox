The AgfaReference

The Agfa ColorReference is designed according to the IT8.7 standard.The
standard defines the layout and colorimetric values of an input test target
that allows any color scanner to be calibrated with any photographic medium
dye set. The IT8 target was designed by the ANSI IT8 subcommittee to be 
used for both calibration by visual comparison and as a numerical data target.

Each ColorReference consist of 288 patches, and has been designed to represent
the color space from full saturation to near neutrals at highlight, midtone, and
shadows.Hues falling at regular intervals through the color space represent a
full spectrum gamut. A linear perception neutral density scale, and CMY and RGB
color dye scales provide basic reference points to check for gray balance, tone
reproduction, and color correction. Finally, a vendor-optional area containing
flesh colors based on the colorimetric measurements of various skin tones plus
the colors of nature completes the ColorReference.

The spectral reflectance of samples were measured with Minolta spectro-
photometer with option SCE (Specular component excluded). The CM-2002
utilizes d/8 (diffuse illumination/8o viewing) geometry which conforms to
ISO and DIN standards (and also to CIE d/0 recommendations).

Measuring equipment: Minolta spectrofotometer CM-2002.

Wavelength interval: 400 nm - 700 nm.

Wavelength resolution: 10 nm.

File formats:  The available formats are ASCII and MATLAB.

   ASCII-file: agfait872.dat

      Order of samples (264 samples, numbered 1-264):

      A1, A2, ..., A22,
      B1, B2, ..., B22,
      ...
      L1, L2, ..., L22;

      Neutral scale samples (22 samples, numbered 265-286)

      1, 2, ..., 22;

      Black sample  number 287;
      White sample  number 288;
      Minolta white calibration sample  number 289.

      The color co-ordinates of the samples are stored in the same file.

   MATLAB-file: agfait872.mat

      Order of samples (264 samples, columns 1-264):

      A1, A2, ..., A22,
      B1, B2, ..., B22,
      ...
      L1, L2, ..., L22;

      Neutral scale samples (22 samples, columns 265-286)

      1, 2, ..., 22;

      Black sample  column 287;
      White sample  column 288;
      Minolta white calibration sample  column 289.

Measurer: ela@ee.oulu.fi (University of Oulu, Electrical Eng.Dept)

Further information: ela@ee.oulu.fi (University of Oulu, Electrical Eng.Dept)

References: 

   AgfaFotoreference, Trademark of Agfa-Gevaert A.G.,
   Septestraat 27 2640 Mortsel - Belgium,1992. 


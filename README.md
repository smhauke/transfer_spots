This script can be used to copy the location of spots from one Imaris image to another. They will retain their size, but data contained in the spots (i.e. intensity data) will not be copied. This script should work on 4D images, although I've only used it on static 3D images (z-stacks from a confocal).

Requires:
- Imaris v9.0.1 (may work with other versions as well)
- MATLAB 2014 (likely works with all versions of MATLAB)
- Imaris MATLAB XTensions enabled

An Obnoxiously Detailed Explanation of How to Use transfer_spots:
1) Download the .m file located in this repository. Find it in File Explorer and open it in MATLAB.
2) Locate the tab labeled “transfer_spots” (title of a tab within the central Editor window) in MATLAB.
3) Open the Imaris application, so that MATLAB can “see” it.
4) With the script up, click the “Run” button in MATLAB (Home tab -> green triangle button).
5) Within the MATLAB command window, you should see the following prompt: "Within Imaris, please open the image with spots you would like to transfer, then press Enter..." Follow these instructions. Open your image in Imaris, then return to the MATLAB command window and press Enter.
Now you should see this message: "Now switch to the image you would like to transfer spots to, then press Enter..." Follow these instructions with the image you would like to transfer spots to.  
6) Now you should see some messages about what the code is doing as well as: 'Target image has ' # ' time points (0 to #) ' . Make sure this is the correct number of time points (only 1 for a static image). The final message should be “Spots successfully transferred!”, and you should be able to see the new spots in Imaris.
7) If this script doesn't work for some reason and you need help troubleshooting, email me (smhauke@uab.edu).

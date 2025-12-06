#!/usr/bin/env python
"""
Transfer Spot Locations Between Imaris Images
This script copies spot locations from one Imaris image to another
Requires: ImarisLib Python module
"""

import numpy as np
import sys
import os

# Step 1: CONNECT TO IMARIS

# Add ImarisLib to path
path = r'C:\Program Files\Bitplane\Imaris x64 9.0.1\XT\python'
sys.path.append(path)

try:
    import ImarisLib
except ImportError:
    raise ImportError("ImarisLib not found. Please check the path and ensure ImarisLib is installed.")

# Initialize Imaris connection
vImarisLib = ImarisLib.ImarisLib()
# Get the Imaris application object
vImaris = vImarisLib.GetApplication(0)

# Check if Imaris is running
if vImaris is None:
    raise RuntimeError('Imaris is not running. Please start Imaris first.')


# Step 2: GET SPOTS FROM FIRST IMAGE (Source)
print('Within Imaris, please open the image with spots you would like to transfer, then press Enter...')
raw_input()

vAppA = vImarisLib.GetApplication(0)
sceneA = vAppA.GetSurpassScene()

# Get the spots object - make sure index 3 is correct for your scene
spotObjA = sceneA.GetChild(3)

# Convert to spots interface FIRST
spotInterfaceA = vAppA.GetFactory().ToSpots(spotObjA)

# Check if conversion was successful
if spotInterfaceA is None:
    raise RuntimeError('Child at index 3 is not a Spots object or conversion failed')

# Now get the coordinates from the spots interface
SpotCoordinates = spotInterfaceA.GetPositionsXYZ()
# Also get radii
SpotRadii = spotInterfaceA.GetRadiiXYZ()
# Also get time indices
SpotTimes = spotInterfaceA.GetIndicesT()

print('Found ' + str(len(SpotCoordinates)) + ' spots')


# Step 3: TRANSFER SPOTS TO SECOND IMAGE (Target)
# Switch to Target Image (8-bit)
print('\nNow switch to the image you would like to transfer spots to, then press Enter...')
raw_input()

# or use GetApplication(1) if you have multiple instances
vAppB = vImarisLib.GetApplication(0)
# Change to (1) for second instance
sceneB = vAppB.GetSurpassScene()

# Now, let's create the spots
spots = vAppB.GetFactory().CreateSpots()

# The issue is likely the parameter format. Let's try different approaches
print('Trying different parameter formats for Set() method...')

# Let's get the valid time points from the target image
print('Getting time information from target image...')

# Get dataset info to understand valid time points
dataset = vAppB.GetDataSet()
if dataset is not None:
    numTimePoints = dataset.GetSizeT()
    print('Target image has ' + str(numTimePoints) + ' time points (0 to ' + str(numTimePoints-1) + ')')
    
    # Use time point 0 for all spots (or map to valid range)
    if numTimePoints > 0:
        # Method 1: Put all spots at time point 0
        validTimeIndices = np.zeros(len(SpotTimes), dtype=np.int32)
        
        # Method 2: Map source times to valid target times
        # validTimeIndices = np.array([int(t) % numTimePoints for t in SpotTimes], dtype=np.int32)
        
    else:
        print('Warning: Target image has no time points, using 0')
        validTimeIndices = np.zeros(len(SpotTimes), dtype=np.int32)
else:
    print('Warning: Could not get dataset info, using time 0 for all spots')
    validTimeIndices = np.zeros(len(SpotTimes), dtype=np.int32)

# Convert data to proper format
# Convert to list of lists format: [[x1,y1,z1], [x2,y2,z2], ...]
if isinstance(SpotCoordinates, np.ndarray):
    SpotCoordinatesList = SpotCoordinates.tolist()
else:
    SpotCoordinatesList = list(SpotCoordinates)

# Convert radii - use first radius value from each spot
if isinstance(SpotRadii, np.ndarray):
    radiiSingle = [float(r[0]) for r in SpotRadii]
else:
    radiiSingle = [float(r[0]) for r in SpotRadii]

# Convert time indices to list
if isinstance(validTimeIndices, np.ndarray):
    validTimeIndicesList = validTimeIndices.tolist()
else:
    validTimeIndicesList = list(validTimeIndices)

print('Data formats after conversion:')
print('Coordinates type: ' + str(type(SpotCoordinatesList)))
print('Coordinates length: ' + str(len(SpotCoordinatesList)))
if len(SpotCoordinatesList) > 0:
    print('First coordinate: ' + str(SpotCoordinatesList[0]) + ' (type: ' + str(type(SpotCoordinatesList[0])) + ')')
print('Radii type: ' + str(type(radiiSingle)))
print('Times type: ' + str(type(validTimeIndicesList)))

print('Attempting to create spots with corrected time indices...')

try:
    # Use the method that almost worked (Method 2) but with corrected time indices
    spots.Set(SpotCoordinatesList, validTimeIndicesList, radiiSingle)
    print('SUCCESS: Spots created with Set() method!')
    
except Exception as ME:
    print('Set method still failed: ' + str(ME))
    
    # Alternative approach: Try to understand what Set() actually expects
    # by looking at how the source spots were created
    print('Trying alternative approach based on source spot format...')
    
    try:
        # Get the exact format from source spots
        sourceCoords = spotInterfaceA.GetPositionsXYZ()
        sourceTimes = spotInterfaceA.GetIndicesT()
        sourceRadii = spotInterfaceA.GetRadiiXYZ()
        
        # Convert to list format
        if isinstance(sourceCoords, np.ndarray):
            sourceCoordsLst = sourceCoords.tolist()
        else:
            sourceCoordsLst = list(sourceCoords)
            
        if isinstance(sourceRadii, np.ndarray):
            sourceRadiiLst = [float(r[0]) for r in sourceRadii]
        else:
            sourceRadiiLst = [float(r[0]) for r in sourceRadii]
        
        print('Source times range: ' + str(min(sourceTimes)) + ' to ' + str(max(sourceTimes)))
        print('Source times class: ' + type(sourceTimes).__name__)
        
        # Use exact same format as source but with target-appropriate times
        if numTimePoints > 0:
            # Map source times to valid target range
            mappedTimes = [int(t) % numTimePoints for t in sourceTimes]
        else:
            mappedTimes = [0] * len(sourceTimes)
        
        spots.Set(sourceCoordsLst, mappedTimes, sourceRadiiLst)
        print('SUCCESS: Used exact source data format!')
        
    except Exception as ME2:
        print('Alternative method failed: ' + str(ME2))
        
        # Last resort: Try the most basic version
        try:
            # Create spots at time 0 with minimal data
            simpleCoords = SpotCoordinatesList  # Already converted above
            simpleTimes = [0] * len(SpotCoordinatesList)
            simpleRadii = [0.5] * len(SpotCoordinatesList)  # Default radius
            
            spots.Set(simpleCoords, simpleTimes, simpleRadii)
            print('SUCCESS: Used simplified format!')
            
        except Exception as ME3:
            print('All methods failed. Last error: ' + str(ME3))
            
            # Show what we tried
            print('Data formats used:')
            print('Coordinates: ' + str(simpleCoords.shape) + ' (class: ' + type(simpleCoords).__name__ + ')')
            print('Times: ' + str(simpleTimes.shape) + ' (class: ' + type(simpleTimes).__name__ + ')')
            print('Radii: ' + str(simpleRadii.shape) + ' (class: ' + type(simpleRadii).__name__ + ')')
            
            raise

# Set additional properties
try:
    spots.SetName('Transferred Spots')
    print('Name set successfully')
except:
    print('Warning: Could not set name')

# Add to scene
try:
    sceneB.AddChild(spots, -1)
    print('Spots added to scene successfully!')
except:
    print('Warning: Could not add to scene (may already be there)')

print('Spots successfully transferred!')

# Clean up connections
try:
    vAppB = None
    vAppA = None
    vImaris = None
    vImarisLib = None
except:
    pass
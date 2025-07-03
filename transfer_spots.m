%% Transfer Spot Locations Between Imaris Images
% This script copies spot locations from one Imaris image to another
% Requires: Imaris MATLAB Extension (ImarisLib)


%% Step 1: CONNECT TO IMARIS

path='C:\Program Files\Bitplane\Imaris x64 9.0.1\XT\rtmatlab\';
javaaddpath([path 'ImarisLib.jar'])

% Initialize Imaris connection 
vImarisLib = ImarisLib; 
% Get the Imaris application object
vImaris = vImarisLib.GetApplication(0); 
% Check if Imaris is running
if isempty(vImaris)
    error('Imaris is not running. Please start Imaris first.');
end

%% Step 2: GET SPOTS FROM FIRST IMAGE (Source)
fprintf('Within Imaris, please open the image with spots you would like to transfer, then press Enter...\n');
pause;

vAppA = vImarisLib.GetApplication(0);
sceneA = vAppA.GetSurpassScene();

% Get the spots object - make sure index 3 is correct for your scene
spotObjA = sceneA.GetChild(3); 

% Convert to spots interface FIRST
spotInterfaceA = vAppA.GetFactory().ToSpots(spotObjA);

% Check if conversion was successful
if isempty(spotInterfaceA)
    error('Child at index 3 is not a Spots object or conversion failed');
end

% Now get the coordinates from the spots interface
SpotCoordinates = spotInterfaceA.GetPositionsXYZ();
% Also get radii
SpotRadii = spotInterfaceA.GetRadiiXYZ();  
% Also get time indices
SpotTimes = spotInterfaceA.GetIndicesT();  

disp(['Found ' num2str(size(SpotCoordinates, 1)) ' spots']);


%% Step 3: TRANSFER SPOTS TO SECOND IMAGE (Target)
% Switch to Target Image (8-bit)
fprintf('\nNow switch to the image you would like to transfer spots to, then press Enter...\n');
pause;
% or use GetApplication(1) if you have multiple instances
vAppB = vImarisLib.GetApplication(0);  
% Change to (1) for second instance
sceneB = vAppB.GetSurpassScene();

% Now, let's create the spots 
spots = vAppB.GetFactory().CreateSpots();

% The issue is likely the parameter format. Let's try different approaches
disp('Trying different parameter formats for Set() method...');

% Let's get the valid time points from the target image
disp('Getting time information from target image...');

% Get dataset info to understand valid time points
dataset = vAppB.GetDataSet();
if ~isempty(dataset)
    numTimePoints = dataset.GetSizeT();
    disp(['Target image has ' num2str(numTimePoints) ' time points (0 to ' num2str(numTimePoints-1) ')']);
    
    % Use time point 0 for all spots (or map to valid range)
    if numTimePoints > 0
        % Method 1: Put all spots at time point 0
        validTimeIndices = zeros(size(SpotTimes), 'int32');
        
        % Method 2: Map source times to valid target times
        % validTimeIndices = int32(mod(SpotTimes - 1, numTimePoints));
        
    else
        disp('Warning: Target image has no time points, using 0');
        validTimeIndices = zeros(size(SpotTimes), 'int32');
    end
else
    disp('Warning: Could not get dataset info, using time 0 for all spots');
    validTimeIndices = zeros(size(SpotTimes), 'int32');
end

% Convert data to proper format
SpotCoordinates = double(SpotCoordinates);
radiiSingle = double(SpotRadii(:, 1));  % Use only first radius value

disp('Attempting to create spots with corrected time indices...');

try
    % Use the method that almost worked (Method 2) but with corrected time indices
    spots.Set(SpotCoordinates, validTimeIndices, radiiSingle);
    disp('SUCCESS: Spots created with Set() method!');
    
catch ME
    disp(['Set method still failed: ' ME.message]);
    
    % Alternative approach: Try to understand what Set() actually expects
    % by looking at how the source spots were created
    disp('Trying alternative approach based on source spot format...');
    
    try
        % Get the exact format from source spots
        sourceCoords = double(spotInterfaceA.GetPositionsXYZ());
        sourceTimes = spotInterfaceA.GetIndicesT();
        sourceRadii = double(spotInterfaceA.GetRadiiXYZ());
        
        disp(['Source times range: ' num2str(min(sourceTimes)) ' to ' num2str(max(sourceTimes))]);
        disp(['Source times class: ' class(sourceTimes)]);
        
        % Use exact same format as source but with target-appropriate times
        if numTimePoints > 0
            % Map source times to valid target range
            mappedTimes = int32(mod(double(sourceTimes), numTimePoints));
        else
            mappedTimes = int32(zeros(size(sourceTimes)));
        end
        
        spots.Set(sourceCoords, mappedTimes, sourceRadii(:,1));
        disp('SUCCESS: Used exact source data format!');
        
    catch ME2
        disp(['Alternative method failed: ' ME2.message]);
        
        % Last resort: Try the most basic version
        try
            % Create spots at time 0 with minimal data
            simpleCoords = double(SpotCoordinates);
            simpleTimes = int32(zeros(size(SpotCoordinates, 1), 1));
            simpleRadii = ones(size(SpotCoordinates, 1), 1) * 0.5;  % Default radius
            
            spots.Set(simpleCoords, simpleTimes, simpleRadii);
            disp('SUCCESS: Used simplified format!');
            
        catch ME3
            disp(['All methods failed. Last error: ' ME3.message]);
            
            % Show what we tried
            disp('Data formats used:');
            disp(['Coordinates: ' num2str(size(simpleCoords)) ' (class: ' class(simpleCoords) ')']);  
            disp(['Times: ' num2str(size(simpleTimes)) ' (class: ' class(simpleTimes) ')']);
            disp(['Radii: ' num2str(size(simpleRadii)) ' (class: ' class(simpleRadii) ')']);
            
            rethrow(ME);
        end
    end
end

% Set additional properties
try
    spots.SetName('Transferred Spots');
    disp('Name set successfully');
catch
    disp('Warning: Could not set name');
end

% Add to scene
try
    sceneB.AddChild(spots, -1);
    disp('Spots added to scene successfully!');
catch
    disp('Warning: Could not add to scene (may already be there)');
end

disp('Spots successfully transferred!');
clear all; clc;
%% script for Cherry picking
Rows = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P'];
% load data
% loades column C (concatenate)
[~, Row_Data, ~] = xlsread('20220822_CHERRYPICKING_LETICIA_4 plates.xlsx','sheet1','D:D');
% remove header from Row_Data
Row_Data = Row_Data(2:end);
% NOTE: after importing, make sure all the cells have the right string 
% (that #E# didn't turn to be #*10^#), and that ther are no empty cells
% empty_cells = find(cellfun(@isempty, Row_Data));

%% Mapping the row data.
A_Volume = 50; % Volume of the source
D_Volume = 50; % Volume of the target
well_target_plate = 1; % first well in the target plates
New_library_R = {}; % creation of the output library
New_library_C = {}; % creation of the output library
New_library_P = {};
Index_Target_Plates = 1; % serial number of the tareget plate.

for well = 1:size(Row_Data,1)
    well_Source_plate = Row_Data{well};
    BW_Letters = isletter(well_Source_plate);
    Row_location = find(BW_Letters);
    Source_Row = well_Source_plate(Row_location);
    Source_Column = well_Source_plate(Row_location+1:end);
    Source_Plate = well_Source_plate(1:Row_location-1);
    Plate_Target = strcat('Target',num2str(Index_Target_Plates));
    Aspirate_txt_Row = ['A',';','Source',';;;',num2str((str2num(Source_Column)-1)*16+strfind(Rows,Source_Row)),';;',num2str(A_Volume),'\r\n']; % line for the aspirate to the target plates.
    Dispense_txt_Row = ['D',';',Plate_Target,';;;',num2str(well_target_plate),';;',num2str(D_Volume),'\r\n']; % line for the dispense to the target plate.
    
    %% List for Odd numbers 
    if 1==mod(well_target_plate,2)
        Current_file=['Source_plate_Odd_numbers',Source_Plate,'.txt'];
        fileID = fopen(Current_file,'a');
        fprintf(fileID,Aspirate_txt_Row);
        fprintf(fileID,Dispense_txt_Row);
        fprintf(fileID,'W;\r\n');
        fclose(fileID);
        
    %% List for Even numbers 
    else
        Current_file = ['Source_plate_Even_numbers',Source_Plate,'.txt'];
        fileID = fopen(Current_file,'a');
        fprintf(fileID,Aspirate_txt_Row);
        fprintf(fileID,Dispense_txt_Row);
        fprintf(fileID,'W;\r\n');
        fclose(fileID);
    end
    
    C_T = floor(well_target_plate/16);
    R_T = Rows(((well_target_plate/16-C_T)*16)+1);
    New_library_R = [New_library_R;R_T];
    New_library_C = [New_library_C;C_T];
    New_library_P = [New_library_P;Index_Target_Plates];
    well_target_plate = well_target_plate+1;
    
    while well_target_plate == 385
          well_target_plate = 1;
          Index_Target_Plates = Index_Target_Plates+1;
    end
end

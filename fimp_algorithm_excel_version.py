from pathlib import Path
import pandas as pd
import numpy as np

# Hold on to this Excel code
# =IF(OR(I2="C", I2="I", I2="P", I2="P", I2="W"), "raised", "slab")

###############################################################################
# Variables for the user to change

# Change the folder and the file path to your file
USER_FOLDER_PATH = r'C:/Users/e3plfmen/Downloads/Nonstructural for Jack'
USER_FILE_NAME = 'Cranford_py123024.xlsx'

# Change the values on the right hand side to match your basement strings
BASEMENT_TYPE = {
    'slab': 'No Basement/Slab on-grade',
    'subgrade': 'Subgrade Basement',
    'raised': 'Raised/Crawlspace',
    'walkout': 'Walkout Basement',
    'ranches': 'Bi-Levels and Raised Ranches',
    'split': 'Split Levels'
}

# Change the values on the right hand side to match your damage types
DAMAGE_CATEGORY = {
    'COM' : ['NonResidential'],
    'RES': ['RES']
}
NONSTRUCTURAL_PARAMETERS = {
    'damage_category': 'Damage Category',
    'building_construction_type': 'Construction Type',
    'square_footage': 'MFsqFt',
    'flood_level': 'WaterElevation_10Year',
    'main_floor': 'Main Floor Elev',
    'protection_level': 'DesignWaterElevation',
    'ground': 'groundelev_2016_atpoint_ft',
    'basement': 'basement_type',
    }

###############################################################################



###############################################################################
# CONSTANTS
MAX_SIZE = 2000
WOOD_CONSTRUCTION = 'W'
MASONRY_CONSTRUCTION = 'M'

BASEMENT_CODES = {
        '0': BASEMENT_TYPE['slab'],
        '1S': BASEMENT_TYPE['subgrade'],
        '1W': BASEMENT_TYPE['subgrade'],
        '2': BASEMENT_TYPE['raised'],
        '3': BASEMENT_TYPE['subgrade']
    }

USAGE_CODES = {
        12: 'Multi-Family',
        13: 'Garden Apts',
        14: 'High Rise Apts',
        15: 'Townhouses'
    }

# TODO: create a prefined list of results
TREATMENT_RESULTS = {
    'residential': {
        'slab': {
            'sealant_closures': 'Sealant & Closures',
            'raise': 'Raise',
            'raise_ac': 'Raise AC',
        },
        'subgrade': {
            'raise': 'Raise',
            'fill': 'Fill Basement + Utility Room'
        },
        'raised': {
            'raise': 'Raise',
            'raise_lovers': 'Raise AC + Louvers'
        },
        'walkout': {
            'raise': 'Raise',
            'interior': 'Interior Floodwall',
            'lower_floor': 'Raise Lower Floor + Space'
        },
        'ranches': {
            'raise': 'Raise',
            'sealant_closures': 'Sealant & Closures',
            'lower_floor': 'Raise Lower Floor + Space'
        },
        'split': {
            'raise': 'Raise',
            'sealant_closures': 'Sealant & Closures',
        },
        'larger_residential': {
            'ringwall': 'Ringwall',
            'raise': 'Raise',
            'protect': 'Protect Utilities',
            'sealant_closures': 'Sealant & Closures',
        }
    },
    'non_residential_wood': {
        'raised': {
            'raise': 'Raise',
            'protect': 'Protect Utilities + Louvers',
        },
        'slab': {
            'sealant_closures': 'Sealant & Closures',
            'raise': 'Raise',
            'protect': 'Protect Utilities',
        },
        'subgrade': {
            'raise': 'Raise',
            'fill': 'Fill Basement + Utility Area'
        },
        'walkout': {
            'raise': 'Raise',
            'interior': 'Interior Floodwall',
            'lower_floor': 'Raise Lower Floor + Space'
        }
    },
    'non_residential_masonry': {
        'ringwall': 'Ringwall',
        'sealant_closures': 'Sealant & Closures',
        'protect': 'Protect Utilities',
    }
}

###############################################################################



###############################################################################
# Helper functions

# The message that is returned
# Returns a string to the row that is be calculated
def treatment(message):
    return str(message)

#Helper functions
# 1.) treatment
# 2.) flood_greater_main
# 3.) protection_ground_greater
# 4.) protection_greater_main
# 5.) main_floor_calculation

# The functions to determine the if the measures match a condition

# Compares the flood level to the main floor
# Checks the flood level to the main floor
def flood_greater_main(flood_level, main_floor):
    return flood_level >= main_floor

# Checks the protection level to the ground and determine the 'freeboard'
# If the difference of the protection level between the ground is greater then 3 -> return True
def protection_ground_greater(protection_level, ground):
    return (protection_level - ground) >= 3

# Checks the protection level to the main floor
def protection_greater_main(protection_level, main_floor):
    return protection_level >= main_floor

# Calculates the main floor based on the ground, number of steps and the height of the steps
# Because the step height measured in inches and everything else is measured in feet
# need to change from inches to feet
def main_floor_calculation(number_of_steps, ground, step_height=8):
    # return (ground + (number_of_steps / 12 * step_height))
    return number_of_steps

###############################################################################


###############################################################################
# Code that implements the flowchart and algorithm

# Follows the AECOM flowchart and algorithm
# Follows the 7 nodes in the residential portion of the flowchart

class ResidentialClass:

    # Checks for 'Slab on Grade' type basement, follows the below path
    # I.) Flood level >= Main floor
    #   1.) Protection level < Ground 
    #   2.) Protection level >= Ground
    # II.) Flood level < Main floor
    #   1.) Protection level < Main floor
    #   2.) Protection level >= Main floor
    #       A.) Protection level < Ground
    #       B.) Protection level >= Ground
    @classmethod
    def __no_basement_slab(cls, flood_level, main_floor, protection_level, ground, basement):
        if flood_greater_main(flood_level, main_floor):
            if not protection_ground_greater(protection_level, ground):
                return treatment('Sealant and Closures')
            elif protection_ground_greater(protection_level, ground):
                return treatment('Raise')
        elif not flood_greater_main(flood_level, main_floor):
            if not protection_greater_main(protection_level, main_floor):
                return treatment('Raise AC')
            elif protection_greater_main(protection_level, main_floor):
                if not protection_ground_greater(protection_level, ground):
                    return treatment('Sealant and Closures')
                elif protection_ground_greater(protection_level, ground):
                    return treatment('Raise')

    # Checks for 'Subgrade Basement', follows the below path
    # I.) Flood level >= Main floor
    # II.) Flood level < Main floor
    #   1.) Protection level < Main floor
    #   2.) Protection >= Main floor
    @classmethod
    def __subgrade_basement(cls, flood_level, main_floor, protection_level, basement):
        if flood_greater_main(flood_level, main_floor):
            return treatment('Raise')
        elif not flood_greater_main(flood_level, main_floor):
            if not protection_greater_main(protection_level, main_floor):
                return treatment('Fill Basement + Utility Room')
            elif protection_greater_main(protection_level, main_floor):
                return treatment('Raise')

    # Checks for 'Crawlspace', follows the below path
    # I.) Flood level >= Main floor
    # II.) Flood level < Main floor
    #   1.) Protection level < Main floor
    #   2.) Protection level >= Main floor
    @classmethod
    def __raised_crawlspace(cls, flood_level, main_floor, protection_level, basement):
        if flood_greater_main(flood_level, main_floor):
            return treatment('Raise')
        elif not flood_greater_main(flood_level, main_floor):
            if not protection_greater_main(protection_level, main_floor):
                return treatment('Raise AC + Louvers')
            elif protection_greater_main(protection_level, main_floor):
                return treatment('Raise')

    # Checks for 'Walkout Basement', follows the below path
    # I.) Flood level >= Main floor
    # II.) Flood level < Main floor
    #   1.) Protection level < Main floor
    #       A.) Protection - Ground < 3
    #       B.) Protection - Ground >= 3
    #   2.) Protection level >= Main floor
    @classmethod
    def __walkout_basement(cls, flood_level, main_floor, protection_level, ground, basement):
        if flood_greater_main(flood_level, main_floor):
            return treatment('Raise')
        elif not flood_greater_main(flood_level, main_floor):
            if not protection_greater_main(protection_level, main_floor):
                if not protection_ground_greater(protection_level, ground):
                    return treatment('Interior Floodwall')
                elif protection_ground_greater(protection_level, ground):
                    return treatment('Raise Lower Floor + space')
            elif protection_greater_main(protection_level, main_floor):
                return treatment('Raise')

    # Checks for one of two basements:
    # 1.) 'Bi-Level'
    # 2.) 'Raised Ranches'
    # I.) Flood level >= Main floor
    # II.) Flood level < Main floor
    #   1.) Protection level < Main floor
    #       A.) Protection level - Ground <= 3
    #       B.) Protection level - Ground > 3
    #   2.) Protection level >= Main floor
    @classmethod
    def __bi_levels_raised_ranches(cls, flood_level, main_floor, protection_level, ground, basement):
        if flood_greater_main(flood_level, main_floor):
            return treatment('Raise')
        elif not flood_greater_main(flood_level, main_floor):
            if not protection_greater_main(protection_level, main_floor):
                if (protection_level - ground) <= 3:
                    return treatment('Sealant and Closures')
                elif (protection_level - ground) > 3:
                    return treatment('Raise lower floor + space')
            elif protection_greater_main(protection_level, main_floor):
                return treatment('Raise')

    # Checks for 'Split Levels', follows the below path
    # I.) Flood level >= Main floor
    # II.) Flood level < Main floor
    #   1.) Protection level < Main floor
    #       A.) Protection - Ground < 3
    #       B.) Protection - Ground >= 3
    #   2.) Protection > Main floor
    @classmethod
    def __split_levels(cls, flood_level, main_floor, protection_level, ground, basement):
        if flood_greater_main(flood_level, main_floor):
            return treatment('Raise')
        elif not flood_greater_main(flood_level, main_floor):
            if not protection_greater_main(protection_level, main_floor):
                if not protection_ground_greater(protection_level, ground):
                    return treatment('Sealant and Closures')
                elif protection_ground_greater(protection_level, ground):
                    return treatment('Raise')
            elif protection_greater_main(protection_level, main_floor):
                return treatment('Raise')

    # Checks for 'Larger Residential'
    # This method uses many different data types
    # TODO To check for Larger Residential structures we require additional variables: structure_type, usage_code, size
    # Most of the cloest variables are NULL so we need to collect data (or redifne variables) for this data
    # At the moment the cloest to check on residential types is DwellingType_FromLocal (dwellingtype_fromlocal)
    @classmethod
    def __larger_residential(cls, flood_level, main_floor, protection_level, ground, basement, 
                        square_footage, usage_code):
        # TODO: For these purposes USAGE_CODE will be hardcoded to a value of 12
        usage_code = USAGE_CODES[12]
        
        
        if basement in [BASEMENT_CODES.get(key) for key in ['1S', '1W', '3']]:
            if usage_code in [USAGE_CODES.get(key) for key in list(range(13, 16))]: # 16 because end is exclusive
                return treatment('Ringwall')
            if usage_code == USAGE_CODES[12]:
                if square_footage <= MAX_SIZE:
                    return treatment('Raise')
                elif square_footage > MAX_SIZE:
                    return treatment('Ringwall')
        elif basement in [BASEMENT_CODES.get(key) for key in ['0', '2']]:
            if not protection_greater_main(protection_level, main_floor):
                return treatment('Protect Utilities')
            elif protection_greater_main(protection_level, main_floor):
                if usage_code in [USAGE_CODES.get(key) for key in list(range(13, 16))]: # 16 because end is exclusive
                    return treatment('Ringwall')
                if (usage_code == USAGE_CODES[12]) and (not protection_ground_greater(protection_level, ground)):                    
                    return treatment('Sealant and Closures')
                elif (usage_code == USAGE_CODES[12]) and ((protection_level - ground) > 3):
                    if square_footage > MAX_SIZE:
                        return treatment('Ringwall')
                    elif square_footage <= MAX_SIZE:
                        return treatment('Raise')
                        

    # This function runs the specific function for the type of basement
    # Based on the 'Basement' type it runs the required function
    @staticmethod
    def residential_algorithm(flood_level, main_floor, protection_level, ground, basement, square_footage):
        if square_footage <= MAX_SIZE:
            if basement == BASEMENT_TYPE['slab']:
                return ResidentialClass.__no_basement_slab(
                    flood_level, main_floor, protection_level, ground, basement)
            elif basement == BASEMENT_TYPE['subgrade']:
                return ResidentialClass.__subgrade_basement(
                    flood_level, main_floor, protection_level, basement)
            elif basement == BASEMENT_TYPE['raised']:
                return ResidentialClass.__raised_crawlspace(
                    flood_level, main_floor, protection_level, basement)
            elif basement == BASEMENT_TYPE['walkout']:
                return ResidentialClass.__walkout_basement(
                    flood_level, main_floor, protection_level, ground, basement)
            elif basement == BASEMENT_TYPE['ranches']:
                return ResidentialClass.__bi_levels_raised_ranches(
                    flood_level, main_floor, protection_level, ground, basement)
            elif basement == BASEMENT_TYPE['split']:
                return ResidentialClass.__split_levels(
                    flood_level, main_floor, protection_level, ground, basement)
        elif square_footage > MAX_SIZE and flood_level > ground:
                return ResidentialClass.__larger_residential(
                    # TODO: What to do about Usage Codes???
                    # TODO: Hardcoded at 12: 'Multi-Family'
                    flood_level, main_floor, protection_level, ground, basement, square_footage, usage_code=12)
        elif square_footage > MAX_SIZE and flood_level < ground:
            return treatment('Larger residential with Flood < Ground')
        # TODO: remove this portion
        elif basement == 'Unknown' or basement == 'Unkonwn' or basement == '':
            return 'Basement is Unknown'


class NonResidentialWood:
    # Checks for 'Crawlspace', follows the below path
    # I.) Flood level >= Main floor
    # II.) Flood level < Main floor
    #   1.) Protection level < Main floor
    #   2.) Protection level >= Main floor
    @classmethod
    def __raised_crawlspace(cls, flood_level, main_floor, protection_level, basement):
        if flood_greater_main(flood_level, main_floor):
            return treatment('Raise')
        elif not flood_greater_main(flood_level, main_floor):
            if not protection_greater_main(protection_level, main_floor):
                return treatment('Protect Utilities + Louvers')
            elif protection_greater_main(protection_level, main_floor):
                return treatment('Raise')
            
    # Checks for 'Slab' type basement, follows the below path
    # I.) Flood level >= Main floor
    #   1.) Protection level < Ground 
    #   2.) Protection level >= Ground
    # II.) Flood level < Main floor
    #   1.) Protection level < Main floor
    #   2.) Protection level >= Main floor
    #       A.) Protection level < Ground
    #       B.) Protection level >= Ground
    @classmethod
    def __slab(cls, flood_level, main_floor, protection_level, ground, basement):
        if flood_greater_main(flood_level, main_floor):
            if not protection_ground_greater(protection_level, ground):
                return treatment('Sealant and Closures')
            elif protection_ground_greater(protection_level, ground):
                return treatment('Raise')
        elif not flood_greater_main(flood_level, main_floor):
            if not protection_greater_main(protection_level, main_floor):
                return treatment('Protect Utilities')
            elif protection_greater_main(protection_level, main_floor):
                if not protection_ground_greater(protection_level, ground):
                    return treatment('Sealant and Closures')
                elif protection_ground_greater(protection_level, ground):
                    return treatment('Raise')
                
    # Checks for 'Subgrade Basement', follows the below path
    # I.) Flood level >= Main floor
    # II.) Flood level < Main floor
    #   1.) Protection level < Main floor
    #   2.) Protection >= Main floor
    @classmethod
    def __subgrade_basement(cls, flood_level, main_floor, protection_level, basement):
        if flood_greater_main(flood_level, main_floor):
            return treatment('Raise')
        elif not flood_greater_main(flood_level, main_floor):
            if not protection_greater_main(protection_level, main_floor):
                return treatment('Fill Basement + Utility Room')
            elif protection_greater_main(protection_level, main_floor):
                return treatment('Raise')
            
    # Checks for 'Walkout Basement', follows the below path
    # I.) Flood level >= Main floor
    # II.) Flood level < Main floor
    #   1.) Protection level < Main floor
    #       A.) Protection - Ground < 3
    #       B.) Protection - Ground >= 3
    #   2.) Protection level >= Main floor
    @classmethod
    def __walkout_basement(cls, flood_level, main_floor, protection_level, ground, basement):
        if flood_greater_main(flood_level, main_floor):
            return treatment('Raise')
        elif not flood_greater_main(flood_level, main_floor):
            if not protection_greater_main(protection_level, main_floor):
                if not protection_ground_greater(protection_level, ground):
                    return treatment('Interior Floodwall')
                elif protection_ground_greater(protection_level, ground):
                    return treatment('Raise Lower Floor + space')
            elif protection_greater_main(protection_level, main_floor):
                return treatment('Raise')
            
    # This function runs the specific function for the type of basement
    # Based on the 'Basement' type it runs the required function
    @staticmethod
    def nonresidential_wood_algorithm(flood_level, main_floor, protection_level, ground, basement, 
                                      square_footage):
        if square_footage <= MAX_SIZE:
            if basement == BASEMENT_TYPE['raised']:
                return NonResidentialWood.__raised_crawlspace(
                    flood_level, main_floor, protection_level, basement)
            elif basement == BASEMENT_TYPE['slab']:
                return NonResidentialWood.__slab(
                    flood_level, main_floor, protection_level, ground, basement)
            elif basement == BASEMENT_TYPE['subgrade']:
                return NonResidentialWood.__subgrade_basement(
                    flood_level, main_floor, protection_level, basement)
            elif basement == BASEMENT_TYPE['walkout']:
                return NonResidentialWood.__walkout_basement(
                    flood_level, main_floor, protection_level, ground, basement)
        elif square_footage > MAX_SIZE:
            return treatment('Ringwall')


class NonResidentialMasonry:
    
    @staticmethod
    def nonresidential_masonry_algorithm(flood_level, main_floor, protection_level, ground, basement,
                                         square_footage):
        # helper variables
        protection_minus_ground_greater_3 = (protection_level - ground) > 3
        protection_minus_main_greater_3 = (protection_level - main_floor) > 3

        if square_footage <= MAX_SIZE:            
            if flood_level >= main_floor:
                if basement in [BASEMENT_CODES.get(key) for key in ['1S', '1W', '3']]:
                    return treatment('Ringwall')
                elif basement in [BASEMENT_CODES.get(key) for key in ['0', '2']]:
                    if not protection_minus_ground_greater_3:
                        return treatment('Sealant and Closures')
                    elif protection_minus_ground_greater_3:
                        return treatment('Ringwall')
            elif flood_level < main_floor:
                if basement in [BASEMENT_CODES.get(key) for key in ['1S', '1W', '3']]:
                    return treatment('Ringwall')
                elif basement in [BASEMENT_CODES.get(key) for key in ['0', '2']]:
                    if not protection_greater_main(protection_level, main_floor):
                        return treatment('Protect Utilities')
                    elif protection_greater_main(protection_level, main_floor):
                        if not protection_minus_main_greater_3:
                            return treatment('Sealant and Closures')
                        elif protection_minus_main_greater_3:
                            return treatment('Ringwall')
        elif square_footage > MAX_SIZE:
            return treatment('Non-residential larger than 2000 square feet')

###############################################################################



###############################################################################

# Runs the actual logic of our algorithm
# Collects our parameters exists run the functions as needed
# Checks the parameters we are required actually exist
# If the parameters do not exist, return the missing variables to the database
##def check_measures(WaterElevation_10Year, numberofsteps, DesignWaterElevation, groundelev_2016_atpoint_ft, basement_type, PreliminaryEligibility):

def check_measures(damage_category,
                   building_construction_type,
                   square_footage,
                   flood_level,
                   number_of_steps,
                   protection_level,
                   ground,
                   basement_type):

    main_floor = main_floor_calculation(number_of_steps, ground, step_height=8)
    
    # Collect the variables, assign them to a dictionary for so they can be checked
    # Use of a dictionary is because ArcGIS does not allow collection of args
    # TODO: add 'structure' to the dictionary, currently structure_category are all 'Null' values
    params = {
                'damage_category': damage_category,
                'building_construction_type': building_construction_type,
                'square_footage': square_footage,
                'flood_level': flood_level,
                'main_floor': main_floor,
                'protection_level': protection_level,
                'ground': ground,
                'basement_type': basement_type}
    
    
    measures = {
                # 'damage_category': damage_category,
                # 'building_construction_type': building_construction_type,
                # 'basement_type': basement_type,
                
                'flood_level': flood_level,
                'main_floor': main_floor,
                'protection_level': protection_level,
                'ground': ground,
                'basement': basement_type,
                'square_footage': square_footage
                }
    
    # Check the Preliminary Eligibility
    preliminary_eligibility = 'Eligible'
    # We can ignore the Not Eligibile and Null values     
    if preliminary_eligibility == 'Not Eligible':
        return 'The structure is not Eligible for treatment'
    elif preliminary_eligibility == None:
        return 'The Preliminary Eligibility is Null'
    elif preliminary_eligibility == 'Eligible':
        # If all the measures exist in the database, run the algorithm
        # Need to check if the keys exist, and the values have a value
        # Because Python considers '0' a False need to check if the value is 0, need to check where None is not in Key also
        # Currently the code triple checks to ensure the variables are not None and contain 0

        # if all(measures.values()) or (not None in measures.values()) and (0 in measures.values()):
        if -1 not in params.values():
            if params['damage_category'] in DAMAGE_CATEGORY['RES']:
                    return ResidentialClass.residential_algorithm(**measures)
                    # TODO: Remove below code if above code works
                    # return NonResidentialWood.nonresidential_wood_algorithm(
                    #     flood_level=measures['flood level'],
                    #     main_floor=measures['main floor'],
                    #     protection_level=measures['protection level'],
                    #     ground=measures['ground'],
                    #     basement=measures['basement'],
                    #     square_footage=measures['square footage']
                    # )
            
            elif params['damage_category'] in DAMAGE_CATEGORY['COM'] and params['building_construction_type'] == WOOD_CONSTRUCTION:
                # TODO: the below line might be doubled and not needed
                # if params['square_footage'] <= MAX_SIZE:
                return NonResidentialWood.nonresidential_wood_algorithm(**measures)
                    # TODO: Remove below code if above code works
                    # return NonResidentialWood.nonresidential_wood_algorithm(
                    #     flood_level=measures['flood level'],
                    #     main_floor=measures['main floor'],
                    #     protection_level=measures['protection level'],
                    #     ground=measures['ground'],
                    #     basement=measures['basement'],
                    #     square_footage=measures['square footage']
                    # )

                # TODO: the below 2 lines might be doubled and not needed
                # elif params['square_footage'] > MAX_SIZE:
                #     return treatment('Ringwall')
            
            # uses the construction type of != WOOD_CONSTRUCTION
            elif params['damage_category'] in DAMAGE_CATEGORY['COM'] and params['building_construction_type'] != WOOD_CONSTRUCTION:
                return NonResidentialMasonry.nonresidential_masonry_algorithm(**measures)
                # TODO: Remove below code if above code works
                # return NonResidentialMasonry.nonresidential_masonry_algorithm(
                #     flood_level=measures['flood level'],
                #     main_floor=measures['main floor'],
                #     protection_level=measures['protection level'],
                #     ground=measures['ground'],
                #     basement=measures['basement']
                # )
        
        # elif np.isnan(measures):
        # If the measures are not there, return the missing measures
        elif -1 in params.values():
            missing = [key for key, value in params.items() if value == None or value == 'Unknown' or value == -1]
            return "Variable{} {} does not contain a value".format(
                    ("s" if len(missing) > 1 else ""), missing)


# TODO: implement the reading and writing of the files
class ProcessFiles:
    def __init__(self, folder_path, file_path):
        self.folder_path = folder_path
        self.file_path = file_path
        # split the file name at the '.' and return the name of the file
        # without the extenstion for later
        self.file_name_without_extenstion = self.file_path.split(".")[0]
        
        self.full_path = Path(self.folder_path, self.file_path)
        self.file_extension = self.full_path.suffix

        self.output_full_path = f'{self.file_name_without_extenstion}_output'
        
    def apply_algorithm(self, data_frame):
        # df['treatments'] = df.apply(lambda df: 
        #                             check(**columns), 
        #                             axis=1)


        data_frame['Treatment'] = data_frame.apply(
            # How we unpack the required variables
            # 1.) return the values() from the NONSTRUCTURAL_PARAMETERS dictionary
            # 2.) put the dictionary (from #1) into a list
            # 3.) take the list (from #2) and use those columns in the dataframe
            # 4.) unpack the dataframe (from #3) into the function
            # 5.) the keys in the dictionary must match the parameter names in the function
            
            # takes the NONSTRUCTURAL_PARAMETERS dictionary
##            lambda data_frame: 
##                check_measures(*data_frame[list(NONSTRUCTURAL_PARAMETERS.values())]),
##                axis=1)

            
            
            lambda data_frame:
                check_measures(
                    damage_category=data_frame[NONSTRUCTURAL_PARAMETERS['damage_category']],
                    building_construction_type=WOOD_CONSTRUCTION,
                    square_footage=data_frame[NONSTRUCTURAL_PARAMETERS['square_footage']],
                    flood_level=data_frame[NONSTRUCTURAL_PARAMETERS['flood_level']],
                    number_of_steps=data_frame[NONSTRUCTURAL_PARAMETERS['main_floor']],
                    protection_level=data_frame[NONSTRUCTURAL_PARAMETERS['protection_level']],
                    ground=data_frame[NONSTRUCTURAL_PARAMETERS['ground']],
                    basement_type=data_frame[NONSTRUCTURAL_PARAMETERS['basement']]
                ), axis=1)
        
    def read_modify_save_file(self):
        if self.file_extension == '.xlsx':
            print('Excel XLSX')
            input_df = pd.read_excel(self.full_path,  index_col=None, header=0)
            
            # replace empty values with a -1
            input_df.fillna(-1, inplace=True)

            self.apply_algorithm(input_df)
            input_df.to_excel(self.full_path.with_stem(self.output_full_path), index=False)
        elif self.file_extension == '.csv':
            print('Excel CSV')
            input_df = pd.read_csv(self.full_path)

            # replace empty values with a -1
            input_df.fillna(-1, inplace=True)

            self.apply_algorithm(input_df)
            input_df.to_csv(self.full_path.with_stem(self.output_full_path), index=False)


if __name__ == '__main__':
    print('Running the algorithm...')
    
    process_files = ProcessFiles(folder_path=USER_FOLDER_PATH,
                                 file_path=USER_FILE_NAME)
    process_files.read_modify_save_file()

    print(f'Completed. File saved at: {process_files.output_full_path}')





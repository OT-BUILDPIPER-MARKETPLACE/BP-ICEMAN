import yaml, logging

def _getProperty(property_file_path):  
    
    try: 
        load_property = open(property_file_path)
        parse_yaml = yaml.load(load_property, Loader=yaml.FullLoader)
        logging.info(f"Loaded conf file succesfully.")
        return parse_yaml
    except FileNotFoundError:
        logging.error(f"Unable to find conf file < {property_file_path} > Please mention correct property file path.")
        exit()

    return None
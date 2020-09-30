import json
from bs4 import BeautifulSoup
from .util import KeysForJsonDict as Key


def get_dict_from_scriptjson(response_text):
    """
    Create dictionary from json-script-data
    :param response_text: str
    :return dict or None
    """
    script_data = get_script_data_from_(response_text)
    try:
        app_script_text = str(script_data.contents[0].string.extract())
        app_text = clear_script_string(app_script_text)
    except Exception as e:
        print(e)
        return None
    else:
        try:
            return json.loads(app_text)
        except Exception as e:
            print(e)
            return None


def get_script_data_from_(response_text):
    """
    Create BeautifulSoup-object and find script-element
    :param response_text: str
    :return bs-element
    """
    bs_obj = BeautifulSoup(markup=response_text,
                           features='html.parser')
    body = bs_obj.find('body')
    return body.find(name='script',
                     attrs={'type': 'application/json',
                            'data-hypernova-key': True})


def clear_script_string(script_data: str):
   """
   Return script data from first scope to last scope
   :param script_data: str
   :return clean script_data
   """
   start_index = script_data.find('{')
   end_index = script_data.rfind('}')
   if start_index == -1 or end_index == -1:
      return None
   return script_data[start_index:end_index + 1]


def get_the_server_modules_list_in_(json_dict):
    """
    Find and return list with modules which are in ServerModules in json
    :param json_dict: dict
    :return done-marker and list with modules or list with key-path
    """
    try:
        return True, json_dict[Key.modules_1][Key.modules_2][Key.modules_3][Key.modules_4]
    except:
        return False, [Key.modules_1, Key.modules_2, Key.modules_3, Key.modules_4]


def find_component_for_(key_component, server_modules_list):
    """
    Method for find component in modules by component name
    :param key_component component name
    :param server_modules_list source for finding
    :return module-dict or none
    """
    for s_module in server_modules_list:
        try:
            if s_module[Key.component_key] == key_component:
                return s_module[Key.props]
        except:
            continue
    return None


def get_site(action_buttons):
    """
    Diving to site in dict-source
    :param action_buttons: dict
    :return str
    """
    try:
        return action_buttons[Key.url_step1][Key.url_step2]
    except:
        return ''


def get_address_telephone_image(json_dict):
    """Working with script where address, tel and image
    :param json_dict
    :return (dict, str,str)"""
    address = dict.fromkeys(['streetAddress', 'addressLocality', 'addressRegion', 'postalCode', 'addressCountry'], '')
    tel = ''
    image = ''
    try:
        scripts_list = json_dict[Key.address_step1][Key.address_step2][Key.address_step3]
    except:
        pass
    else:
        for script in scripts_list:
            script = str(script)
            if script.find('address') != -1 and script.find('telephone') != -1:
                ind1 = script.find('{')
                ind2 = script.find('}<')+1
                script_json = script[ind1: ind2]
                try:
                    script_dict = json.loads(script_json)
                except:
                    pass
                else:
                    try:
                        tel = script_dict['telephone']
                    except:
                        pass
                    try:
                        address.update(script_dict['address'])
                    except:
                        pass
                    try:
                        image = script_dict['image']
                    except:
                        pass
    finally:
        return address, tel, image


def get_email(json_dict):
    """
    Diving to email in dict-source
    :param json_dict: dict
    :return str
    """
    try:
        email = json_dict[Key.email_step1][Key.email_step2][Key.email_step3][Key.email_step4][Key.email_step5]
        return email if email else ''
    except:
        return ''


def get_bizid(json_dict):
    """
    Diving to id in dict-source
    :param json_dict: dict
    :return str
    """
    try:
        return json_dict[Key.bizid_step1][Key.bizid_step2][Key.bizid_step3]
    except:
        return ''


def get_amenities(json_dict):
    """
    Diving to amenities data in dict-source
    :param json_dict: dict
    :return list
    """
    result = []
    try:
        amenities_list = json_dict[Key.amenities_step1][Key.amenities_step2][Key.amenities_step3][Key.amenities_step4][
            Key.amenities_step5]
    except:
        return []
    for element in amenities_list:
        try:
            t: str = element[Key.title_amenities]
            l: str = element[Key.label_amenities]
            if l.lower() == 'yes':
                result.append(t)
            else:
                tl = t + ' - ' + l
                result.append(tl)
        except:
            continue
    return result


def get_hours(json_dict):
    """
    Diving to hours in dict-source
    :param json_dict: dict
    :return str
    """
    try:
        hours_list = json_dict[Key.hours_step1][Key.hours_step2][Key.hours_step3][Key.hours_step4][Key.hours_step5][
            0].values()
        return ', '.join(hours_list)
    except:
        return ''


def get_about_biz(json_dict):
    """
    Diving to data about biz in dict-source
    :param json_dict: dict
    :return str
    """
    try:
        about_biz_dict = json_dict[Key.aboutbiz_step1][Key.aboutbiz_step2][Key.aboutbiz_step3]
    except:
        return ''

    result_list = []
    keys = [Key.specialties_text, Key.year_established, Key.history_text, Key.bio_text, Key.owner_name, Key.owner_role]
    for key in keys:
        try:
            result_list.append(about_biz_dict[key])
        except:
            continue

    return '  '.join(list(filter(None,result_list)))


def get_url(url: str):
    """Replace url from mobile to desktop"""
    return url.replace('m.yelp', 'www.yelp')

import re
import numpy as np
from lib import schedule_parser_pre
from lib import schedule_parser_post

def transform_schedule(keywords, parameters, input_file, output_file, clean_file):
    """
    read the input .inc-file and transform it to .csv schedule
    your main function
    @param keywords: a tuple of keywords we are interested in (DATES, COMPDAT, COMPDATL, etc.)
    @param parameters: column names of output .csv file
    @param input_file: path to your source input .inc file
    @param output_file: path to your output .csv file
    @return:
    """
    input_text = schedule_parser_pre.read_schedule(input_file, 'r', "utf-8")
    if schedule_parser_pre.inspect_schedule(input_text):
        input_cleaned = schedule_parser_pre.clean_schedule(input_text)
        schedule = parse_schedule(input_cleaned, keywords)
        with open(clean_file, "w") as file:
            file.write(input_cleaned)
        result = schedule_parser_post.results_to_csv(schedule, output_file, parameters)
    else:
        print('input file is empty')

    return result


def parse_schedule(text, keywords_tuple):
    """
    return list of elements ready to be transformed to the resulting DataFrame
    @param text: cleaned input text from .inc file
    @param keywords_tuple: a tuple of keywords we are interested in (DATES, COMPDAT, COMPDATL, etc.)
    @return: list of elements [[DATA1, WELL1, PARAM1, PARAM2, ...], [DATA2, ...], ...] ready to be transformed
    to the resulting DataFrame
    """
    cur_date = np.nan
    main_list = []
    sign = False
    keyword_blocks = extract_keyword_blocks(text, keywords_tuple)
    for keyword_block in keyword_blocks:
        keyword, keyword_lines = extract_lines_from_keyword_block(keyword_block)
        cur_date, main_list, sign = parse_keyword_block(keyword, keyword_lines, cur_date, main_list, sign)
    keyword = 'END'
    cur_date, main_list, sign = parse_keyword_block(keyword, keyword_lines, cur_date, main_list, sign)

    return main_list



def extract_keyword_blocks(text, keywords_tuple):
    """
    return keywords text blocks ending with a newline "/"
    @param text: cleaned input text from .inc file
    @param keywords_tuple: a tuple of keywords we are interested in (DATES, COMPDAT, COMPDATL, etc.)
    @return: list keywords text blocks ending with a newline "/"
    """
    block = re.split('\n/\n', text)
    list_of_tuple = []
    for i in block:
        el_tuple = tuple(i.split('\n'))
        if el_tuple[0] in keywords_tuple:
            list_of_tuple.append(el_tuple)

    return list_of_tuple

def extract_lines_from_keyword_block(Tuple):
    """
    extract the main keyword and corresponding lines from a certain block from the input file
    @param block: a block of the input text related to the some keyword (DATA, COMPDAT, etc.)
    @return:
        - keyword - DATA, COMPDAT, etc.
        - lines - lines of the input text related to the current keyword
    """
    return Tuple[0], list(Tuple[1:])

def parse_keyword_block(keyword, keyword_lines, cur_date,
                        main_list, sign):
    """
    parse a block of the input text related to the current keyword (DATA, COMPDAT, etc.)
    @param keyword: DATA, COMPDAT, etc.
    @param keyword_lines: lines of the input text related to the current keyword
    @param current_date: the last parsed DATE. The first DATE is NaN if not specified
    @param schedule_list: list of elements [[DATA1, WELL1, PARAM1, PARAM2, ...], [DATA2, ...], ...]
    @param block_list: schedule_list but for the current keyword
    @return:
        - current_date - current DATE value which might be changed if keyword DATES appears
        - schedule_list - updated schedule_list
        - block_list - updated block_list
    """
    def parse_data(keyword_lines, main_list):
        for line in keyword_lines[:-1]:
            temp_data = parse_keyword_DATE_line(line)
            main_list.append([temp_data, np.nan])
        cur_date = parse_keyword_DATE_line(keyword_lines[-1])
        sign = True
        return main_list, cur_date, sign

    if keyword == "DATES" or keyword == "END":
        if sign:
            print(cur_date)
            main_list.append([cur_date, np.nan])
            main_list, cur_date, sign = parse_data(keyword_lines, main_list)
        else:
            main_list, cur_date, sign = parse_data(keyword_lines, main_list)


    elif keyword == "COMPDAT":
        sign = False
        for well_comp_line in keyword_lines:
            well_comp_data = parse_keyword_COMPDAT_line(well_comp_line)
            # insert current date into list with well completion data
            well_comp_data.insert(0, cur_date)
            main_list.append(well_comp_data)


    elif keyword == "COMPDATL":
        sign = False
        for well_comp_line in keyword_lines:
            well_comp_data = parse_keyword_COMPDATL_line(well_comp_line)
            # insert current date into list with well completion data
            well_comp_data.insert(0, cur_date)
            main_list.append(well_comp_data)

    return cur_date, main_list, sign

def parse_keyword_DATE_line(current_date_line):
    """
    parse a line related to a current DATA keyword block
    @param current_date_line: line related to a current DATA keyword block
    @return: list of parameters in a DATE line
    """
    data = re.search('\d{2}\s[A-Z]{3}\s\d{4}', current_date_line).group()
    return data

def parse_keyword_COMPDAT_line(well_comp_line):
    line = default_params_unpacking_in_line(well_comp_line)
    line = re.sub('\s+ ', ' ', line)
    line = re.sub(' /|\'', '', line)
    parameters = re.split('\s+',line)
    parameters.insert(1, np.nan)
    return parameters

def parse_keyword_COMPDATL_line(well_comp_line):
    line = default_params_unpacking_in_line(well_comp_line)
    line = re.sub('\s+ ', ' ', line)
    line = re.sub(' /|\'', '', line)
    parameters = re.split('\s+',line)
    return parameters

def default_params_unpacking_in_line(line):
    """
    unpack default parameters set by the 'n*' expression
    @param line: line related to a current COMPDAT/COMPDATL keyword block
    @return: the unpacked line related to a current COMPDAT/COMPDATL keyword block
    """
    # for i in range(len(line)):
    #     if line.find('*', i) == i:
    #         num = line[i - 1]
    #         default = ['DEFAULT'] * str(num)
    #         line = line.replace(str(num) + '*', ('DEFAULT' + ' ') * int(num))
    for i in range(len(line)):
        if line.find('*', i) == i:
            num = line[i - 1]
            s = ['DEFAULT'] * int(num)
            s1 = ' '.join(s)
            line = line.replace(str(num) + '*',s1)
    return line

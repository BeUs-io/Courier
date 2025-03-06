def zero_fill(
    data, attribute, target_range, fill_value=None,
    fill_attributes=()
):
    index = 0
    new_data = list()
    fill_dict = {attribute: fill_value for attribute in fill_attributes}
    for element in target_range:
        if index < len(data) and data[index][attribute] == element:
            new_data.append(data[index])
            index += 1
        else:
            fill_record = {attribute: element}
            fill_record.update(fill_dict)
            new_data.append(fill_record)
    return new_data

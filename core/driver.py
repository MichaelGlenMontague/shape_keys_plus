def refresh(driver):
    if driver:
        driver.expression += " "
        driver.expression = driver.expression[:-1]


def reconstruct_variables(driver, source):
    data = []
    
    for var in source:
        data.append({
            'name': var.name,
            'type': var.type,
            'targets': [{
                'id': target.id,
                'id_type': target.id_type,
                'data_path': target.data_path,
                'bone_target': target.bone_target,
                'transform_type': target.transform_type,
                'rotation_mode': target.rotation_mode,
                'transform_space': target.transform_space
            } for j, target in enumerate(var.targets)]
        })
    
    while driver.variables:
        driver.variables.remove(driver.variables[0])
    
    for i in range(len(source)):
        new_var = driver.variables.new()
        new_var.name = data[i]['name']
        
        # The type controls the targets, so this comes first.
        new_var.type = data[i]['type']
        
        for j, old_target in enumerate(data[i]['targets']):
            new_target = new_var.targets[j]
            
            # Only the "Single Property" type can have its id_type changed.
            if new_var.type == 'SINGLE_PROP':
                new_target.id_type = old_target['id_type']
            
            new_target.id = old_target['id']
            
            new_target.data_path = old_target['data_path']
            new_target.bone_target = old_target['bone_target']
            new_target.transform_type = old_target['transform_type']
            new_target.rotation_mode = old_target['rotation_mode']
            new_target.transform_space = old_target['transform_space']
    
    refresh(driver)

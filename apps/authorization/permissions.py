# Global permissions list
permission_list = {
        'admin': {'getEmployee', 'editEmployee', 'deleteEmployee', 'getEmployeeList', 'addEmployee'},
        'team lead': {'getEmployee'},
        'team member': {'getEmployee'},
    }

def get_permission_list():
    return permission_list





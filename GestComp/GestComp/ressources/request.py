#!/usr/bin/env python
# -*- coding: utf-8 -*-

def get_boolean_from_request(request, key, method='POST'):
    " gets the value from request and returns it's boolean state "
    value = getattr(request, method).get(key, False)
    
    if value == 'False' or value == 'false' or value == '0' or value == 0:
        value = False
    elif value: 
        value = True
    else:
        value = False
        
    return value    

is_true = lambda value: bool(value) and value.lower() not in ('false', '0')
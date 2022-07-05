#sets are mutable and items in no order
valid_inputs = {"yes", "y", "no", "n"} 
valid_inputs.add("y") 
valid_inputs

#lists are mutable
month_name_list = ["Jan", "Feb", "Mar", "Apr", 
    "May", "Jun", "Jul", "Aug", 
    "Sep", "Oct", "Nov", "Dec"] 
month_name_list[8] 
month_name_list.index("Feb") 

month_name_list[1:2] #feb
month_name_list[:2] #jan feb
month_name_list[10:] #nov dec
month_name_list.index("Jan") #0
month_name_list.index("jan") #error

#tuples are immutable
month_name_tuple = ("Jan", "Feb", "Mar", "Apr", 
    "May", "Jun", "Jul", "Aug", 
    "Sep", "Oct", "Nov", "Dec") 
month_name_tuple[1:2]
month_name_tuple[6]
month_name_tuple.index("Jan") #0
month_name_tuple.index("jan") #error

scheme = {"Crimson": (220, 14, 60), 
        "DarkCyan": (0, 139, 139), 
        "Yellow": (255, 255, 00)} 
scheme["Crimson"]

from collections import Counter
store = Counter(a=4, b=2, c=0, d=-2)
store["a"]
Counter('abracadabra').most_common()


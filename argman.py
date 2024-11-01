import sys

def find_string_index(search_string, string_list):
    try:
        index = string_list.index(search_string)
        return index
    except ValueError:
        return -1
    
class ArgOptMap:
    def __init__(self, _optname, _defvals):
        self.name = _optname
        self.defvals = _defvals

class ArgOption:

    def __init__(self, _name, _args):        
    #    self.opts = _defopts
        self.name = _name
        self.args = _args

#    def __str__(self):
 #       return print(self.args)

    def grub(self, array_of_items):
        i=0
    #    print(array_of_items)
        for _key in self.args:
            if(i<len(array_of_items)):
                self.args[_key] = array_of_items[i]
            i+=1
     
     


class ArgManager:

    def __init__(self, argv_arr, _def_opts):
        self.real_args = sys.argv[1:]
        self.def_opts = _def_opts
        opts = list(filter(lambda arg: arg[0:2]=="--", self.real_args ))
        self.args = {}
        for _opt_key in _def_opts:
            self.args[_opt_key] = ArgOption(_opt_key,_def_opts[_opt_key])

        onames = self.def_opts.keys()
        for opt in opts:
            #  if(self.def_opts)
            oname = opt[2:]
            if(oname in onames):
                opt_idx = self.real_args.index(opt)
                #newarg = ArgOption(oname)
                arr = []
                for i in range(opt_idx+1, len(self.real_args)):
                    curr_arg = self.real_args[i] 
                    if(curr_arg[0:2]=="--"): 
                        break
                    arr.append(curr_arg)
                self.args[oname].grub(arr)
                #self.args[oname] = newarg      
